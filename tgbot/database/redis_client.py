from typing import List

from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
from config import settings
from redis.asyncio import ConnectionPool, Redis


class RedisClientGPT:
    """
    Первая redis база
    для хранения последних диалогов пользователей с нейросетью
    """

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


# url для первой базы
REDIS_URL_0 = f'redis://:{settings.R_PASSWORD}@localhost:6379/0?decode_responses=True&protocol=3'
# url для второй базы
REDIS_URL_1 = f'redis://:{settings.R_PASSWORD}@localhost:6379/1?decode_responses=True&protocol=3'

# Экземпляр первой базы для gpt
redis_client_gpt = RedisClientGPT(REDIS_URL_0)

# Экземпляр второй базы для сессий
redis_fsm_storage = RedisStorage.from_url(
    url=REDIS_URL_1,
    key_builder=DefaultKeyBuilder(
        with_bot_id=True,
        with_destiny=True
    )
)
