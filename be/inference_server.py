import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sentence_transformers import CrossEncoder
from langchain_huggingface import HuggingFaceEmbeddings

app = FastAPI(title="TicketX Inference Service", version="1.0.0")

# Load model on startup to keep it warm in memory
print("Loading CrossEncoder model...")
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
print("Loading HuggingFace Embeddings model...")
embedding_model = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-base")
print("Models loaded successfully.")

class RerankRequest(BaseModel):
    query: str
    docs: List[str]

class RerankResponse(BaseModel):
    scores: List[float]

class EmbedRequest(BaseModel):
    text: str

class EmbedResponse(BaseModel):
    embedding: List[float]

@app.post("/v1/rerank", response_model=RerankResponse)
def rerank(req: RerankRequest):
    if not req.docs:
        return RerankResponse(scores=[])
        
    try:
        pairs = [[req.query, doc] for doc in req.docs]
        # Batch size 32 is more efficient on modern CPUs/GPUs
        scores = reranker.predict(pairs, batch_size=32)
        return RerankResponse(scores=[float(s) for s in scores])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class EmbedBatchRequest(BaseModel):
    texts: List[str]

class EmbedBatchResponse(BaseModel):
    embeddings: List[List[float]]

@app.post("/v1/embed", response_model=EmbedResponse)
def embed(req: EmbedRequest):
    try:
        # Use simple invoke to get vector. Adjust depending on Langchain behavior
        vector = embedding_model.embed_query(req.text)
        return EmbedResponse(embedding=vector)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/embed_batch", response_model=EmbedBatchResponse)
def embed_batch(req: EmbedBatchRequest):
    if not req.texts:
        return EmbedBatchResponse(embeddings=[])
    try:
        vectors = embedding_model.embed_documents(req.texts)
        return EmbedBatchResponse(embeddings=vectors)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
