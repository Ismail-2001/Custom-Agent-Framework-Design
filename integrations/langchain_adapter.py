from typing import Any, Dict, List, Optional
from tools.base import Tool, ToolResult

# Try to import LangChain components, but don't fail if not installed
try:
    from langchain_core.tools import BaseTool as LangChainBaseTool
    from langchain.agents import AgentExecutor
    from langchain.agents import BaseSingleActionAgent
except ImportError:
    LangChainBaseTool = object
    AgentExecutor = object
    BaseSingleActionAgent = object

class LangChainAdapter:
    """
    Adapt custom framework to LangChain.
    """
    
    @staticmethod
    def tool_to_langchain(tool: Tool) -> Any:
        """Convert custom tool to LangChain tool."""
        # Dynamic creation of a LangChain tool class
        from langchain_core.tools import Tool as LCTool
        
        async def _wrapper(input_str: str) -> str:
            # LangChain tools typically take a string input, or we need more complex logic
            # For simplicity, we assume single string or try to parse JSON
            import json
            try:
                kwargs = json.loads(input_str)
            except:
                # If only one param, assume input_str is that param
                if len(tool.parameters.get("properties", {})) == 1:
                    key = list(tool.parameters["properties"].keys())[0]
                    kwargs = {key: input_str}
                else:
                    kwargs = {}
                    
            result = await tool.execute(**kwargs)
            return str(result.output) if result.success else f"Error: {result.error}"

        return LCTool(
            name=tool.name,
            func=lambda x: "Async tool, use ainvoke", # Placeholder for sync execution
            description=tool.description,
            coroutine=_wrapper
        )
        
    @staticmethod
    def tool_from_langchain(lc_tool: Any) -> Tool:
        """Convert LangChain tool to custom tool."""
        
        class WrappedLangChainTool(Tool):
            name: str = lc_tool.name
            description: str = lc_tool.description
            parameters: dict = {"type": "object", "properties": {"input": {"type": "string"}}} # Simplified
            
            async def _run(self, **kwargs):
                # We assume kwargs has what lc_tool needs
                # This is a simplification; handling all LC input schemas is complex
                input_val = kwargs.get("input") or kwargs.get("query") or list(kwargs.values())[0]
                try:
                    # Prefer async run if available
                    if hasattr(lc_tool, "ainvoke"):
                         return await lc_tool.ainvoke(input_val)
                    elif hasattr(lc_tool, "arun"):
                        return await lc_tool.arun(input_val)
                    else:
                        return lc_tool.run(input_val)
                except Exception as e:
                    raise e

        return WrappedLangChainTool()
