import httpx
from typing import Optional

class HttpClientManager:
    client: Optional[httpx.AsyncClient] = None

    @classmethod
    def start(cls):
        if cls.client is None or cls.client.is_closed:
            cls.client = httpx.AsyncClient(timeout=2.0)

    @classmethod
    async def stop(cls):
        if cls.client:
            await cls.client.aclose()
            cls.client = None

    @classmethod
    def get(cls) -> httpx.AsyncClient:
        if cls.client is None or cls.client.is_closed:
            cls.start()
        return cls.client
