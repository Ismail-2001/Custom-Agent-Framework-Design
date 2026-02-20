import os
from typing import List, Dict, Any, Optional, AsyncIterator
from openai import AsyncOpenAI
from .provider import LLMProvider, Message, LLMResponse

class OpenAIProvider(LLMProvider):
    """OpenAI implementation of LLMProvider."""
    
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        organization: Optional[str] = None
    ):
        self.model = model
        # api_key will be read from environment if not provided
        self.client = AsyncOpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"), organization=organization)
        
    async def generate(
        self,
        messages: List[Message],
        tools: Optional[List[Any]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> LLMResponse:
        formatted_messages = [{"role": m.role, "content": m.content} for m in messages]
        
        params = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        if tools:
            # Placeholder for tool conversion logic
            params["tools"] = tools
            
        response = await self.client.chat.completions.create(**params)
        choice = response.choices[0].message
        
        tool_calls = None
        if hasattr(choice, 'tool_calls') and choice.tool_calls:
            tool_calls = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                } for tc in choice.tool_calls
            ]
            
        return LLMResponse(
            content=choice.content or "",
            role=choice.role,
            tool_calls=tool_calls,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        )
        
    async def stream_generate(
        self,
        messages: List[Message],
        **kwargs
    ) -> AsyncIterator[str]:
        formatted_messages = [{"role": m.role, "content": m.content} for m in messages]
        
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=formatted_messages,
            stream=True,
            **kwargs
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def supports_tool_calling(self) -> bool:
        return True
