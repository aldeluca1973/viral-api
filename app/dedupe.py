# <app/dedupe.py>
import hashlib
from .utils import async_retry, embed_text
import numpy as np

@async_retry()
async def dedupe_headlines(items, similarity_threshold=0.85):
    """Remove duplicates based on semantic similarity"""
    if not items:
        return []
    
    # For backwards compatibility, handle both list of dicts and list of items
    if isinstance(items[0], dict):
        items_list = items
    else:
        items_list = [item if isinstance(item, dict) else item.dict() for item in items]
    
    unique_items = []
    seen_embeddings = []
    
    for item in items_list:
        try:
            # Get embedding for current headline
            current_embedding = await embed_text(item["headline"], provider="local")
            current_vec = np.array(current_embedding)
            
            # Check if it's too similar to existing items
            is_duplicate = False
            for seen_vec in seen_embeddings:
                # Cosine similarity
                similarity = np.dot(current_vec, seen_vec) / (
                    np.linalg.norm(current_vec) * np.linalg.norm(seen_vec)
                )
                
                if similarity > similarity_threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_items.append(item)
                seen_embeddings.append(current_vec)
                
        except Exception as e:
            # If embedding fails, fall back to exact match
            print(f"Embedding failed for: {item['headline']}, using exact match")
            if item["headline"] not in [u["headline"] for u in unique_items]:
                unique_items.append(item)
    
    return unique_items
