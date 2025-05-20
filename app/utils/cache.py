import redis
import json
import os
from typing import Optional, Any
from .logger import logger

class RedisCache:
    def __init__(self):
        try:
            self.client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                db=int(os.getenv('REDIS_DB', 0)),
                decode_responses=True
            )
            self.client.ping()  # Test connection
        except redis.ConnectionError as e:
            logger.error(f"Redis connection failed: {e}")
            raise

    def get(self, key: str) -> Optional[Any]:
        try:
            value = self.client.get(key)
            return json.loads(value) if value else None
        except (json.JSONDecodeError, redis.RedisError) as e:
            logger.error(f"Cache get failed for key {key}: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        try:
            return bool(self.client.setex(key, ttl, json.dumps(value)))
        except (TypeError, redis.RedisError) as e:
            logger.error(f"Cache set failed for key {key}: {e}")
            return False