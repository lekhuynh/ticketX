from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
DATABASE_URL = settings.DATABASE_URL
import ssl
# Tạo SSL context cho asyncpg
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

engine = create_async_engine(
    DATABASE_URL,
    echo=False,              # True nếu muốn debug SQL
    pool_pre_ping=True, 
    connect_args={
        "prepared_statement_cache_size": 0,  # <--- DÒNG PHÉP THUẬT GIẢI QUYẾT LỖI
        "statement_cache_size": 0            # (Nên thêm cả dòng này cho chắc cú)
    }
)

AsyncSessionLocal = async_sessionmaker(
    bind = engine,
    class_ = AsyncSession,
    expire_on_commit=  False
)

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception :
            await session.rollback()
            raise 