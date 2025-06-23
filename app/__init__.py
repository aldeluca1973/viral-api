from dotenv import load_dotenv
load_dotenv()  # load environment variables from .env before anything else

from fastapi import FastAPI
from .main import router

app = FastAPI(title="Carism Viral‑Automation API", version="0.1.0")
app.include_router(router)
