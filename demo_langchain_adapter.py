import asyncio
import sys
import os

# Add root to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from tools.base import Tool, ToolResult
from integrations.langchain_adapter import LangChainAdapter

class CustomSearchTool(Tool):
    name: str = "custom_search"
    description: str = "Search my local documents"
    parameters: dict = {"type": "object", "properties": {"query": {"type": "string"}}}
    
    async def _run(self, query: str) -> str:
        return f"Results for '{query}': Document A mentions 'Expert Agent Framework'."

async def run_langchain_demo():
    print("🦜 LANGCHAIN ADAPTER DEMO")
    print("=" * 50)
    
    # 1. Take our custom tool
    custom_tool = CustomSearchTool()
    
    # 2. Convert to LangChain tool
    print("Converting custom tool to LangChain format...")
    lc_tool = LangChainAdapter.tool_to_langchain(custom_tool)
    
    print(f"LangChain Tool Name: {lc_tool.name}")
    print(f"LangChain Tool Description: {lc_tool.description}")
    
    # 3. Use it via LangChain (simulated or real if installed)
    print("\nExecuting tool via LangChain adapter interface...")
    try:
        # We test the coroutine we wrapped
        result = await lc_tool.coroutine('{"query": "expert"}')
        print(f"Result: {result}")
        
        if "Results for 'expert'" in result:
             print("\n✅ Tool successfully executed through adapter!")
    except Exception as e:
        print(f"Execution failed (expected if LangChain not in environment): {e}")

if __name__ == "__main__":
    asyncio.run(run_langchain_demo())
