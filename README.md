"""
# Carism Viral‑Automation API

## Local dev
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill vars
uvicorn app:app --reload
```

## Endpoints
| Method | Path | Description |
|---|---|---|
| GET | /trends/scrape | Fetch raw headlines |
| POST | /trends/breakthrough | Return scored items ≥ threshold |
| POST | /content/generate | Claude/OpenAI copy + image prompt |
| POST | /publish/linkedin | Publish text+image |

## Render deploy
* Runtime: Python 3.11
* Start: `uvicorn app:app --host 0.0.0.0 --port $PORT`
* Add env vars seen in `.env.example`
"""

