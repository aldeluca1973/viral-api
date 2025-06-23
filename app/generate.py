from langchain_openai import ChatOpenAI
from .utils import async_retry
import os

llm = ChatOpenAI(model="gpt-4o", temperature=0.5)

@async_retry()
async def generate_copy(headline:str, tone:str, platform:str):
    prompt = (f"Write a {tone} {platform} post (max 50 words) about: '{headline}'.\n"
              f"Return JSON with keys text, image_prompt.")
    resp = llm.invoke(prompt)
    return resp.content


