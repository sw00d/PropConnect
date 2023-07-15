from channels_redis.core import RedisChannelLayer
from django.conf import settings
from redis import asyncio as aioredis


class MaxConnectionRedisChannelLayer(RedisChannelLayer):
    def create_pool(self, index):
        """
        OVERRIDING THIS TO PASS MAX CONNECTIONS TO POOL!

        Takes the value of the "host" argument and returns a suited connection pool to
        the corresponding redis instance.
        """
        # avoid side-effects from modifying host
        host = self.hosts[index].copy()
        if "address" in host:
            address = host.pop("address")
            return aioredis.ConnectionPool.from_url(address, **host)

        master_name = host.pop("master_name", None)
        if master_name is not None:
            sentinels = host.pop("sentinels")
            sentinel_kwargs = host.pop("sentinel_kwargs", None)
            return aioredis.sentinel.SentinelConnectionPool(
                master_name,
                aioredis.sentinel.Sentinel(sentinels, sentinel_kwargs=sentinel_kwargs),
                **host
            )

        return aioredis.ConnectionPool(
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            **host
        )
