from fastapi import APIRouter, Header, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, Field
from typing import List
from fastapi.security import APIKeyHeader
from fastapi.openapi.models import APIKey
from fastapi.openapi.models import APIKey as OpenAPIKey
import os
from .scrape import gather_sources
from .dedupe import dedupe_headlines
from .score import score_items
from .generate import generate_copy
from .publish import post_linkedin, post_facebook
from fastapi import Security

router = APIRouter()

@router.get("/debug/key")
def debug_key():
    return {"loaded_internal_key": API_KEY}

APP_VERSION = "1.0.1"  # Increment this with each fix
API_KEY = os.getenv("INTERNAL_API_KEY", "dev")

# ⬇️ Define Swagger-compatible security schema
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

def verify_key(x_api_key: str = Depends(api_key_header)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Bad API Key")

@router.get("/version")  # No auth required for version check
def get_version():
    return {"version": APP_VERSION}

@router.get("/health")  # No auth required - for Render health checks
def health_check():
    return {"status": "healthy"}

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
