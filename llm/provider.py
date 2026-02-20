from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncIterator
from pydantic import BaseModel

class Message(BaseModel):
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = None

class LLMResponse(BaseModel):
    content: str
    role: str = "assistant"
    tool_calls: Optional[List[Dict[str, Any]]] = None
    usage: Optional[Dict[str, int]] = None

class LLMProvider(ABC):
    """
    Unified LLM interface.
    """
    
    @abstractmethod
    async def generate(
        self,
        messages: List[Message],
        tools: Optional[List[Any]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> LLMResponse:
        """Generate completion."""
        pass
        
    @abstractmethod
    async def stream_generate(
        self,
        messages: List[Message],
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream completion."""
        pass
    
    @abstractmethod
    def supports_tool_calling(self) -> bool:
        """Check if provider supports native tool calling."""
        pass
