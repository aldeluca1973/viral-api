# <app/utils.py>
import time, functools, asyncio
import aiohttp
import os

def async_retry(retries=3, delay=1):
    def decorator(fn):
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return await fn(*args, **kwargs)
                except Exception as e:
                    if attempt == retries - 1:
                        raise
                    await asyncio.sleep(delay)
        return wrapper
    return decorator

# Embedding function with multiple provider options
async def embed_text(text: str, provider: str = "azure") -> list:
    """
    Generate embeddings for text using various providers.
    
    Args:
        text: The text to embed
        provider: "azure", "openai", or "local"
    
    Returns:
        List of floats representing the embedding vector
    """
    
    if provider == "azure":
        # Azure AI Search embedding
        AI_KEY = os.getenv("AI_SEARCH_KEY")
        AI_ENDPOINT = os.getenv("AI_SEARCH_ENDPOINT")
        
        if not AI_KEY or not AI_ENDPOINT:
            raise ValueError("Azure AI Search credentials not configured")
        
        async with aiohttp.ClientSession() as session:
            # Azure expects the embedding endpoint format
            url = f"{AI_ENDPOINT}/indexes/carismindex/docs/search.post.embedding"
            
            headers = {
                "api-key": AI_KEY,
                "Content-Type": "application/json"
            }
            
            # Azure embedding request format
            data = {
                "text": text
            }
            
            async with session.post(url, json=data, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Azure embedding failed: {error_text}")
                
                result = await response.json()
                return result.get("embedding", [])
    
    elif provider == "openai":
        # OpenAI embeddings (requires openai package and API key)
        OPENAI_KEY = os.getenv("OPENAI_API_KEY")
        
        if not OPENAI_KEY:
            raise ValueError("OpenAI API key not configured")
        
        # You'll need to: pip install openai
        import openai
        
        client = openai.AsyncOpenAI(api_key=OPENAI_KEY)
        
        response = await client.embeddings.create(
            model="text-embedding-3-small",  # Or "text-embedding-ada-002"
            input=text
        )
        
        return response.data[0].embedding
    
    elif provider == "local":
        # Free local embeddings using sentence-transformers
        # You'll need to: pip install sentence-transformers
        try:
            from sentence_transformers import SentenceTransformer
            
            # Load model (downloads on first use, ~400MB)
            model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Generate embedding
            embedding = model.encode(text)
            
            return embedding.tolist()
        
        except ImportError:
            raise ImportError(
                "sentence-transformers not installed. "
                "Run: pip install sentence-transformers"
            )
    
    else:
        raise ValueError(f"Unknown provider: {provider}")

# Helper function to find similar content
async def find_similar_topics(query_text: str, all_topics: list, provider: str = "local", top_k: int = 5):
    """
    Find the most similar topics to a query using embeddings.
    
    Args:
        query_text: The text to search for
        all_topics: List of topics to search through
        provider: Embedding provider to use
        top_k: Number of similar topics to return
    """
    import numpy as np
    
    # Get query embedding
    query_embedding = await embed_text(query_text, provider)
    query_vec = np.array(query_embedding)
    
    # Calculate similarities
    similarities = []
    for topic in all_topics:
        topic_embedding = await embed_text(topic, provider)
        topic_vec = np.array(topic_embedding)
        
        # Cosine similarity
        similarity = np.dot(query_vec, topic_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(topic_vec))
        similarities.append((topic, similarity))
    
    # Sort by similarity
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    return similarities[:top_k]
