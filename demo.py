import asyncio
import os
from dotenv import load_dotenv
from llm.provider import LLMProvider, Message, LLMResponse
from llm.openai_provider import OpenAIProvider
from core.agent import Agent
from tools.base import Tool, ToolResult

# Load environment variables
load_dotenv()

class CalculatorTool(Tool):
    name: str = "calculator"
    description: str = "Perform simple arithmetic operations"
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
        yield "The final result is 115."

    async def generate(self, messages, tools=None, **kwargs):
        last_msg = messages[-1].content
        content = last_msg # Aligning with the provided snippet's variable name
        
        if "What is 2+2?" in content:
            if "Observation: 4" in content:
                return LLMResponse(content="Thought: I have the result.\nFinal Answer: The answer is 4", role="assistant")
            return LLMResponse(
                content='Thought: I need to add 2 and 2.\nAction: calculator\nAction Input: {"operation": "add", "a": 2, "b": 2}',
                role="assistant"
            )
        if "Search" in content or "DeepSeek" in content:
            # Check if we already have the observation in previous messages (simulating history check)
            # In our simple mock, we check if the LAST message was a tool result
            is_tool_result = False
            # This is a bit hacky because we don't pass full history to generate here properly in the demo structure
            # But based on the "Found results" check:
            if "Found results" in content: 
                 return LLMResponse(content="Thought: I found it.\nFinal Answer: I found the information about DeepSeek API.", role="assistant")
            
            # If we don't see results, search
            return LLMResponse(content='Thought: I need to search.\nAction: mock_search\nAction Input: {"query": "DeepSeek API"}', role="assistant")
            
        # Original logic for 15*7 and +10, adapted to fit the new structure
        if "15 multiplied by 7" in last_msg:
             return LLMResponse(
                content="I need to multiply 15 by 7.",
                role="assistant",
                tool_calls=[{
                    "id": "call_1",
                    "type": "function",
                    "function": {
                        "name": "calculator",
                        "arguments": '{"operation": "multiply", "a": 15, "b": 7}'
                    }
                }]
            )
        elif "105" in last_msg:
             return LLMResponse(
                content="Now I need to add 10 to 105.",
                role="assistant",
                tool_calls=[{
                    "id": "call_2",
                    "type": "function",
                    "function": {
                        "name": "calculator",
                        "arguments": '{"operation": "add", "a": 105, "b": 10}'
                    }
                }]
            )
        else:
            return LLMResponse(content="The final result is 115.", role="assistant")

async def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize LLM Provider
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key and not api_key.startswith("your_"):
        print("Using real OpenAI Provider...")
        llm = OpenAIProvider(model="gpt-4o-mini")
    else:
        print("OPENAI_API_KEY not found or default. Using MockLLM...")
        llm = MockLLM(model="mock-model")
    
    # Initialize Tools
    tools = [CalculatorTool()]
    
    # Initialize Agent
    agent = Agent(llm=llm, tools=tools)
    
    # Run a task
    task = "What is 15 multiplied by 7, and then add 10 to the result?"
    print(f"Running task: {task}")
    
    result = await agent.run(task)
    
    print("\n--- Final Output ---")
    print(result.get("output", "No output"))
    
    print("\n--- Execution History ---")
    for event in result["state"]["history"]:
        # Truncate data for cleaner output
        data_str = str(event['data'])[:100] + "..." if len(str(event['data'])) > 100 else str(event['data'])
        print(f"[{event['timestamp']}] {event['event']}: {data_str}")

if __name__ == "__main__":
    asyncio.run(main())
