from dotenv import load_dotenv   # NEW — pulls variables from .env
load_dotenv()     

from fastapi import FastAPI
from .main import router

app = FastAPI(title="Carism Viral‑Automation API", version="0.1.0")
app.include_router(router)
