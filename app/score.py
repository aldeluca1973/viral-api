# <app/score.py>
from datetime import datetime, timezone
import re

def score_items(items):
    """Score items based on multiple viral indicators"""
    scored_items = []
    
    # Viral indicator keywords with their score boosts
    viral_indicators = {
        # AI/Tech trends
        "ai": 0.15, "chatgpt": 0.2, "gpt": 0.15, "llm": 0.15,
        "automation": 0.1, "machine learning": 0.15,
        
        # Marketing trends
        "roi": 0.1, "conversion": 0.1, "engagement": 0.1,
        "personalization": 0.12, "customer data": 0.12,
        
        # Hot topics
        "privacy": 0.15, "cookieless": 0.15, "first-party data": 0.15,
        "tiktok": 0.12, "gen z": 0.12, "sustainability": 0.1,
        
        # Urgency/Trending
        "breaking": 0.15, "just announced": 0.15, "new study": 0.12,
        "2025": 0.1, "trends": 0.1, "future": 0.08
    }
    
    for item in items:
        score = 0.5  # Base score
        headline_lower = item["headline"].lower()
        
        # Check for viral indicators
        for indicator, boost in viral_indicators.items():
            if indicator in headline_lower:
                score += boost
        
        # Boost for Reddit upvotes
        reddit_score = item.get("score", 0)
        if reddit_score > 1000:
            score += 0.25
        elif reddit_score > 500:
            score += 0.2
        elif reddit_score > 100:
            score += 0.15
        elif reddit_score > 50:
            score += 0.1
        
        # Boost for recent content
        published = item.get("published", "")
        if isinstance(published, (int, float)):
            # Unix timestamp
            pub_date = datetime.fromtimestamp(published, tz=timezone.utc)
            hours_old = (datetime.now(timezone.utc) - pub_date).total_seconds() / 3600
            
            if hours_old < 24:
                score += 0.2
            elif hours_old < 72:
                score += 0.1
        
        # Check headline quality
        if len(headline_lower.split()) > 5:  # Not too short
            score += 0.05
        
        if "?" in item["headline"]:  # Questions often get engagement
            score += 0.05
        
        # Cap at 1.0
        item["viralScore"] = min(score, 1.0)
        scored_items.append(item)
    
    # Sort by viral score
    return sorted(scored_items, key=lambda x: x["viralScore"], reverse=True)
