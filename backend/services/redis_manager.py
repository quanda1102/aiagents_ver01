from dotenv import load_dotenv
load_dotenv(override=True)
import os
import logging
from typing import Optional

# Set up logging
logger = logging.getLogger(__name__)

class RedisManager:
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self._client = None

    async def initialize(self):
        if self._client is None:
            await self._connect()
    
    async def _connect(self):
        """Initialize Redis connection"""
        try:
            import redis.asyncio
            
            # Get Redis configuration from environment variables or use defaults
            redis_host = os.getenv("REDIS_HOST", "localhost")
            redis_port = int(os.getenv("REDIS_PORT", 6379))
            redis_password = os.getenv("REDIS_PASSWORD", "your_secure_password")
            redis_db = int(os.getenv("REDIS_DB", 0))
            
            self._client = redis.asyncio.Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password,
                db=redis_db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # Test the connection
            await self._client.ping()
            logger.info(f"Successfully connected to Redis at {redis_host}:{redis_port}")
            
        except ImportError:
            logger.error("Redis module not available")
            self._client = None
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._client = None
    
    @property
    async def client(self) -> Optional:
        """Get the Redis client instance"""
        if self._client is None:
            await self._connect()
        return self._client
    
    async def is_connected(self) -> bool:
        """Check if Redis is connected"""
        if self._client is None:
            return False
        try:
            await self._client.ping()
            return True
        except Exception:
            return False
    
    async def reconnect(self):
        """Force reconnection to Redis"""
        self._client = None
        await self._connect()
    
    def close(self):
        """Close Redis connection"""
        if self._client:
            try:
                self._client.close()
                logger.info("Redis connection closed")
            except Exception as e:
                logger.error(f"Error closing Redis connection: {e}")
            finally:
                self._client = None

    async def set_with_expiration(self, key: str, value: str, expiration_time: int):
        """Set a key-value pair with an expiration time (in seconds)."""
        if await self.client:
            try:
                client = await self.client
                await client.setex(key, expiration_time, value)
                logger.debug(f"Redis: Set key '{key}' with value '{value}' and expiration {expiration_time}s.")
            except Exception as e:
                logger.error(f"Redis: Error setting key '{key}': {e}")
        else:
            logger.warning("Redis client not available. Cannot set key with expiration.")

    async def get(self, key: str) -> Optional[str]:
        """Get the value associated with a key."""
        if await self.client:
            try:
                client = await self.client
                value = await client.get(key)
                logger.debug(f"Redis: Got key '{key}', value: '{value}'.")
                return value
            except Exception as e:
                logger.error(f"Redis: Error getting key '{key}': {e}")
                return None
        else:
            logger.warning("Redis client not available. Cannot get key.")
            return None

    async def delete(self, key: str):
        """Delete a key."""
        if await self.client:
            try:
                client = await self.client
                await client.delete(key)
                logger.debug(f"Redis: Deleted key '{key}'.")
            except Exception as e:
                logger.error(f"Redis: Error deleting key '{key}': {e}")
        else:
            logger.warning("Redis client not available. Cannot delete key.")


# Global instance for easy access
redis_manager = RedisManager()


def get_redis_client():
    """Convenience function to get Redis client"""
    return redis_manager.client

