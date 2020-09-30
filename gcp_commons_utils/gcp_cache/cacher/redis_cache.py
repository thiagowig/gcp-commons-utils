"""Cache on Redis System."""
import logging
from datetime import datetime
from typing import Any

import redis

from .cache_interface import CacherInterface

LOGGER = logging.getLogger(__name__)


class RedisCacher(CacherInterface):
    """Cache Interface for GCP cache system."""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = None) -> None:
        self.host = host
        self.port = port
        self.db = db
        self.redis = self._get_redis_connection()

    def _get_redis_connection(self) -> redis.Redis:
        """."""
        LOGGER.debug(['RedisCacher', '_get_redis_connection:redishost', self.host])
        return redis.Redis(host=self.host, port=self.port)

    def get_cache(self, seed: str, cache_hash: str, seconds_expire: int) -> Any:
        """Get cache from redis."""
        LOGGER.debug(
            ['RedisCacher', 'get_cache::seed::cache_hast::time', seed, cache_hash, seconds_expire]
        )
        element = self.redis.hget(seed, cache_hash)
        creation_time = self.redis.hget(seed, cache_hash + "::time")
        creation_time = float(creation_time.decode()) if creation_time else None
        now_timestamp = datetime.now().timestamp()

        LOGGER.debug([
            'RedisCacher',
            'get_cache::creation_time::now_timestamp',
            seed,
            creation_time,
            now_timestamp
        ])

        if creation_time:
            if creation_time + seconds_expire > now_timestamp:
                LOGGER.debug(['RedisCacher', 'get_cache::got the cache', seed, cache_hash])
                return element
            else:
                LOGGER.debug(['RedisCacher', 'get_cache::removing old cache', seed, cache_hash])
                self.clear_cache(seed)
        LOGGER.debug(['RedisCacher', 'get_cache::unable to get cache', seed, cache_hash])
        return None

    def set_cache(self, seed: str, cache_hash: str, element: Any) -> bool:
        """Save the cache to redis."""
        now_timestamp = datetime.now().timestamp()
        LOGGER.debug(['redis_cache:set_cache', 'seed::key::time', seed, cache_hash, now_timestamp])

        # Set the cache on MAP of same seed in Redis
        self.redis.hset(seed, cache_hash, element)

        # Set the creation timestamp of cache, to be used as expiration period
        self.redis.hset(seed, cache_hash + "::time", now_timestamp)
        return True

    def clear_cache(self, seed: str, cache_hash: str = None) -> bool:
        """Remove the cache from redis, either all cache from same seed or specific one."""
        if cache_hash:
            LOGGER.debug(['redis_cache:clear_cache', 'seed::cache_hash', seed, cache_hash])
            self.redis.hdel(seed, cache_hash)
        else:
            LOGGER.debug(['redis_cache:clear_cache', 'seed', seed])
            self.redis.delete(seed)
        return True

    def clear_all_cache(self) -> bool:
        """Execute the flushdb command to the redis."""
        return self.redis.flushdb()
