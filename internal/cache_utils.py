from django.core.cache import cache
from django_redis import get_redis_connection
from functools import wraps
import hashlib
import logging

logger = logging.getLogger(__name__)


def generate_cache_key(*args, prefix="", **kwargs):
    """Generate a unique cache key based on args and kwargs"""
    # Sort kwargs to ensure consistent key generation
    sorted_kwargs = sorted(kwargs.items())

    # Convert all arguments to strings and join them
    key_parts = [str(arg) for arg in args] + [f"{k}:{v}" for k, v in sorted_kwargs]
    key_string = ":".join(key_parts)

    # Create an MD5 hash of the key string to ensure safe key length
    hash_object = hashlib.md5(key_string.encode())
    hashed_key = hash_object.hexdigest()

    return f"{prefix}:{hashed_key}" if prefix else hashed_key


def safe_cache_get(key):
    """Safely get data from cache with error handling"""
    try:
        return cache.get(key)
    except Exception as e:
        logger.error(f"Cache get error for key {key}: {str(e)}")
        return None


def safe_cache_set(key, value, timeout=None):
    """Safely set data in cache with error handling"""
    try:
        cache.set(key, value, timeout)
        return True
    except Exception as e:
        logger.error(f"Cache set error for key {key}: {str(e)}")
        return False


def cache_data(prefix, timeout=60 * 15):
    """
    Generic cache decorator that can be used for any function.

    Args:
        prefix (str): Prefix for the cache key (e.g., 'anime_data', 'streaming_data')
        timeout (int): Cache timeout in seconds
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key using all arguments
            cache_key = generate_cache_key(*args, prefix=prefix, **kwargs)

            # Try to get from cache
            cached_data = safe_cache_get(cache_key)
            if cached_data is not None:
                return cached_data

            try:
                # Get fresh data
                result = func(*args, **kwargs)
                # Cache the result
                safe_cache_set(cache_key, result, timeout)
                return result
            except Exception as e:
                logger.error(
                    f"Error in {prefix} for args {args}, kwargs {kwargs}: {str(e)}"
                )
                # On error, return fresh data without caching
                return func(*args, **kwargs)

        return wrapper

    return decorator


def clear_cache(pattern=None, prefix=None):
    """
    Clear cache entries based on a pattern or prefix.

    Args:
        pattern (str): Direct Redis key pattern to match (e.g., '*anime_id*')
        prefix (str): Cache prefix to clear (e.g., 'anime_data')
    """
    try:
        redis_conn = get_redis_connection("default")

        if not pattern and not prefix:
            # Clear all known prefixes if neither pattern nor prefix specified
            prefixes = ["anime_data:*", "streaming_data:*", "search_results:*"]
            total_cleared = 0
            for p in prefixes:
                keys = redis_conn.keys(p)
                if keys:
                    redis_conn.delete(*keys)
                    total_cleared += len(keys)
                    logger.info(f"Cleared {len(keys)} entries for pattern {p}")
            return total_cleared

        if prefix:
            pattern = f"{prefix}:*"

        keys = redis_conn.keys(pattern)
        if keys:
            redis_conn.delete(*keys)
            logger.info(f"Cleared {len(keys)} cache entries matching {pattern}")
            return len(keys)
        return 0

    except Exception as e:
        logger.error(f"Error clearing cache with pattern {pattern}: {str(e)}")
        return 0
