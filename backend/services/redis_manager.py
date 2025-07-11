from dotenv import load_dotenv
load_dotenv(override=True)
import os
import logging
from typing import Optional

# Set up logging
logger = logging.getLogger(__name__)

class RedisManager:
    """Singleton Redis connection manager to avoid duplicate connections"""
    
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self._connect()
    
    def _connect(self):
        """Initialize Redis connection"""
        try:
            import redis
            
            # Get Redis configuration from environment variables or use defaults
            redis_host = os.getenv("REDIS_HOST", "localhost")
            redis_port = int(os.getenv("REDIS_PORT", 6379))
            redis_password = os.getenv("REDIS_PASSWORD", "your_secure_password")
            redis_db = int(os.getenv("REDIS_DB", 0))
            
            self._client = redis.Redis(
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
            self._client.ping()
            logger.info(f"Successfully connected to Redis at {redis_host}:{redis_port}")
            
        except ImportError:
            logger.error("Redis module not available")
            self._client = None
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._client = None
    
    @property
    def client(self) -> Optional:
        """Get the Redis client instance"""
        if self._client is None:
            self._connect()
        return self._client
    
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        if self._client is None:
            return False
        try:
            self._client.ping()
            return True
        except Exception:
            return False
    
    def reconnect(self):
        """Force reconnection to Redis"""
        self._client = None
        self._connect()
    
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


# Global instance for easy access
redis_manager = RedisManager()


def get_redis_client():
    """Convenience function to get Redis client"""
    return redis_manager.client


# Example usage and testing
if __name__ == "__main__":
    # Test the Redis manager
    print("Testing Redis Manager...")
    
    # Test connection
    client = get_redis_client()
    if client:
        print("✅ Redis connection successful")
        
        # Test basic operations
        try:
            client.set("test_key", "test_value")
            value = client.get("test_key")
            print(f"✅ Test operation successful: {value}")
            
            # Clean up
            client.delete("test_key")
            print("✅ Cleanup successful")
            
        except Exception as e:
            print(f"❌ Test operation failed: {e}")
    else:
        print("❌ Redis connection failed")
    
    # Test singleton pattern
    manager1 = RedisManager()
    manager2 = RedisManager()
    print(f"✅ Singleton test: {manager1 is manager2}")