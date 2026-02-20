try:
    from langchain_community.tools import DuckDuckGoSearchRun
except ImportError:
    pass

import asyncio
from dotenv import load_dotenv
from core.agent import Agent
from llm.openai_provider import OpenAIProvider
from integrations.langchain_adapter import LangChainAdapter

load_dotenv()

async def demo_integrations():
    print("=" * 60)
    print("INTEGRATIONS DEMO (LangChain)")
    print("=" * 60)
    
    # 1. Use a LangChain tool in our Agent
    try:
        print("\n[LC] Loading LangChain Mock Tool...")
        
        # Create a simple LangChain tool manually for testing
        from langchain_core.tools import Tool as LCTool
        
        def mock_search(query: str):
            return "Found results for: " + query
            
        lc_tool = LCTool(
            name="mock_search",
            func=mock_search,
            description="A mock search tool"
        )
        
        custom_tool = LangChainAdapter.tool_from_langchain(lc_tool)
        print(f"   Converted to: {custom_tool.name}")
        
        # Use MockLLM to avoid API key issues in this specific test
        from demo import MockLLM
        llm = MockLLM(model="mock")
        agent = Agent(llm=llm, tools=[custom_tool])
        
        print("\n[RUN] Executing search task...")
        result = await agent.run("Search for 'DeepSeek API'", pattern="react")
        if isinstance(result, dict) and "output" in result:
             print(f"\n[RESULT] {result['output']}")
        else:
             print(f"\n[RESULT] {result}")

    except Exception as e:
        print(f"[SKIP] Integration demo skipped: {e}")

if __name__ == "__main__":
    asyncio.run(demo_integrations())
