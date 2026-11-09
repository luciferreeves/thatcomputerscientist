import redis
import pickle

from django.conf import settings


class Cache:
    def __init__(self, redis_url=None):
        self.client = redis.Redis.from_url(redis_url or settings.REDIS_URL)

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
