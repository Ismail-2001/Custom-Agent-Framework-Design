import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class ToolResult(BaseModel):
    """Standardized tool output."""
    success: bool
    output: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    duration: float = 0.0
    cost: Optional[float] = None

class Tool(BaseModel):
    """
    Base tool specification.
    """
    name: str
    description: str
    parameters: Dict[str, Any]  # JSON Schema
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute tool with given parameters. Should be overridden by subclasses."""
        start_time = time.time()
        try:
            # This is a base implementation, subclasses must override _run
            output = await self._run(**kwargs)
            return ToolResult(
                success=True,
                output=output,
                duration=time.time() - start_time
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
                duration=time.time() - start_time
            )

    async def _run(self, **kwargs) -> Any:
        """The actual implementation of the tool."""
        raise NotImplementedError("Subclasses must implement _run")

    def to_openai_function(self) -> Dict[str, Any]:
        """Convert to OpenAI function calling format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }
