from typing import List
from config import settings
from redis.asyncio import ConnectionPool, Redis


class RedisClient:
    def __init__(
        self,
        url
    ) -> None:
        self.pool = ConnectionPool.from_url(url=url)
        self.client = Redis.from_pool(self.pool)

    async def messages_post(
        self,
        username,
        *args
    ) -> None:
        await self.client.rpush(username, *args)
        await self.client.ltrim(username, -10, -1)

    async def messages_get(
        self,
        username
    ) -> List[str]:
        result = await self.client.lrange(username, 0, -1)
        return result

    async def close(self) -> None:
        if self.client:
            await self.client.aclose()


redis_client = RedisClient(
    f'redis://:{settings.R_PASSWORD}@localhost:6379?decode_responses=True&protocol=3'
)
