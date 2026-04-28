from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from pgvector.asyncpg import register_vector

DATABASE_URL = settings.DATABASE_URL
import ssl

from sqlalchemy import event

# Tạo SSL context cho asyncpg
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

engine = create_async_engine(
    DATABASE_URL,
    echo=False,              # True nếu muốn debug SQL
    pool_pre_ping=True, 
    connect_args={
        "prepared_statement_cache_size": 0,
        "statement_cache_size": 0,
    }
)

# Đăng ký pgvector loại nhị phân (binary) cho mỗi kết nối mới
@event.listens_for(engine.sync_engine, "connect")
def register_pgvector(dbapi_connection, connection_record):
    dbapi_connection.run_async(register_vector)

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
            raise "quá mệt mõi"