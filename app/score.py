from datetime import datetime, timezone

def score_items(items):
    def score(item):
        age_h = (datetime.utcnow().replace(tzinfo=timezone.utc) - datetime.fromtimestamp(float(item["published"]), tz=timezone.utc)).total_seconds()/3600
        age = max(1, age_h)
        buzz = 1/age  # simple recency weight
        return {**item, "viralScore": buzz}
    return sorted([score(i) for i in items], key=lambda x: x["viralScore"], reverse=True)

