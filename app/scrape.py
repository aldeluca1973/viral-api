# <app/scrape.py>
import aiohttp, asyncio, os
# from .utils import async_retry # Comment this out for now

AI_KEY = os.getenv("AI_SEARCH_KEY")
AI_ENDPOINT = os.getenv("AI_SEARCH_ENDPOINT")
AI_INDEX = os.getenv("AI_INDEX_NAME")
SERP_KEY = os.getenv("SERPAPI_KEY")
HEADERS = {"User-Agent": "CarismBot/1.0"}

# Marketing Intelligence trending topics
TRENDING_TOPICS = [
    "AI marketing automation 2025",
    "predictive analytics marketing",
    "customer data platforms CDP",
    "marketing attribution models",
    "conversational AI chatbots",
    "first-party data strategies",
    "privacy-first marketing",
    "marketing mix modeling MMM",
    "customer journey analytics",
    "intent data marketing",
    "account-based marketing ABM",
    "marketing ops MarTech stack",
    "generative AI content marketing",
    "real-time personalization",
    "cookieless tracking solutions"
]

#@async_retry
async def fetch(session, url, **kwargs):
    async with session.get(url, **kwargs) as response:
        response.raise_for_status()
        return await response.json()

async def gather_sources(topic=None):
    """Gather trending marketing intelligence content from multiple sources."""
    
    # Rotate through trending topics or use provided one
    if not topic:
        import random
        topic = random.choice(TRENDING_TOPICS)
    
    async with aiohttp.ClientSession() as session:
        # Reddit - search multiple marketing subreddits
        reddit_tasks = []
        subreddits = ["marketing", "digitalmarketing", "marketingautomation", "martech"]
        
        for subreddit in subreddits:
            reddit_tasks.append(fetch(
                session,
                f"https://www.reddit.com/r/{subreddit}/search.json",
                params={
                    "q": topic,
                    "t": "week",
                    "limit": 10,
                    "sort": "relevance",
                    "restrict_sr": "true"
                },
            ))
        
        # Azure AI Search - if you have marketing content indexed
        ai_news = fetch(
            session,
            f"{AI_ENDPOINT}/indexes/{AI_INDEX}/docs",
            params={
                "api-version": "2023-11-01",
                "search": topic,
                "$searchFields": "title,description",
                "$top": "25"
            },
            headers={
                **HEADERS,
                "api-key": AI_KEY,
            }
        )
        
        # Google News for latest marketing trends
        tasks = reddit_tasks + [ai_news]
        
        if SERP_KEY:
            serp = fetch(
                session,
                "https://serpapi.com/search.json",
                params={
                    "api_key": SERP_KEY,
                    "engine": "google_news",
                    "q": f"{topic} marketing trends",
                    "gl": "us",
                    "hl": "en"
                },
            )
            tasks.append(serp)
        
        raw = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process Reddit results from multiple subreddits
        reddit_items = []
        for i, result in enumerate(raw[:len(subreddits)]):
            if isinstance(result, dict) and "data" in result:
                items = [
                    {
                        "source": f"reddit-{subreddits[i]}",
                        "headline": p["data"]["title"],
                        "url": f"https://reddit.com{p['data']['permalink']}",
                        "published": p["data"]["created_utc"],
                        "score": p["data"]["score"],  # Reddit upvotes - good viral indicator!
                        "topic": topic
                    }
                    for p in result["data"]["children"]
                    if p["data"]["score"] > 5  # Filter low-quality posts
                ]
                reddit_items.extend(items)
        
        # Process AI Search results
        ai_items = []
        ai_result = raw[len(subreddits)]
        if isinstance(ai_result, dict) and "value" in ai_result:
            ai_items = [
                {
                    "source": "ai-search",
                    "headline": a.get("title", "Untitled"),
                    "url": a.get("link", "#"),
                    "published": a.get("publishedAt", "2025-01-01T00:00:00Z"),
                    "topic": topic
                }
                for a in ai_result.get("value", [])
            ]
        
        # Process SERP results
        serp_items = []
        if SERP_KEY and len(raw) > len(subreddits) + 1:
            serp_result = raw[-1]
            if isinstance(serp_result, dict) and "news_results" in serp_result:
                serp_items = [
                    {
                        "source": "google-news",
                        "headline": s["title"],
                        "url": s["link"],
                        "published": s.get("date"),
                        "snippet": s.get("snippet", ""),
                        "topic": topic
                    }
                    for s in serp_result.get("news_results", [])
                ]
        
        # Sort by relevance/recency
        all_items = reddit_items + ai_items + serp_items
        
        return {
            "topic_searched": topic,
            "total_results": len(all_items),
            "items": all_items
        }
