from abc import ABC, abstractmethod
from typing import Any, List, Dict, Optional

class BaseMemory(ABC):
    @abstractmethod
    async def store(self, key: str, value: Any, metadata: Optional[Dict] = None) -> None:
        """Store information in memory."""
        pass
        
    @abstractmethod
    async def retrieve(self, query: str, k: int = 5) -> List[Dict]:
        """Retrieve relevant memories."""
        pass
        
    @abstractmethod
    async def clear(self) -> None:
        """Clear all memories."""
        pass
