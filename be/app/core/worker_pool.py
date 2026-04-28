import asyncio
from typing import Any, Callable

class AsyncWorkerPool:
    def __init__(self, worker_num=5, max_queue_size=100):
        self.queue = asyncio.Queue(maxsize=max_queue_size)
        self.worker_num = worker_num
        self.workers = []
        self._started = False

    async def start(self):
        if self._started:
            return
        self._started = True
        for _ in range(self.worker_num):
            self.workers.append(asyncio.create_task(self.worker()))

    async def stop(self):
        for w in self.workers:
            w.cancel()
        self.workers = []
        self._started = False

    async def worker(self):
        while True:
            try:
                func, args, future = await self.queue.get()
                try:
                    result = await func(*args)
                    if not future.done():
                        future.set_result(result)
                except Exception as e:
                    if not future.done():
                        future.set_exception(e)
                finally:
                    self.queue.task_done()
            except asyncio.CancelledError:
                break

    async def submit(self, func: Callable, *args) -> Any:
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        try:
            # Drop/Fallback pattern when overload
            await asyncio.wait_for(self.queue.put((func, args, future)), timeout=0.1)
        except asyncio.TimeoutError:
            future.set_exception(Exception("AsyncWorkerPool Queue Overloaded (Timeout)"))
        return await future

# Khởi tạo Global Pool
embedding_pool = AsyncWorkerPool(worker_num=3, max_queue_size=50)
rerank_pool = AsyncWorkerPool(worker_num=2, max_queue_size=30)
