import asyncio
import sys
import os
import json

# Add root to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from core.agent import Agent
from tools.base import Tool, ToolResult
from llm.provider import LLMProvider, LLMResponse, Message

class MockPlanningLLM(LLMProvider):
    def __init__(self):
        self.iteration = 0
        
    async def generate(self, messages, tools=None, **kwargs):
        prompt = messages[-1].content
        
        # 1. INITIAL PLANNING
        if "Decompose the following task" in prompt:
            return LLMResponse(content=json.dumps({
                "steps": [
                    {"id": 1, "task": "Design schema", "tool": None},
                    {"id": 2, "task": "Write code", "tool": "code_writer"},
                    {"id": 3, "task": "Test pipeline", "tool": "tester"}
                ]
            }), role="assistant")
            
        # 2. REACT LOOP
        self.iteration += 1
        
        if self.iteration == 1:
            return LLMResponse(content='Thought: I will write the code.\nAction: code_writer\nAction Input: {"code": "pipeline.py"}', role="assistant")
             
        if self.iteration == 2:
            return LLMResponse(content='Thought: Now I need to test.\nAction: tester\nAction Input: {"module": "pipeline"}', role="assistant")

        if self.iteration == 3:
            return LLMResponse(content='Thought: Still testing...\nAction: tester\nAction Input: {"module": "pipeline"}', role="assistant")

        if self.iteration == 4:
             return LLMResponse(content='Thought: Re-testing again to trigger reflection loop at step 4 (i=3).\nAction: tester\nAction Input: {"module": "pipeline"}', role="assistant")

        # 3. REFLECTION
        if "Analyze the agent's performance" in prompt:
            return LLMResponse(content=json.dumps({
                "is_progressing": False,
                "critique": "The agent is repeating the test action without progress.",
                "suggestion": "We need to fix the module and update the plan."
            }), role="assistant")
            
        # 4. REPLANNING
        if "update the plan" in prompt:
            return LLMResponse(content=json.dumps({
                "steps": [
                    {"id": 4, "task": "Debug the code", "tool": "code_writer"},
                    {"id": 5, "task": "Final check", "tool": "tester"}
                ]
            }), role="assistant")
            
        if self.iteration >= 5:
             return LLMResponse(content="Final Answer: Task completed successfully after adaptive replanning.", role="assistant")

        return LLMResponse(content="Thought: Continuing...\nAction: code_writer\nAction Input: {}", role="assistant")

    def supports_tool_calling(self): return True
    async def stream_generate(self, messages, **kwargs): yield "Done."

class DummyTool(Tool):
    parameters: dict = {"type": "object", "properties": {"input": {"type": "string"}}}
    async def _run(self, **kwargs): return "Success"

async def run_adaptive_demo():
    print("ADAPTIVE PLANNING DEMO")
    print("=" * 50)
    
    llm = MockPlanningLLM()
    tools = [
        DummyTool(name="code_writer", description="Write code"),
        DummyTool(name="tester", description="Run tests")
    ]
    
    agent = Agent(llm=llm, tools=tools)
    
    task = "Build and test a simple data pipeline"
    print(f"Task: {task}")
    
    result = await agent.run(task, use_planning=True)
    
    print("\n[FINAL OUTPUT]")
    print(result.get("output"))
    
    print("\n[EXECUTION HISTORY]")
    for entry in result["state"]["history"]:
        event = entry["event"]
        data = entry["data"]
        if event == "plan":
            print(f"- Initial Plan: {len(data['steps'])} steps created.")
        elif event == "plan_update":
            print(f"- Plan Updated! {len(data['steps'])} new steps.")
        elif event == "reflection":
            print(f"- Reflection: {data.get('critique')}")

if __name__ == "__main__":
    asyncio.run(run_adaptive_demo())
