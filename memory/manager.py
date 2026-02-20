from typing import Any, List, Dict, Optional
from .short_term import ShortTermMemory
from .long_term import LongTermMemory
from .episodic import Episode
from .vector_store import VectorStoreMemory

class MemoryManager:
    """
    Central memory coordinator.
    Routes queries to appropriate memory types and manages consolidation.
    """
    
    def __init__(self, db_path: str = "agent_memory.db"):
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory(db_path)
        self.episodic = Episode(db_path)
        self.vector_store = VectorStoreMemory()
        
    async def remember(
        self,
        content: Any,
        role: str = None,
        memory_type: str = "auto",
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Store content in appropriate memory.
        """
        if memory_type == "short_term" or (memory_type == "auto" and role):
            await self.short_term.store(role, content, metadata)
            
        if memory_type == "long_term" or memory_type == "auto":
            if isinstance(content, dict) and "key" in content:
                await self.long_term.store(content["key"], content["value"], metadata)
                
    async def add_episode(
        self,
        task: str,
        steps: List[Dict],
        success: bool,
        final_answer: str,
        duration: float
    ) -> int:
        return await self.episodic.store_episode(task, steps, success, final_answer, duration)
        
    async def recall(
        self,
        query: str,
        memory_types: List[str] = ["short_term", "long_term", "episodic", "vector"],
        k: int = 5
    ) -> Dict[str, Any]:
        results = {}
        
        if "short_term" in memory_types:
            results["short_term"] = await self.short_term.retrieve(query, k)
            
        if "long_term" in memory_types:
            results["long_term"] = await self.long_term.retrieve(query, k)
            
        if "episodic" in memory_types:
            results["episodic"] = await self.episodic.retrieve(query, k)

        if "vector" in memory_types:
            results["vector"] = await self.vector_store.retrieve(query, k)
            
        return results

    async def clear_all(self) -> None:
        await self.short_term.clear()
        await self.long_term.clear()
        await self.episodic.clear()
        await self.vector_store.clear()
