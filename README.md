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
4. Save settings.
5. Authorize by opening in your browser (single line):
   ```text
   https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=<YOUR_CLIENT_ID>&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Flinkedin%2Foauth&scope=profile%20w_member_social&state=carism123
   ```
6. After allowing, copy the `code=` value from the redirect URL.
7. Exchange the code for a token:
   ```bash
   curl -X POST 'https://www.linkedin.com/oauth/v2/accessToken' \
     -H 'Content-Type: application/x-www-form-urlencoded' \
     --data-urlencode 'grant_type=authorization_code' \
     --data-urlencode 'code=<YOUR_CODE>' \
     --data-urlencode 'client_id=<YOUR_CLIENT_ID>' \
     --data-urlencode 'client_secret=<YOUR_CLIENT_SECRET>' \
     --data-urlencode 'redirect_uri=http://localhost:8000/linkedin/oauth'
   ```
8. Set the returned `access_token` in your `.env` as `LI_ACCESS_TOKEN`.
9. Restart the API server.

## Endpoints
| Method | Path                | Description                                 |
|-------:|---------------------|---------------------------------------------|
| GET    | /trends/scrape      | Fetch raw headlines from sources            |
| POST   | /trends/breakthrough| Dedupe & score items, return above threshold|
| POST   | /content/generate   | Generate copy and image prompts             |
| POST   | /publish/linkedin   | Publish text (+ image) to LinkedIn          |
| POST   | /publish/facebook   | Publish text (+ link) to Facebook Page      |
"""

