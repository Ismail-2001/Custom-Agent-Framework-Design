from typing import Any, List, Dict, Optional
from collections import deque
from .base import BaseMemory
from llm.provider import Message

class ShortTermMemory(BaseMemory):
    """
    Conversation buffer with sliding window.
    """
    
    def __init__(self, max_messages: int = 50, max_tokens: int = 4000):
        self.messages = deque(maxlen=max_messages)
        self.max_tokens = max_tokens
        
    async def add_message(self, content: str, role: str = "user", metadata: Optional[Dict] = None):
        """Standard method for adding messages."""
        self.messages.append(Message(role=role, content=content))
        
    async def store(self, role: str, content: str, metadata: Optional[Dict] = None) -> None:
        """Alias for add_message to satisfy BaseMemory interface."""
        await self.add_message(content, role, metadata)
        
    async def retrieve(self, query: str, k: int = 5) -> List[Dict]:
        # Simple retrieval: return last k messages
        return [m.model_dump() for m in list(self.messages)[-k:]]
        
    async def get_messages(self) -> List[Message]:
        """Returns all messages as Message objects."""
        return list(self.messages)
        
    async def get_all(self) -> List[Dict]:
        return [m.model_dump() for m in list(self.messages)]
        
    async def clear(self) -> None:
        self.messages.clear()
