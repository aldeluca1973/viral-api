# <README.md>
# Carism USA - Viral-Automation API v0.1.0

A service to track trending marketing headlines, deduplicate & score them, generate AI-powered social media content, and publish to LinkedIn & Facebook.

## Features
- **Fetch** top headlines from Reddit, Azure AI Search, and SerpAPI
- **Deduplicate** semantically with embeddings & Redis caching
- **Score** items by recency (viralScore)
- **Generate** personalized copy & image prompts via GPT/Claude
- **Publish** content to LinkedIn and Facebook pages

## 🔧 Getting Started

### Local development
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in your environment variables
uvicorn app:app --reload
```

## OAuth 2.0 Setup for LinkedIn
1. In LinkedIn Developer **Products**, ensure **Share on LinkedIn** and **Sign In with LinkedIn (OIDC)** are added.
2. In the **Auth** tab, under **Authorized redirect URLs**, add:
   ```
   http://localhost:8000/linkedin/oauth
   ```
3. In **OAuth 2.0 scopes**, confirm you see:
   - openid
   - profile
   - email
   - w_member_social

## Endpoints
| Method | Path                   | Description                              |
|-------:|------------------------|------------------------------------------|
| GET    | /version               | Return API version                       |
| GET    | /health                | Basic liveness/readiness check           |
| GET    | /trends/scrape         | Fetch raw headlines from sources         |
| POST   | /trends/breakthrough   | Dedupe & score items above threshold     |
| POST   | /content/generate      | Generate social copy & image prompts     |
| POST   | /publish/linkedin      | Publish text (+image) to LinkedIn        |
| POST   | /publish/facebook      | Publish text (+link) to Facebook Page    |

## 📦 Deployment
### Render.com
1. Push to GitHub `main`.
2. On Render: **New Web Service** → connect repo.
3. Build: `pip install -r requirements.txt`
4. Start: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Add env vars from `.env.example` in Render dashboard.

### Docker (optional)
```bash
docker build -t viral-api .
docker run -d -p 8000:8000 --env-file .env viral-api
```

## ✅ Testing
```bash
pytest
```

## 📜 License
MIT

"""

