from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import Callable

from redis.asyncio import ConnectionPool, Redis


class RedisDatabase:
    def __init__(self, url: str):
        self._conn_poll = ConnectionPool.from_url(url)

    @property
    def connection_pool(self):
        return self._conn_poll

    @asynccontextmanager
    async def client(self) -> Callable[..., AbstractAsyncContextManager[Redis]]:
        try:
            client = Redis(connection_pool=self._conn_poll)
            yield client
        finally:
            await client.close()
