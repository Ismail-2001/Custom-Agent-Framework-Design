from typing import Dict, Any, List, Optional
from llm.provider import LLMProvider, Message
from state.manager import AgentState

class Reflector:
    """
    enables the agent to critique its own actions and reasoning.
    """
    def __init__(self, llm: LLMProvider):
        self.llm = llm

    async def critique(
        self, 
        task: str, 
        recent_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze recent actions and provide feedback.
        """
        history_text = "\n".join([
            f"{entry['event']}: {entry['data']}" 
            for entry in recent_history[-5:] # Look at last 5 steps
        ])
        
        prompt = f"""
You are a critical reviewer for an AI agent.
Task: {task}

Recent Activity:
{history_text}

Analyze the agent's performance. 
1. Are the actions aligned with the task?
2. Are there any errors or repetitive behaviors?
3. What should the agent do next?

Output JSON format:
{{
    "is_progressing": boolean,
    "critique": "string explanation",
    "suggestion": "string suggestion for next step"
}}
"""
        response = await self.llm.generate([Message(role="user", content=prompt)])
        
        # Simple parsing for now, assuming LLM follows instructions or use Parser
        try:
            import json
            import re
            content = response.content
            # Try to find JSON block
            match = re.search(r"(\{.*\})", content, re.DOTALL)
            if match:
                content = match.group(1)
            return json.loads(content)
        except:
            return {
                "is_progressing": True, 
                "critique": "Failed to parse critique.", 
                "suggestion": "Continue."
            }
