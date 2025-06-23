import os, asyncio, aiohttp, redis.asyncio as redis
from functools import wraps

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.from_url(redis_url, decode_responses=True)

def async_retry(times:int=3, delay:float=2.0):
    def deco(fn):
        @wraps(fn)
        async def wrapper(*a, **k):
            for attempt in range(times):
                try:
                    return await fn(*a, **k)
                except Exception as e:
                    if attempt == times-1: raise
                    await asyncio.sleep(delay * (2**attempt))
        return wrapper
    return deco
