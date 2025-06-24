import aiohttp, asyncio, os
from .utils import async_retry

# ‑‑‑ Environment vars ‑‑‑
AI_KEY       = os.getenv("AI_SEARCH_KEY")          # Azure AI Search  admin key
AI_ENDPOINT  = os.getenv("AI_SEARCH_ENDPOINT", "").rstrip("/") # ensure trailing /
SERP_KEY     = os.getenv("SERPAPI_KEY")            # optional Google News
HEADERS      = {"User-Agent": "CarismBot/1.0"}

@async_retry()
async def fetch(session, url, params=None, headers=None):
    async with session.get(url, params=params, headers=headers or HEADERS, timeout=30) as r:
        r.raise_for_status()
        return await r.json()

async def gather_sources():
    """Return unified list of Reddit, Azure AI Search News, optional SerpAPI headlines."""
    async with aiohttp.ClientSession() as session:
        reddit = fetch(
            session,
            "https://www.reddit.com/r/marketing/top.json",
            params={"t": "day", "limit": 50},
        )

        ai_news = fetch(
            session,
            f"{AI_ENDPOINT}/news/search",
            params={"q": "marketing automation", "count": 50},
            headers={**HEADERS, "Ocp-Apim-Subscription-Key": AI_KEY},
        )

        tasks = [reddit, ai_news]
        if SERP_KEY:
            serp = fetch(
                session,
                "https://serpapi.com/search.json",
                params={"api_key": SERP_KEY, "engine": "google_news", "q": "marketing ROI"},
            )
            tasks.append(serp)

        raw = await asyncio.gather(*tasks)

        # flatten + unify ➜ create common dict structure per item
        reddit_items = [
            {
                "source": "reddit",
                "headline": p["data"]["title"],
                "url": "https://reddit.com" + p["data"]["permalink"],
                "published": p["data"]["created_utc"],
            }
            for p in raw[0]["data"]["children"]
        ]

        ai_items = [
            {
                "source": "ai-search",
                "headline": a["name"],
                "url": a["url"],
                "published": a["datePublished"],
            }
            for a in raw[1]["value"]
        ]

        serp_items = []
        if SERP_KEY:
            serp_items = [
                {
                    "source": "serpapi",
                    "headline": s["title"],
                    "url": s["link"],
                    "published": s.get("date"),
                }
                for s in raw[2].get("news_results", [])
            ]

        return reddit_items + ai_items + serp_items
