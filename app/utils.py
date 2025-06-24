# <app/utils.py>
import time, functools
import openai
import os

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_KEY

async def embed_text(text: str) -> list:
    """Return OpenAI embedding for a given string."""
    response = await openai.Embedding.acreate(
        input=text,
        model="text-embedding-ada-002"
    )
    return response["data"][0]["embedding"]


def async_retry(retries=3, delay=1):
    def decorator(fn):
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return await fn(*args, **kwargs)
                except Exception as e:
                    if attempt == retries - 1:
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator
