import asyncio
import os
from dotenv import load_dotenv
from llm.provider import LLMProvider, Message, LLMResponse
from core.agent import Agent
from tools.base import Tool
from state.persistence import StatePersistence

# Load environment
load_dotenv()

class MockLLMWithCritique(LLMProvider):
    def __init__(self, model: str):
        self.model = model
        self.step = 0
    
    def supports_tool_calling(self) -> bool:
        return True
        
    async def stream_generate(self, messages, **kwargs):
        yield "Final."

    async def generate(self, messages, tools=None, **kwargs):
        content = messages[-1].content
        self.step += 1
        
        # Reflection Request
        if "You are a critical reviewer" in content:
            return LLMResponse(
                content='{"is_progressing": false, "critique": "You are iterating but not solving.", "suggestion": "Try reverse calculation."}',
                role="assistant"
            )

        # Normal Agent flow
        if self.step < 3:
            return LLMResponse(
                content=f'Thought: I am trying step {self.step}.\nAction: test_tool\nAction Input: {{"try": {self.step}}}',
                role="assistant"
            )
        elif self.step == 3:
             # Trigger reflection in look by doing something incomplete
             return LLMResponse(
                content=f'Thought: I am stuck.',
                role="assistant"
            )
        else:
             return LLMResponse(
                content='Thought: Based on reflection, I will solve it.\nFinal Answer: Solved after reflection.',
                role="assistant"
            )

class TestTool(Tool):
    name: str = "test_tool"
    description: str = "Testing"
    parameters: dict = {"type": "object", "properties": {"try": {"type": "integer"}}}
    async def _run(self, **kwargs):
        return "Executed"

async def demo_reflection():
    print("=" * 60)
    print("REFLECTION & ROBUSTNESS DEMO")
    print("=" * 60)
    
    llm = MockLLMWithCritique(model="mock-reflect")
    tools = [TestTool()]
    agent = Agent(llm=llm, tools=tools)
    
    print("\n[START] Running task that requires reflection...")
    result = await agent.run("Solve a hard problem", pattern="react")
    
    print(f"\n[RESULT] {result.get('output')}")
    
    print("\n[HISTORY]")
    history = result['state']['history']
    for event in history:
        if event['event'] == 'reflection':
             print(f"🧠 REFLECTION: {event['data']}")
        elif event['event'] == 'thought':
             print(f"💭 THOUGHT: {event['data']}")

if __name__ == "__main__":
    asyncio.run(demo_reflection())
