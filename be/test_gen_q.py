import asyncio
from app.langchain.rag_chain import generate_queries

async def test():
    q = await generate_queries("có sự kiện đà nẵng không")
    print(q)

if __name__ == "__main__":
    asyncio.run(test())
