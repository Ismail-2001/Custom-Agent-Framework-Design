import asyncio
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.agent import Agent
from tools.base import Tool
from llm.provider import LLMResponse, LLMProvider

class SearchTool(Tool):
    name: str = "scholar_search"
    description: str = "Search academic papers"
    parameters: dict = {"type": "object", "properties": {"query": {"type": "string"}}}

    async def _run(self, query: str) -> str:
        return f"Found paper: 'Agents in 2024: A Survey' (Authors: Smith et al.) Abstract: rapid progress in agentic frameworks..."

class SummarizeTool(Tool):
    name: str = "summarize"
    description: str = "Summarize text"
    parameters: dict = {"type": "object", "properties": {"text": {"type": "string"}}}

    async def _run(self, text: str) -> str:
        return "Summary: The field is evolving correctly with focus on memory and planning."

class ResearchLLM(LLMProvider):
    def __init__(self, model: str = None):
        self.model = model

    def supports_tool_calling(self) -> bool:
        return True
        
    async def stream_generate(self, messages, **kwargs):
        yield "Final."

    async def generate(self, messages, tools=None, **kwargs):
        content = messages[-1].content
        if "state of AI agents" in content:
            if "Summary:" in content:
                return LLMResponse(content="Final Answer: Recent research indicates rapid progress in agentic frameworks, specifically in memory and planning systems (Smith et al., 2024).", role="assistant")
            if "Found paper" in content:
                return LLMResponse(content='Thought: I found a relevant paper. Now I should summarize it.\nAction: summarize\nAction Input: {"text": "Agents in 2024: A Survey..."}', role="assistant")
            return LLMResponse(content='Thought: I need to find papers first.\nAction: scholar_search\nAction Input: {"query": "AI agents 2024"}', role="assistant")
            
        return LLMResponse(content="Final Answer: Done.", role="assistant")

async def main():
    print("="*60)
    print("🎓 RESEARCH ASSISTANT AGENT")
    print("="*60)

    llm = ResearchLLM(model="research-beta")
    tools = [SearchTool(), SummarizeTool()]
    agent = Agent(llm=llm, tools=tools)

    task = "Research the current state of AI agents in 2024"
    result = await agent.run(task, pattern="react")
    print(f"\n[OUTPUT] {result.get('output', result)}")

if __name__ == "__main__":
    asyncio.run(main())
