# <app/scrape.py>
import aiohttp, asyncio, os, random
from .utils import async_retry

AI_KEY = os.getenv("AI_SEARCH_KEY")
AI_ENDPOINT = os.getenv("AI_SEARCH_ENDPOINT", "").rstrip("/")
AI_INDEX = os.getenv("AI_SEARCH_INDEX", "carismindex")
SERP_KEY = os.getenv("SERPAPI_KEY")
HEADERS = {"User-Agent": "CarismBot/1.0"}

# Marketing Intelligence trending topics
TRENDING_TOPICS = [
    "AI marketing automation",
    "predictive analytics marketing", 
    "customer data platforms CDP",
    "privacy-first marketing",
    "generative AI content marketing",
    "cookieless tracking solutions",
    "first-party data strategies",
    "marketing attribution models",
    "conversational AI chatbots",
    "real-time personalization",
    "TikTok marketing strategies",
    "Gen Z marketing trends",
    "sustainable marketing practices",
    "account-based marketing ABM",
    "marketing mix modeling MMM"
]

@async_retry()
async def fetch(session, url, params=None, headers=None):
    async with session.get(url, params=params, headers=headers or HEADERS, timeout=30) as r:
        r.raise_for_status()
        return await r.json()

async def gather_sources(topic=None):
    """Return unified list of trending content for a specific topic."""
    
    # Use provided topic or pick a random trending one
    if not topic:
        topic = random.choice(TRENDING_TOPICS)
    
    async with aiohttp.ClientSession() as session:
        # Search Reddit marketing subreddits
        reddit = fetch(
            session,
            "https://www.reddit.com/r/marketing/search.json",
            params={
                "q": topic,
                "t": "week",
                "limit": 25,
                "sort": "relevance",
                "restrict_sr": "true"
            },
        )

        # Search Azure AI Search with the topic
        ai_news = fetch(
            session,
            f"{AI_ENDPOINT}/indexes/{AI_INDEX}/docs",
            params={
                "api-version": "2023-11-01",
                "search": topic,
                "$searchFields": "title,description",
                "$top": 25
            },
            headers={
                **HEADERS,
                "api-key": AI_KEY,
            }
        )

        tasks = [reddit, ai_news]
        
        # Search Google News for the topic
        if SERP_KEY:
            serp = fetch(
                session,
                "https://serpapi.com/search.json",
                params={
                    "api_key": SERP_KEY,
                    "engine": "google_news",
                    "q": f"{topic} marketing trends"
                },
            )
            tasks.append(serp)

        raw = await asyncio.gather(*tasks, return_exceptions=True)

        # Process Reddit results
        reddit_items = []
        if isinstance(raw[0], dict) and "data" in raw[0]:
            reddit_items = [
                {
                    "source": "reddit",
                    "headline": p["data"]["title"],
                    "url": "https://reddit.com" + p["data"]["permalink"],
                    "published": p["data"]["created_utc"],
                    "score": p["data"]["score"],  # Reddit upvotes
                    "topic": topic
                }
                for p in raw[0]["data"]["children"]
                if p["data"]["score"] > 5  # Quality filter
            ]

        # Process AI Search results
        ai_items = []
        if isinstance(raw[1], dict) and "value" in raw[1]:
            ai_items = [
                {
                    "source": "ai-search",
                    "headline": a.get("title", "Untitled"),
                    "url": a.get("link", "#"),
                    "published": a.get("publishedAt", "2025-01-01T00:00:00Z"),
                    "topic": topic
                }
                for a in raw[1].get("value", [])
            ]

        # Process SERP results
        serp_items = []
        if SERP_KEY and len(raw) > 2 and isinstance(raw[2], dict):
            serp_items = [
                {
                    "source": "serpapi",
                    "headline": s["title"],
                    "url": s["link"],
                    "published": s.get("date"),
                    "snippet": s.get("snippet", ""),
                    "topic": topic
                }
                for s in raw[2].get("news_results", [])
            ]

        return {
            "topic_searched": topic,
            "items": reddit_items + ai_items + serp_items
        }
