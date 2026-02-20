import asyncio
import sys
import os
import json

# Add root to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from core.agent import Agent
from memory.manager import MemoryManager
from tools.base import Tool, ToolResult
from llm.provider import LLMProvider, LLMResponse, Message

class MockScalingLLM(LLMProvider):
    def __init__(self):
        self.iteration = 0
        self.hit_rate_limit = False
        
    async def generate(self, messages, tools=None, **kwargs):
        self.iteration += 1
        
        # Simulate a rate limit on the second call
        if self.iteration == 2 and not self.hit_rate_limit:
            self.hit_rate_limit = True
            raise Exception("Rate limit reached. HTTP 429 Too Many Requests.")
            
        if self.iteration <= 3:
            return LLMResponse(content='Thought: I need to delete the old records to clean up.\nAction: delete_database\nAction Input: {"db_name": "old_data.db"}', role="assistant")
            
        return LLMResponse(content="Final Answer: Cleanup completed successfully.", role="assistant")

    def supports_tool_calling(self): return True
    async def stream_generate(self, messages, **kwargs): yield "Done."

class SensitiveTool(Tool):
    name: str = "delete_database"
    description: str = "Deletes a database (Dangerous!)"
    parameters: dict = {"type": "object", "properties": {"db_name": {"type": "string"}}}
    requires_approval: bool = True # TRIGGER HITL
    
    async def _run(self, db_name: str) -> str:
        return f"Database '{db_name}' deleted."

async def simulated_human_approval(tool_name: str, params: dict) -> bool:
    print(f"\n[HUMAN APPROVAL REQUESTED]")
    print(f"Tool: {tool_name}")
    print(f"Arguments: {params}")
    
    # In a real app, this might be a UI button.
    # Here we simulate an approval.
    print("Decision: APPROVED (Simulated)")
    return True

async def run_scaling_demo():
    print("PHASE 7: SCALING & HITL DEMO")
    print("=" * 50)
    
    llm = MockScalingLLM()
    tools = [SensitiveTool()]
    agent = Agent(llm=llm, tools=tools)
    
    task = "Clean up the old database systems."
    print(f"Task: {task}")
    
    # Run with approval callback
    result = await agent.run(task, approval_callback=simulated_human_approval)
    
    print("\n[FINAL OUTPUT]")
    print(result.get("output"))
    
    print("\n[EXECUTION HISTORY]")
    for entry in result["state"]["history"]:
        event = entry["event"]
        data = entry["data"]
        if event == "system" and "Requesting approval" in str(data):
            print(f"- HITL: Framework paused and asked for permission.")
        elif event == "observation" and "denied" in str(data):
            print(f"- Security: User blocked the action.")
        elif event == "observation" and "Rate Limit" in str(data):
            print(f"- Robustness: Agent detected rate limit and backed off.")

if __name__ == "__main__":
    asyncio.run(run_scaling_demo())
