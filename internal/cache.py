import redis
import pickle
import os

REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"


class Cache:
    def __init__(self, redis_url=REDIS_URL):
        self.client = redis.Redis.from_url(redis_url)

    def set(self, key, value, ex=None):
        pickled = pickle.dumps(value)
        self.client.set(key, pickled, ex=ex)

    def get(self, key):
        data = self.client.get(key)
        if isinstance(data, (bytes, bytearray, memoryview)):
            return pickle.loads(data)
        return None

    def delete(self, key):
        self.client.delete(key)

    def ttl(self, key) -> int:
        remaining = self.client.ttl(key)
        return remaining if isinstance(remaining, int) else -2

    def expire(self, key, seconds):
        self.client.expire(key, seconds)


cache = Cache()
