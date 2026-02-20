from typing import Dict, Any, Optional
from .base import Tool, ToolResult
from core.robustness import ErrorHandler

class ToolExecutor:
    """
    Execute tools with monitoring and error handling.
    """
    
    async def execute(
        self,
        tool: Tool,
        params: Dict[str, Any],
        max_retries: int = 2
    ) -> ToolResult:
        """
        Execute tool with monitoring and retry logic.
        """
        # Wrap tool.execute in robustness handler
        success, result = await ErrorHandler.retry_with_backoff(
            tool.execute,
            max_retries=max_retries,
            base_delay=0.5,
            **params
        )
        
        if success:
            return result
        else:
            return ToolResult(
                success=False,
                output=None,
                error=f"Execution failed after maximum retries. Last error: {result}"
            )
