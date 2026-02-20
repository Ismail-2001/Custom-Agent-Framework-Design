import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.agent import Agent
from tools.base import Tool
from llm.provider import LLMResponse, LLMProvider

class CodeAnalysisTool(Tool):
    name: str = "analyze_code"
    description: str = "Analyze python code for style and errors"
    parameters: dict = {
        "type": "object", 
        "properties": {
            "code": {"type": "string"},
            "focus": {"type": "string", "enum": ["style", "bugs", "security"]}
        }
    }

    async def _run(self, code: str, focus: str = "style") -> str:
        # Simulate static analysis
        issues = []
        if "eval(" in code:
            issues.append("[SECURITY] Avoid using eval()")
        if "print" in code and focus == "style":
            issues.append("[STYLE] Use logging instead of print")
        
        if not issues:
            return "No issues found."
        return "\n".join(issues)

# Mock specialized LLM for code review
    def __init__(self, model: str = None):
        self.model = model
        self.found_security_issue = False
        
    def supports_tool_calling(self) -> bool:
        return True
        
    async def stream_generate(self, messages, **kwargs):
        yield "Final Answer: Code looks good."

    async def generate(self, messages, tools=None, **kwargs):
        content = messages[-1].content
        
        # Check if previous tool execution found the issue
        # We can look at the content for the observation
        if "Observation: [SECURITY]" in content:
            self.found_security_issue = True
            
        if self.found_security_issue:
             return LLMResponse(content="Final Answer: The code contains a critical security issue: use of eval(). Suggested fix: Parse inputs safely.", role="assistant")
             
        # Initial thought or re-try
        if "def unsafe_function" in content and not self.found_security_issue:
            return LLMResponse(content='Thought: I should check for security issues.\nAction: analyze_code\nAction Input: {"code": "def unsafe_function(x): eval(x)", "focus": "security"}', role="assistant")
        
        return LLMResponse(content="Final Answer: Code looks good.", role="assistant")

async def main():
    print("="*60)
    print("🤖 CODE REVIEW AGENT")
    print("="*60)

    llm = CodeReviewLLM(model="code-alpha")
    tools = [CodeAnalysisTool()]
    agent = Agent(llm=llm, tools=tools)

    code_snippet = "def unsafe_function(x): eval(x)"
    print(f"\nAnalyzing:\n{code_snippet}\n")
    
    result = await agent.run(f"Review this code: {code_snippet}", pattern="react")
    print(f"[REPORT] {result.get('output', result)}")

if __name__ == "__main__":
    asyncio.run(main())
