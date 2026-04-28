import asyncio
import sys
import os

# Thêm đường dẫn để import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from app.db.session import AsyncSessionLocal
from app.langchain.rag_chain import hybrid_search
from app.core.redis_client import redis_client

async def test_updates():
    print("--- 1. Testing Redis Connection ---")
    try:
        await redis_client.ping()
        print("Redis is ALIVE")
    except Exception as e:
        print(f"Redis is DOWN: {e}")
        return

    print("\n--- 2. Testing Hybrid Search (Binary + Cache) ---")
    async with AsyncSessionLocal() as db:
        queries = ["Vé concert Anh Trai Say Hi", "Sự kiện âm nhạc"]
        
        print("First call (should be Cache MISS)...")
        results = await hybrid_search(db, queries, k=5)
        print(f"Results found: {len(results)}")
        
        print("\nChecking Redis keys...")
        for q in queries:
            exists = await redis_client.exists(f"emb:e5-base:{q}")
            print(f"Key for '{q}': {'EXISTS' if exists else 'MISSING'}")

        print("\nSecond call (should be Cache HIT)...")
        results2 = await hybrid_search(db, queries, k=5)
        print(f"Results found: {len(results2)}")

if __name__ == "__main__":
    asyncio.run(test_updates())
