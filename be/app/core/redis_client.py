import redis.asyncio as redis
from app.core.config import settings

# Khởi tạo Redis client
redis_client = redis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True  # Chúng ta sẽ decode thủ công nếu cần lưu binary, nhưng ở đây dùng JSON
)

async def get_redis():
    """Dependency cho FastAPI hoặc sử dụng trực tiếp"""
    return redis_client
