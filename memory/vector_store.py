import math
from typing import Any, List, Dict, Optional
from .base import BaseMemory

class VectorStoreMemory(BaseMemory):
    """
    Lightweight Vector Store Memory implementing cosine similarity from first principles.
    In a real implementation, this would use ChromaDB, Pinecone, or FAISS.
    """
    
    def __init__(self):
        self.vectors = [] # List of (embedding, content, metadata)
        
    async def store(self, content: str, embedding: List[float], metadata: Optional[Dict] = None) -> None:
        self.vectors.append({
            "content": content,
            "embedding": embedding,
            "metadata": metadata or {}
        })
        
    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(v1, v2))
        magnitude_v1 = math.sqrt(sum(a * a for a in v1))
        magnitude_v2 = math.sqrt(sum(b * b for b in v2))
        
        if magnitude_v1 == 0 or magnitude_v2 == 0:
            return 0.0
            
        return dot_product / (magnitude_v1 * magnitude_v2)
        
    async def retrieve(self, query_embedding: List[float], k: int = 5) -> List[Dict]:
        """
        Retrieves top k similar items based on cosine similarity.
        """
        if not self.vectors:
            return []
            
        # Calculate similarities and sort
        scored_vectors = []
        for v in self.vectors:
            similarity = self._cosine_similarity(query_embedding, v["embedding"])
            scored_vectors.append({**v, "similarity": similarity})
            
        # Sort by similarity descending
        scored_vectors.sort(key=lambda x: x["similarity"], reverse=True)
        
        return scored_vectors[:k]
        
    async def clear(self) -> None:
        self.vectors = []
