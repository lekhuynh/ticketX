from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import router
from app.core.config import settings

app = FastAPI(
    title="TicketX API",
    version="1.0.0",
    description="Ticket booking system API"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api")

from app.core.http_client import HttpClientManager
from app.core.worker_pool import embedding_pool, rerank_pool

@app.on_event("startup")
async def startup():
    HttpClientManager.start()
    await embedding_pool.start()
    await rerank_pool.start()

@app.on_event("shutdown")
async def shutdown():
    await embedding_pool.stop()
    await rerank_pool.stop()
    await HttpClientManager.stop()

@app.get("/")
async def root():
    return {"message": "Welcome to TicketX API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}