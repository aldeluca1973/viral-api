# <app/dedupe.py>
import hashlib, json, os
import openai, redis.asyncio as redis
from .utils import embed_text, async_retry

openai.api_key = os.getenv("OPENAI_API_KEY")
rdb = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

@async_retry()
async def dedupe_headlines(items: list[dict]) -> list[dict]:
    seen = set()
    output = []

    for item in items:
        h = item["headline"]
        cache_key = f"emb:{hashlib.md5(h.encode()).hexdigest()}"

        # Fetch or create embedding
        cached = await rdb.get(cache_key)
        if cached:
            emb = json.loads(cached)
        else:
            emb = await embed_text(h)
            await rdb.set(cache_key, json.dumps(emb), ex=86400)

        # Compare with seen
        is_duplicate = False
        for other in seen:
            # simple dot product thresholding (e.g., cosine similarity)
            similarity = sum(a * b for a, b in zip(emb, other))
            if similarity > 0.94:
                is_duplicate = True
                break

        if not is_duplicate:
            seen.add(tuple(emb))
            output.append(item)

    return output
