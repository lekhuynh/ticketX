from typing import List, Dict, Optional
from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db, AsyncSessionLocal
from app.langchain.ingest_service import refresh_ai_docs_for_event
from app.langchain.rag_chain import ask
from app.core.security import get_optional_user, get_current_user
from app.db.models.user import User
from app.services.chat_history_service import ChatHistoryService
import json
import asyncio
import httpx
import os

AGENT_SVC_URL = os.getenv("AGENT_SVC_URL", "http://127.0.0.1:8002")

router = APIRouter()


# =========================
# REQUEST MODELS/ folder models
# =========================

class AskRequest(BaseModel):
    question: str
    history: Optional[List[Dict[str, str]]] = None # Legacy support or for guest manual history


class IngestEventRequest(BaseModel):
    event_id: UUID4

async def save_history_bg(user_id: UUID4, question: str, answer: str):
    """Save chat history in the background with its own session."""
    async with AsyncSessionLocal() as db_bg:
        history_service = ChatHistoryService(db_bg)
        await history_service.save_message(user_id, "human", question)
        await history_service.save_message(user_id, "assistant", answer)

@router.post("/ask")
async def ask_ai(
    payload: AskRequest, 
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    RAG Monolithic Gateway: Trực tiếp gọi hàm suy luận cục bộ từ cấu trúc RAG Chain
    """
    history_service = ChatHistoryService(db)
    chat_history = []

    if current_user:
        chat_history = await history_service.get_history(current_user.id)
    elif payload.history:
        chat_history = payload.history

    async def proxy_generator():
        yield "retry: 15000\n\n"
        full_answer = ""
        
        # Async Queue giới hạn maxsize để tạo Backpressure
        # Tránh việc LLM push quá nhanh chật RAM khi Client lấy chậm
        queue = asyncio.Queue(maxsize=15)
        
        async def producer():
            try:
                async for chunk in ask(db, payload.question, chat_history=chat_history):
                    if chunk:
                        await queue.put(chunk)
                await queue.put(None) # Sentinel end
            except Exception as e:
                import traceback
                traceback.print_exc()
                await queue.put(e)

        # Chạy Producer ngầm song song với Consumer
        producer_task = asyncio.create_task(producer())

        try:
            while True:
                item = await queue.get()
                
                if item is None:
                    break
                    
                if isinstance(item, Exception):
                    yield f"data: {json.dumps({'error': 'Lỗi suy luận nội bộ.', 'details': str(item)})}\n\n"
                    break
                    
                full_answer += item
                # Yield tốc độ phù hợp cho network client, nếu client chậm -> queue đầy -> producer bị block an toàn
                yield f"data: {json.dumps({'token': item})}\n\n"
            
            if current_user and full_answer:
                asyncio.create_task(save_history_bg(current_user.id, payload.question, full_answer))

            yield f"data: {json.dumps({'done': True})}\n\n"
            
        except asyncio.CancelledError:
            # Bắt event khi user ngắt kết nối trình duyệt đột ngột -> tắt producer task để dọn RAM
            producer_task.cancel()
            raise

    return StreamingResponse(
        proxy_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  
            "Content-Type": "text/event-stream",
        }
    )


# =========================
# (Removed old ask block backup)
# =========================


# =========================
# MANAGE HISTORY
# =========================

@router.get("/history")
async def get_chat_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all chat history for the logged-in user.
    """
    history_service = ChatHistoryService(db)
    history = await history_service.get_history(current_user.id)
    return history


@router.delete("/history", status_code=status.HTTP_204_NO_CONTENT)
async def clear_chat_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Clear all chat history for the logged-in user.
    """
    history_service = ChatHistoryService(db)
    await history_service.clear_history(current_user.id)
    return None


# =========================
# INGEST EVENT → BUILD VECTOR
# =========================
@router.post("/ingest/event")
async def ingest_event(payload: IngestEventRequest, db: AsyncSession = Depends(get_db)):
    await refresh_ai_docs_for_event(db, payload.event_id)

    return {
        "event_id": str(payload.event_id),
        "status": "vectorized"
    }