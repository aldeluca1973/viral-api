from dotenv import load_dotenv
load_dotenv()   # ← make sure this is the very first thing in __init__.py

from fastapi import FastAPI
from .main import router

app = FastAPI(title="Carism Viral‑Automation API", version="0.1.0")
app.include_router(router)
