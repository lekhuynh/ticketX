import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings

async def check():
    # Use prepared_statement_cache_size=0 for Supabase Pooler compatibility
    engine = create_async_engine(
        settings.DATABASE_URL,
        connect_args={"prepared_statement_cache_size": 0}
    )
    async with engine.connect() as conn:
        try:
            res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'events'"))
            cols = [r[0] for r in res.all()]
            print("Table events columns:", cols)
            
            ver = await conn.execute(text('SELECT version_num FROM alembic_version'))
            print("Alembic Version:", ver.scalar())
        except Exception as e:
            print("Error:", e)
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check())
