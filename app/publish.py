import os
import httpx
from .utils import async_retry

LI_TOKEN   = os.getenv("LI_ACCESS_TOKEN")
FB_TOKEN   = os.getenv("FB_PAGE_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")

@async_retry()
async def post_linkedin(payload: dict) -> dict:
    """
    Publish a post to LinkedIn using the UGC API.
    payload: { text: str, imageUrl?: str }
    Returns: { status: "ok", id: "urn:li:ugcPost:..." }
    """
    # Use projection to request profile fields (mandatory in v2)
    me_url   = "https://api.linkedin.com/v2/me?projection=(id)"
    post_url = "https://api.linkedin.com/v2/ugcPosts"
    headers  = {
        "Authorization": f"Bearer {LI_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    async with httpx.AsyncClient() as client:
        # 1. Fetch profile URN
        profile_resp = await client.get(me_url, headers=headers)
        profile_resp.raise_for_status()
        me = profile_resp.json()
        author_urn = f"urn:li:person:{me['id']}"

        # 2. Build the post body
        body = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": payload.get("text")},
                    "shareMediaCategory": "NONE",
                }
            }
        }
        # 3. Attach image if provided
        if payload.get("imageUrl"):
            share = body["specificContent"]["com.linkedin.ugc.ShareContent"]
            share["shareMediaCategory"] = "IMAGE"
            share["media"] = [{
                "status": "READY",
                "description": {"text": payload.get("text")},
                "media": payload.get("imageUrl"),
                "title": {"text": ""},
            }]

        # 4. Send POST to LinkedIn
        post_resp = await client.post(post_url, headers=headers, json=body)
        post_resp.raise_for_status()
        data = post_resp.json()
        return {"status": "ok", "id": data.get("id")}  

@async_retry()
async def post_facebook(payload: dict) -> dict:
    """
    Publish a post to a Facebook Page.
    payload: { text: str, link?: str }
    Returns: { status: "ok", id: "<pageID>_<postID>" }
    """
    post_url = f"https://graph.facebook.com/v14.0/{FB_PAGE_ID}/feed"
    params = {"access_token": FB_TOKEN, "message": payload.get("text")}
    if payload.get("link"):
        params["link"] = payload.get("link")

    async with httpx.AsyncClient() as client:
        fb_resp = await client.post(post_url, params=params)
        fb_resp.raise_for_status()
        data = fb_resp.json()
        return {"status": "ok", "id": data.get("id")}  
