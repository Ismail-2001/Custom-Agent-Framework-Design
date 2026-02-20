import pytest
import asyncio
from typing import List, Dict, Any, Optional
from llm.provider import LLMProvider, Message, LLMResponse
from tools.base import Tool, ToolResult
from core.agent import Agent

class MockLLM(LLMProvider):
    async def generate(self, messages, tools=None, **kwargs):
        # The content is the full prompt including tools and scratchpad
        prompt = messages[-1].content
        
        # If the task is 2+2
        if "What is 2+2?" in prompt:
            # Check if we've already done the calculation
            if "Observation: 4" in prompt:
                return LLMResponse(
                    content="Thought: I have the result from the calculator. The answer is 4.\nFinal Answer: The answer is 4",
                    role="assistant"
                )
            
            # Initial thought and action
            return LLMResponse(
                content='Thought: I need to calculate the sum of 2 and 2.\nAction: calculator\nAction Input: {"operation": "add", "a": 2, "b": 2}',
                role="assistant"
            )
            
        return LLMResponse(content="Final Answer: I am not sure how to help with that.", role="assistant")

    async def stream_generate(self, messages, **kwargs):
        yield "Final Answer: The answer is 4"

    def supports_tool_calling(self):
        return True

class CalculatorTool(Tool):
    name: str = "calculator"
    description: str = "Perform arithmetic"
    parameters: dict = {
        "type": "object",
        "properties": {
            "operation": {"type": "string"},
            "a": {"type": "number"},
            "b": {"type": "number"}
        }
    }
    async def _run(self, operation, a, b):
        return a + b

@pytest.mark.asyncio
async def test_agent_basic_run():
    llm = MockLLM()
    tool = CalculatorTool()
    agent = Agent(llm=llm, tools=[tool])
    
    result = await agent.run("What is 2+2?")
    
    # Check if 'output' exists (if not, result might be an error dict)
    assert "output" in result, f"Agent failed: {result.get('error', 'unknown error')}"
    assert "4" in result["output"]
    assert result["state"]["status"] == "completed"
