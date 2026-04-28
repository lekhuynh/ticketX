import asyncio
import re
from typing import List, Optional, Dict, Any, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, bindparam
from pgvector.sqlalchemy import Vector

from app.core.config import settings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from aiobreaker import CircuitBreaker
import base64
import zlib
import json
import hashlib
from app.core.redis_client import redis_client
from app.core.http_client import HttpClientManager
from app.core.worker_pool import embedding_pool, rerank_pool

anti_spike_semaphore = asyncio.Semaphore(10)

def compress_vec(vec: List[float]) -> str:
    return base64.b64encode(zlib.compress(json.dumps(vec).encode())).decode()

def decompress_vec(data: str) -> List[float]:
    return json.loads(zlib.decompress(base64.b64decode(data)))

# ==============================================================================
# 1. MICROSERVICES & MODELS
# ==============================================================================

# Circuit Breaker limits blast radius of microservice outages by endpoint/tenant isolating
embedding_breaker = CircuitBreaker(fail_max=5, reset_timeout=30, name="embedding_service")
reranking_breaker = CircuitBreaker(fail_max=5, reset_timeout=30, name="reranking_service")

@embedding_breaker
async def get_embedding_svc(text: str) -> List[float]:
    res = await HttpClientManager.get().post(
        "http://localhost:8001/v1/embed",
        json={"text": text},
        timeout=2.0
    )
    res.raise_for_status()
    return res.json()["embedding"]

@embedding_breaker
async def get_embedding_batch_svc(texts: List[str]) -> List[List[float]]:
    if not texts:
        return []
    res = await HttpClientManager.get().post(
        "http://localhost:8001/v1/embed_batch",
        json={"texts": texts},
        timeout=5.0
    )
    res.raise_for_status()
    return res.json()["embeddings"]

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=settings.GROQ_API_KEY,
    temperature=0.1,
    streaming=True
)

# Reranker extracted to inference_server microservice on port 8001

# ==============================================================================
# 2. QUERY EXPANSION
# ==============================================================================

async def generate_search_queries(question: str) -> List[str]:
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Bạn là chuyên gia tối ưu hóa tìm kiếm cho hệ thống bán vé TicketX."),
        ("human", """Tạo 1 search query định dạng từ khóa (keyword) ngắn gọn để tìm kiếm.
- Chỉ trả về đúng 1 query, không giải thích
- Tiếng Việt

Câu hỏi: {question}
""")
    ])

    chain = prompt | llm | StrOutputParser()
    try:
        res = await asyncio.wait_for(
            chain.ainvoke({"question": question}),
            timeout=3.0
        )
    except asyncio.TimeoutException:
        print("[LLM TIMEOUT] generate_search_queries")
        return [question]

    queries = [q.strip() for q in res.split("\n") if q.strip()]
    queries = [re.sub(r'^(\d+\.|\-|\*)\s*', '', q) for q in queries]

    if question not in queries:
        queries.insert(0, question)

    return queries[:2]  # Giới hạn tối đa 2 queries để giảm tải CPU

def normalize_query(q: str) -> str:
    """Chuẩn hóa query để cache key đạt tỉ lệ hit cao nhất"""
    return re.sub(r'\s+', ' ', q.lower().strip())


# ==============================================================================
# 3. HYBRID SEARCH (BATCH EMBEDDING)
# ==============================================================================

async def hybrid_search(
    db: AsyncSession,
    queries: List[str],
    k: int = 15,
    precomputed_embeddings: Optional[List[Optional[list[float]]]] = None,
    tenant_id: str = "T-999"
) -> List[Dict[str, Any]]:

    if not queries:
        return []

    # =========================
    # 1. REDIS CACHE EMBEDDING (MGET vs Timeout Guard)
    # =========================
    cache_prefix = f"emb:v2:{tenant_id}:e5-base:query:"
    norm_queries = [normalize_query(q) for q in queries]
    cached_vectors = {}

    # Chèn precomputed_embeddings để không bị gọi compute lại
    if precomputed_embeddings:
        for i, emb in enumerate(precomputed_embeddings):
            if emb is not None and i < len(norm_queries):
                cached_vectors[norm_queries[i]] = emb

    # Lọc ra các queries CÒN THIẾU chưa có trong cached_vectors
    missing_indices = [i for i, nq in enumerate(norm_queries) if nq not in cached_vectors]
    
    if missing_indices:
        missing_q = [queries[i] for i in missing_indices]
        missing_nq = [norm_queries[i] for i in missing_indices]
        cache_keys = [f"{cache_prefix}{hashlib.md5(nq.encode('utf-8')).hexdigest()}" for nq in missing_nq]
        
        still_missing_q = []
        still_missing_nq = []

        try:
            # 3. Redis mget có TimeOut Guard (0.5s)
            mget_results = await asyncio.wait_for(redis_client.mget(*cache_keys), timeout=0.5)
            for q, nq, cached_val in zip(missing_q, missing_nq, mget_results):
                if cached_val:
                    try:
                        cached_vectors[nq] = decompress_vec(cached_val)
                    except:
                        # Fallback for old uncompressed data format
                        cached_vectors[nq] = json.loads(cached_val)
                else:
                    still_missing_q.append(q)
                    still_missing_nq.append(nq)
        except Exception as e:
            print(f"[RAG WARNING] Redis MGET / Timeout error: {e}. Bypassing cache.")
            still_missing_q = missing_q
            still_missing_nq = missing_nq

        # Chỉ embed những query THỰC SỰ CÒN THIẾU (Cache Miss) bằng Microservice Batch GPU
        if still_missing_q:
            try:
                # Use batch API to save network roundtrips and avoid DDoS via Worker Pool
                new_vectors = await embedding_pool.submit(
                    get_embedding_batch_svc, 
                    [f"query: {nq}" for nq in still_missing_nq]
                )
            except Exception as e:
                print(f"[EMBED ERROR] Microservice batch failed: {e}")
                # Fallback to empty if embedding totally blocked
                new_vectors = [None] * len(still_missing_nq)
            
            try:
                # Pipelining kèm theo TimeOut Guard (1.0s) & ZLib Compression O(N) RAM fix
                pipe = redis_client.pipeline()
                for q, nq, vec in zip(still_missing_q, still_missing_nq, new_vectors):
                    if vec:
                        cached_vectors[nq] = vec
                        key = f"{cache_prefix}{hashlib.md5(nq.encode('utf-8')).hexdigest()}"
                        pipe.setex(key, 60 * 60 * 24 * 7, compress_vec(vec))
                if new_vectors and new_vectors[0]: # only execute if we got results
                    await asyncio.wait_for(pipe.execute(), timeout=1.0)
            except Exception as e:
                print(f"[RAG WARNING] Redis PIPELINE SET / error: {e}.")

    # Lấy vectors, Guard chống KeyError và hỗ trợ partial query
    vectors = []
    valid_queries = []
    for q in queries:
        nq = normalize_query(q)
        if nq in cached_vectors:
            valid_queries.append(q)
            vectors.append(cached_vectors[nq])
            
    queries = valid_queries
    if not queries:
        return []

    # =========================
    # PGVECTOR SEARCH (1 ROUND-TRIP BATCH)
    # =========================
    score_exprs = []
    bind_params = {"limit": k * 2} # Tăng limit để cover khi gom query
    type_binds = []

    for i in range(len(queries)):
        score_exprs.append(f"(0.7 * (1 - (embedding <=> :embedding_{i})) + 0.3 * ts_rank(tsv, plainto_tsquery('simple', :query_{i})))")
        bind_params[f"embedding_{i}"] = vectors[i]
        bind_params[f"query_{i}"] = queries[i]
        type_binds.append(bindparam(f"embedding_{i}", type_=Vector(768)))

    if len(queries) == 1:
        final_score_expr = score_exprs[0]
    else:
        # Dùng AVG (trung bình cộng) để lấy signal từ tất cả các query
        final_score_expr = f"({ ' + '.join(score_exprs) }) / {len(queries)}.0"

    sql = text(f"""
        SELECT 
            content,
            metadata,
            {final_score_expr} AS final_score
        FROM ai_docs
        WHERE is_active = true
        AND tenant_id = :tenant_id
        ORDER BY final_score DESC
        LIMIT :limit
    """).bindparams(*type_binds)
    
    bind_params["tenant_id"] = tenant_id

    try:
        result = await asyncio.wait_for(
            db.execute(sql, bind_params),
            timeout=2.0
        )
    except asyncio.TimeoutException:
        print("[RAG WARNING] DB Timeout during hybrid_search. Bypassing retrieved state.")
        return []

    all_docs = []
    seen = set()

    for row in result.fetchall():
        content, metadata, score = row
        if content not in seen:
            seen.add(content)
            all_docs.append({
                "content": content,
                "metadata": metadata,
                "score": score
            })

    return all_docs[:20]  # Tối đa 20 docs đưa vào Reranker để không bị hụt context


# ==============================================================================
# 4. RERANK
# ==============================================================================

async def apply_reranking(
    query: str,
    items: List[Dict[str, Any]],
    top_k: int = 5
) -> List[str]:

    if not items:
        return []

    docs = [item["content"] for item in items]
    
    # Guard circuit breaker state
    if reranking_breaker.current_state.name == "OPEN":
        print("[RERANK WARNING] Circuit Open! Fallback immediately.")
        return docs[:top_k]

    @reranking_breaker
    async def fetch_rerank(q: str, d: List[str]):
        res = await HttpClientManager.get().post(
            "http://localhost:8001/v1/rerank",
            json={"query": q, "docs": d},
            timeout=3.0
        )
        res.raise_for_status()
        return res.json()["scores"]

    scores = None
    for _ in range(2):
        try:
            scores = await rerank_pool.submit(fetch_rerank, query, docs)
            break
        except CircuitBreakerError:
            print("[RERANK WARNING] Circuit Opened during retry!")
            break
        except Exception as e:
            # Fallback queue overload or timeout
            print(f"[RERANK WARNING] Microservice error/Timeout: {e}. Retry...")
            await asyncio.sleep(0.2)
            
    if scores is None:
        print("[RERANK ERROR] Fallback to raw order. Microservice offline.")
        return docs[:top_k]

    ranked = sorted(
        zip(docs, scores),
        key=lambda x: x[1],
        reverse=True
    )

    if not ranked:
        return []

    top_score = ranked[0][1]

    if top_score < -2:
        return []

    threshold = top_score - 1.5
    filtered = [doc for doc, s in ranked if s >= threshold]

    return filtered[:top_k]


# ==============================================================================
# 5. FINAL RAG PIPELINE
# ==============================================================================

async def _ask_inner(
    db: AsyncSession,
    question: str,
    chat_history: Optional[List[Dict[str, str]]] = None,
    buffer_size: int = 40,
    tenant_id: str = "T-999"
) -> AsyncGenerator[str, None]:

    # =========================
    # KHI PHÁT HIỆN TRUY VẤN MỚI
    
    # 1. KIỂM TRA SEMANTIC CACHE (L1 / Intent-level Cache)
    try:
        q_emb = await get_embedding_svc(f"query: {normalize_query(question)}")
        
        cache_sql = text("""
            SELECT response
            FROM ai_semantic_cache
            WHERE tenant_id = :tenant_id
            AND created_at >= NOW() - INTERVAL '30 days'
            AND (1 - (embedding <=> :emb)) > 0.95
            ORDER BY (1 - (embedding <=> :emb)) DESC
            LIMIT 1
        """).bindparams(bindparam("emb", type_=Vector(768)))
        
        cache_hit = await db.execute(cache_sql, {"emb": q_emb, "tenant_id": tenant_id})
        cached_row = cache_hit.fetchone()
        
        if cached_row:
            # Semantic Cache Hit -> Skip LLM 100%
            yield cached_row[0]
            return
            
    except Exception as e:
        print(f"[SEMANTIC CACHE WARNING] DB error: {e}")
        q_emb = None

    # 2. Nếu Cache Miss, tiếp tục pipeline RAG thông thường
    if True:
        # 1. Thử nghiệm tìm kiếm nhanh với câu hỏi gốc (Early stop)
        # Truyền precomputed_embeddings để không tính lại embedding gốc
        original_retrieved = await hybrid_search(db, [question], k=5, precomputed_embeddings=[q_emb] if q_emb else None, tenant_id=tenant_id)
        
        # Optimize: Nếu tìm thấy docs và score khá tốt, bỏ qua gọi LLM mở rộng
        if original_retrieved and original_retrieved[0]["score"] > 0.8:
            retrieved = original_retrieved
        else:
            # 2. Điểm chưa đủ tốt -> generate mở rộng và gom 1 round-trip
            queries = await generate_search_queries(question)
            
            # Đảm bảo query gốc luôn có tiên phong và khử trùng lặp
            all_queries = list(dict.fromkeys([question] + queries))
            
            # Hybrid search gom chung (1 DB call). Gắn q_emb ở vị trí đầu tiên
            emb_list = [q_emb] + [None]*len(queries) if q_emb else None
            retrieved = await hybrid_search(db, all_queries, k=5, precomputed_embeddings=emb_list, tenant_id=tenant_id)

        # Reranker với batch_size cao hơn trên giới hạn an toàn
        retrieved = retrieved[:20]

        # Gọi Reranker qua Http (Microservice GPU)
        best_docs = await apply_reranking(question, retrieved)
        
        # Hallucination Guard
        if not best_docs or len(best_docs) < 1:
            yield "Dạ em xin lỗi, em chưa có thông tin chính xác để trả lời câu này."
            return

        # Pre-join string for final context format to save processing logic
        context = "\n\n---\n\n".join(best_docs)

        # Truncate window chống tràn token LLM thông minh
        MAX_CONTEXT_LEN = 3000
        
        def safe_truncate(text_context: str, max_len: int) -> str:
            if len(text_context) <= max_len:
                return text_context
            return text_context[:max_len].rsplit("\n", 1)[0]

        context = safe_truncate(context, MAX_CONTEXT_LEN)

    system_prompt = """Bạn là trợ lý AI của TicketX.

- Chỉ trả lời dựa trên CONTEXT
- Không bịa (No hallucination)
- Nếu không có → từ chối

CONTEXT:
{context}
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}")
    ])

    history_messages = []
    if chat_history:
        for msg in chat_history:
            if msg["role"] in ("human", "user"):
                history_messages.append(HumanMessage(content=msg["content"]))
            else:
                history_messages.append(AIMessage(content=msg["content"]))

    chain = prompt | llm | StrOutputParser()

    buffer = ""
    full_response = ""

    try:
        iterator = chain.astream({
            "context": context,
            "question": question,
            "chat_history": history_messages
        })
        while True:
            try:
                chunk = await asyncio.wait_for(iterator.__anext__(), timeout=5.0)
            except StopAsyncIteration:
                break
            except asyncio.TimeoutException:
                print("[STREAM TIMEOUT] LLM slow response")
                if not buffer and not full_response:
                    yield "Hệ thống AI đang quá tải cục bộ, xin bạn đợi giây lát và thử lại."
                break

            buffer += chunk
            full_response += chunk

            if chunk.endswith((" ", ".", "\n", "!", "?")):
                yield buffer
                buffer = ""

        if buffer:
            yield buffer
    except Exception as e:
        print(f"[STREAMING ERROR] Fallback fallback fallback... {e}")
        yield "Đường truyền bị đứt đoạn, mong bạn thông cảm và thử lại."
        return

    # UPSERT SEMANTIC CACHE L1 SAAS
    if q_emb and full_response.strip() and "chưa có thông tin" not in full_response and "Đường truyền" not in full_response:
        from sqlalchemy.dialects.postgresql import insert
        
        stmt = insert(text("ai_semantic_cache")).values(
            tenant_id=tenant_id,
            query_text=question,
            embedding=q_emb,
            response=full_response
        )
        # Bắt Dedup bằng ON CONFLICT:
        upsert_stmt = stmt.on_conflict_do_update(
            constraint="uq_tenant_query",
            set_={"response": stmt.excluded.response}
        )
        
        try:
            await db.execute(upsert_stmt)
            await db.commit()
        except Exception as e:
            print(f"[SEMANTIC CACHE SAVE ERROR] {e}")


async def ask(
    db: AsyncSession,
    question: str,
    chat_history: Optional[List[Dict[str, str]]] = None,
    buffer_size: int = 40,
    tenant_id: str = "T-999"
) -> AsyncGenerator[str, None]:
    """Wrapper an toàn bọc Semaphore giới hạn Rate Limit cực đoan."""
    try:
        # Prevent queue overload
        await asyncio.wait_for(anti_spike_semaphore.acquire(), timeout=5.0)
    except asyncio.TimeoutException:
        yield "Hệ thống đang phục vụ quá nhiều người cùng lúc, mong bạn thông cảm thử lại sau giây lát."
        return
        
    try:
        async for chunk in _ask_inner(db, question, chat_history, buffer_size, tenant_id):
            yield chunk
    finally:
        anti_spike_semaphore.release()