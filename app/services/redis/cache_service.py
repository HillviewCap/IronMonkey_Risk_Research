"""
Redis caching service
"""
import json
from datetime import timedelta
from flask import current_app

class CacheService:
    """Service for caching data in Redis"""
    
    @staticmethod
    def get_client():
        """Get the Redis client from the application"""
        return current_app.redis
    
    @classmethod
    def get(cls, key):
        """
        Get a value from the cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        redis = cls.get_client()
        if redis is None:
            current_app.logger.warning("Redis is not configured")
            return None
        
        try:
            value = redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            current_app.logger.error(f"Error getting cache: {str(e)}")
            return None
    
    @classmethod
    def set(cls, key, value, expire=None):
        """
        Set a value in the cache
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            expire: Expiration time in seconds (optional)
            
        Returns:
            True if successful, False otherwise
        """
        redis = cls.get_client()
        if redis is None:
            current_app.logger.warning("Redis is not configured")
            return False
        
        try:
            serialized = json.dumps(value)
            if expire:
                return redis.setex(key, expire, serialized)
            return redis.set(key, serialized)
        except Exception as e:
            current_app.logger.error(f"Error setting cache: {str(e)}")
            return False
    
    @classmethod
    def delete(cls, key):
        """
        Delete a value from the cache
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        redis = cls.get_client()
        if redis is None:
            current_app.logger.warning("Redis is not configured")
            return False
        
        try:
            return redis.delete(key) > 0
        except Exception as e:
            current_app.logger.error(f"Error deleting cache: {str(e)}")
            return False
    
    @classmethod
    def clear_pattern(cls, pattern):
        """
        Delete all keys matching a pattern
        
        Args:
            pattern: Key pattern (e.g., "user:*")
            
        Returns:
            Number of keys deleted
        """
        redis = cls.get_client()
        if redis is None:
            current_app.logger.warning("Redis is not configured")
            return 0
        
        try:
            keys = redis.keys(pattern)
            if keys:
                return redis.delete(*keys)
            return 0
        except Exception as e:
            current_app.logger.error(f"Error clearing cache pattern: {str(e)}")
            return 0
