import asyncio
import time
from dotenv import load_dotenv
from llm.provider import LLMProvider, Message, LLMResponse
from llm.openai_provider import OpenAIProvider
from core.agent import Agent
from tools.base import Tool, ToolResult
from state.persistence import StatePersistence
from observability.logger import AgentLogger
from observability.metrics import MetricsCollector

# Load environment
load_dotenv()

class CalculatorTool(Tool):
    name: str = "calculator"
    description: str = "Perform arithmetic operations"
    parameters: dict = {
        "type": "object",
        "properties": {
            "operation": {"type": "string", "enum": ["add", "subtract", "multiply", "divide"]},
            "a": {"type": "number"},
            "b": {"type": "number"}
        },
        "required": ["operation", "a", "b"]
    }

    async def _run(self, operation: str, a: float, b: float) -> float:
        if operation == "add":
            return a + b
        elif operation == "subtract":
            return a - b
        elif operation == "multiply":
            return a * b
        elif operation == "divide":
            return a / b
        else:
            raise ValueError(f"Unknown operation: {operation}")

class MockLLM(LLMProvider):
    def __init__(self, model: str):
        self.model = model
    
    def supports_tool_calling(self) -> bool:
        return True
        
    async def stream_generate(self, messages, **kwargs):
        yield "The final result."

    async def generate(self, messages, tools=None, **kwargs):
        content = messages[-1].content
        
        # Multi-step ReAct simulation
        if "research AI agents" in content:
            if "Observation:" not in content:
                return LLMResponse(
                    content='Thought: I should search for information.\nAction: web_search\nAction Input: {"query": "AI agents 2024"}',
                    role="assistant"
                )
            else:
                return LLMResponse(
                    content='Thought: I have sufficient information.\nFinal Answer: AI agents are autonomous systems that can perceive, reason, and act.',
                    role="assistant"
                )
        
        # Calculator example
        if "multiply 25 by 8" in content:
            if "Observation: 200" in content:
                return LLMResponse(
                    content='Thought: Now I need to add 15.\nAction: calculator\nAction Input: {"operation": "add", "a": 200, "b": 15}',
                    role="assistant"
                )
            elif "Observation: 215" in content:
                return LLMResponse(
                    content='Thought: I have the final answer.\nFinal Answer: The result is 215.',
                    role="assistant"
                )
            else:
                return LLMResponse(
                    content='Thought: First multiply 25 by 8.\nAction: calculator\nAction Input: {"operation": "multiply", "a": 25, "b": 8}',
                    role="assistant"
                )
        
        return LLMResponse(content="Final Answer: Task completed.", role="assistant")

async def demo_advanced_features():
    print("=" * 60)
    print("CUSTOM AGENT FRAMEWORK - ADVANCED DEMO")
    print("=" * 60)
    
    # Initialize components
    llm = MockLLM(model="mock-advanced")
    tools = [CalculatorTool()]
    
    # Create logger and metrics
    logger = AgentLogger("demo_agent", "INFO")
    metrics = MetricsCollector()
    
    # Create agent with persistence
    persistence = StatePersistence(backend="sqlite", db_path="demo_state.db")
    agent = Agent(llm=llm, tools=tools)
    
    # Task 1: Multi-step calculation
    print("\n[CALC] TASK 1: Multi-Step Calculation")
    print("-" * 60)
    task1 = "What is 25 multiplied by 8, then add 15?"
    
    logger.log_iteration_start(1, task1)
    start = time.time()
    
    result1 = await agent.run(task1, pattern="react")
    
    duration1 = time.time() - start
    metrics.record_task_completion(
        success=result1.get("state", {}).get("status") == "completed",
        total_duration=duration1,
        iterations=len(result1.get("state", {}).get("history", [])),
        total_cost=0.0
    )
    
    print(f"\n[OK] Result: {result1.get('output', 'No output')}")
    print(f"[TIME] Duration: {duration1:.2f}s")
    print(f"[STATS] Steps: {len(result1.get('state', {}).get('history', []))}")
    
    # Show episodic memory
    print("\n[MEMORY] Episodic Memory:")
    episodes = await agent.memory.recall("multiply", memory_types=["episodic"], k=5)
    if episodes.get("episodic"):
        for ep in episodes["episodic"][:2]:
            print(f"  - Task: {ep['task'][:50]}... | Success: {ep['success']}")
    
    # Checkpoint demo
    print("\n[SAVE] Creating checkpoint...")
    checkpoint_id = await agent.state_manager.checkpoint(label="after_task1")
    print(f"   Checkpoint saved: {checkpoint_id}")
    
    # Display metrics
    print("\n[METRICS] SUMMARY")
    print("-" * 60)
    summary = metrics.get_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Demo completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(demo_advanced_features())
