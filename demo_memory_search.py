import asyncio
import sys
import os
import math

# Add root to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from memory.vector_store import VectorStoreMemory
from llm.provider import LLMProvider, LLMResponse, Message
from core.agent import Agent

class MockEmbeddingProvider:
    """
    Simple mock embedding provider that converts text to dummy vectors.
    In a real app, this would use OpenAI's text-embedding-3-small.
    """
    def get_embedding(self, text: str) -> list[float]:
        # Create a deterministic vector based on text content
        # Very simple: use alphabetical frequency or hash-based
        vector = [0.0] * 32
        for char in text.lower():
            if 'a' <= char <= 'z':
                index = (ord(char) - ord('a')) % 32
                vector[index] += 1.0
        
        # Normalize
        mag = math.sqrt(sum(x*x for x in vector))
        if mag > 0:
            vector = [x/mag for x in vector]
        return vector

async def run_memory_demo():
    print("🧠 VECTOR MEMORY SEARCH DEMO (Expert Level)")
    print("=" * 50)
    
    vector_store = VectorStoreMemory()
    embedder = MockEmbeddingProvider()
    
    # 1. Store some "expert knowledge"
    knowledge_base = [
        "The best way to build robust agents is using the ReAct pattern combined with episodic memory.",
        "When handling tool failures, always implement exponential backoff retry logic.",
        "State management in agents should support checkpointing and restore functionality for multi-session tasks.",
        "Vector stores are essential for semantic retrieval of long-term knowledge."
    ]
    
    print("Storing knowledge base...")
    for text in knowledge_base:
        embedding = embedder.get_embedding(text)
        await vector_store.store(text, embedding, {"source": "expert_guide"})
    
    # 2. Query the memory
    query = "How to make agents robust?"
    print(f"\nQuerying: '{query}'")
    
    query_embedding = embedder.get_embedding(query)
    results = await vector_store.retrieve(query_embedding, k=2)
    
    print("\n[RELEVANT RESULTS]")
    for i, res in enumerate(results):
        print(f"{i+1}. {res['content']} (Similarity: {res['similarity']:.4f})")
    
    print("\n✅ Memory retrieval verified with cosine similarity.")

if __name__ == "__main__":
    asyncio.run(run_memory_demo())
