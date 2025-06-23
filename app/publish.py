import os, httpx
from .utils import async_retry
LI_TOKEN = os.getenv("LI_ACCESS_TOKEN")
FB_TOKEN = os.getenv("FB_PAGE_TOKEN")

@async_retry()
async def post_linkedin(payload):
    # payload = {text, imageUrl}
    headers = {"Authorization": f"Bearer {LI_TOKEN}", "Content-Type":"application/json"}
    ...
    return {"status":"ok"}

@async_retry()
async def post_facebook(payload):
    ...  # similar call
    return {"status":"ok"}
