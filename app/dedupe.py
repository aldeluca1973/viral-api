from langchain_openai import OpenAIEmbeddings
from .utils import redis_client
import numpy as np, json, hashlib, time, os

emb = OpenAIEmbeddings(model="text-embedding-3-small")
SIM_THRESHOLD = float(os.getenv("SIM_THRESHOLD", 0.85))
CACHE_TTL = 60*60*24  # 24 h

async def dedupe_headlines(items):
    out, vectors = [], []
    for item in items:
        h = item["headline"]
        cache_key = f"emb:{hashlib.md5(h.encode()).hexdigest()}"
        vec_json = await redis_client.get(cache_key)
        if vec_json:
            vec = json.loads(vec_json)
        else:
            vec = emb.embed_query(h)
            await redis_client.set(cache_key, json.dumps(vec), ex=CACHE_TTL)
        # cosine compare against collected vectors
        if not vectors or max(np.dot(vec, v)/(np.linalg.norm(vec)*np.linalg.norm(v)) for v in vectors) < SIM_THRESHOLD:
            vectors.append(vec)
            out.append(item)
    return out
