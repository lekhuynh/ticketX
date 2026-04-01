# import asyncio
# import asyncpg
# from app.core.config import settings

# async def test_direct_connection():
#     """Test kết nối trực tiếp bằng asyncpg (không qua SQLAlchemy)"""
    
#     print("1. Testing direct asyncpg connection...")
#     try:
#         # asyncpg tự động dùng SSL với Supabase
#         conn = await asyncpg.connect(
#             user=settings.user,
#             password=settings.password,
#             host=settings.host,
#             port=settings.port,
#             database=settings.dbname,
#             ssl=True  # Bật SSL
#         )
        
#         version = await conn.fetchval("SELECT version()")
#         print(f"✅ Direct connection successful!")
#         print(f"   PostgreSQL version: {version[:50]}...")
        
#         await conn.close()
#         return True
#     except Exception as e:
#         print(f"❌ Direct connection failed: {e}")
#         return False

# async def test_sqlalchemy_connection():
#     """Test kết nối qua SQLAlchemy"""
#     from sqlalchemy.ext.asyncio import create_async_engine
#     from sqlalchemy import text
    
#     print("\n2. Testing SQLAlchemy connection...")
#     try:
#         engine = create_async_engine(
#             settings.DATABASE_URL,
#             echo=False
#         )
        
#         async with engine.connect() as conn:
#             result = await conn.execute(text("SELECT 1"))
#             print(f"✅ SQLAlchemy successful: {result.scalar()}")
        
#         await engine.dispose()
#         return True
#     except Exception as e:
#         print(f"❌ SQLAlchemy failed: {e}")
#         return False

# async def main():
#     print(f"Database config:")
#     print(f"  Host: {settings.host}")
#     print(f"  Port: {settings.port}")
#     print(f"  User: {settings.user}")
#     print(f"  Database: {settings.dbname}")
#     print(f"  URL: {settings.DATABASE_URL}\n")
    
#     await test_direct_connection()
#     await test_sqlalchemy_connection()

# if __name__ == "__main__":
#     asyncio.run(main())

import asyncio
from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = settings.DATABASE_URL

async def test():
    engine = create_async_engine(DATABASE_URL)
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        print(result.scalar())

asyncio.run(test())