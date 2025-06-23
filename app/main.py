from fastapi import APIRouter, Header, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List
import os
from .scrape import gather_sources
from .dedupe import dedupe_headlines
from .score import score_items
from .generate import generate_copy
from .publish import post_linkedin, post_facebook

router = APIRouter()

API_KEY = os.getenv("INTERNAL_API_KEY", "dev")

def verify_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Bad API Key")

class TrendItem(BaseModel):
    source: str
    headline: str
    url: str
    published: str

class BreakthroughRequest(BaseModel):
    items: List[TrendItem]
    threshold: float = Field(0.7, ge=0, le=1)

class CopyRequest(BaseModel):
    headline: str
    tone: str = "curious"
    platform: str = "linkedin"

@router.get("/trends/scrape", dependencies=[Depends(verify_key)])
async def scrape():
    """Fetch raw headlines from Reddit, Bing News, LinkedIn Pulse."""
    return await gather_sources()

@router.post("/trends/breakthrough", dependencies=[Depends(verify_key)])
async def breakthrough(req: BreakthroughRequest):
    deduped = await dedupe_headlines(req.items)
    scored = score_items(deduped)
    return [x for x in scored if x["viralScore"] >= req.threshold]

@router.post("/content/generate", dependencies=[Depends(verify_key)])
async def gen(req: CopyRequest):
    return await generate_copy(req.headline, req.tone, req.platform)

@router.post("/publish/linkedin", dependencies=[Depends(verify_key)])
async def publish_li(payload: dict):
    return await post_linkedin(payload)

@router.post("/publish/facebook", dependencies=[Depends(verify_key)])
async def publish_fb(payload: dict):
    return await post_facebook(payload)
@router.get("/config", dependencies=[Depends(verify_key)])
def get_config():
    return {
        "LI_ACCESS_TOKEN": bool(os.getenv("LI_ACCESS_TOKEN")),
        "FB_PAGE_ID":    os.getenv("FB_PAGE_ID")
    }

