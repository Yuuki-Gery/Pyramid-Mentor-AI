import redis

from app.core.config import settings


class RedisClient:
    def __init__(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=10,
            health_check_interval=15,
        )

    def set(self, key: str, value: str, expire: int = 3600):
        return self.client.set(key, value, ex=expire)

    def get(self, key: str):
        return self.client.get(key)

    def ping(self) -> bool:
        return bool(self.client.ping())


redis_client = RedisClient()
