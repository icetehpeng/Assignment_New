"""
Redis Caching Manager for optimized data access
Handles caching of vital signs, medications, and other frequently accessed data
"""
import redis
import json
from datetime import datetime, timedelta
from typing import Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self, host='localhost', port=6379, db=0, ttl=3600):
        """Initialize Redis cache connection"""
        self.ttl = ttl
        try:
            self.redis_client = redis.Redis(
                host=host, port=port, db=db, 
                decode_responses=True, socket_connect_timeout=5
            )
            self.redis_client.ping()
            self.available = True
            logger.info("✅ Redis cache connected")
        except Exception as e:
            self.available = False
            logger.warning(f"⚠️ Redis unavailable: {e}. Using in-memory cache.")
            self.memory_cache = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if self.available:
                value = self.redis_client.get(key)
                if value:
                    logger.debug(f"Cache HIT: {key}")
                    return json.loads(value)
            else:
                if key in self.memory_cache:
                    logger.debug(f"Memory cache HIT: {key}")
                    return self.memory_cache[key]
        except Exception as e:
            logger.error(f"Cache GET error: {e}")
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with TTL"""
        try:
            ttl = ttl or self.ttl
            if self.available:
                self.redis_client.setex(key, ttl, json.dumps(value))
                logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
                return True
            else:
                self.memory_cache[key] = value
                logger.debug(f"Memory cache SET: {key}")
                return True
        except Exception as e:
            logger.error(f"Cache SET error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            if self.available:
                self.redis_client.delete(key)
            else:
                self.memory_cache.pop(key, None)
            logger.debug(f"Cache DELETE: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache DELETE error: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        try:
            if self.available:
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
                    logger.debug(f"Cache CLEAR: {len(keys)} keys matching {pattern}")
                    return len(keys)
            else:
                count = 0
                for key in list(self.memory_cache.keys()):
                    if pattern.replace('*', '') in key:
                        del self.memory_cache[key]
                        count += 1
                logger.debug(f"Memory cache CLEAR: {count} keys matching {pattern}")
                return count
        except Exception as e:
            logger.error(f"Cache CLEAR error: {e}")
        return 0
    
    def get_or_set(self, key: str, fetch_func, ttl: Optional[int] = None) -> Any:
        """Get from cache or fetch and cache"""
        cached = self.get(key)
        if cached is not None:
            return cached
        
        try:
            value = fetch_func()
            self.set(key, value, ttl)
            return value
        except Exception as e:
            logger.error(f"Cache GET_OR_SET error: {e}")
            return None
    
    def invalidate_user_cache(self, username: str):
        """Invalidate all cache for a user"""
        patterns = [
            f"vitals:{username}:*",
            f"meds:{username}:*",
            f"activity:{username}:*",
            f"nutrition:{username}:*",
            f"mood:{username}:*",
        ]
        total = 0
        for pattern in patterns:
            total += self.clear_pattern(pattern)
        logger.info(f"Invalidated {total} cache entries for {username}")
