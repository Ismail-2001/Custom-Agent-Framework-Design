from typing import List, Dict, Any, Optional
from .provider import Message
from tools.base import Tool

class PromptBuilder:
    """
    Constructs prompts for different agent patterns.
    """
    
    REACT_TEMPLATE = """
Task: {task}

Available Tools:
{tool_descriptions}

Follow this format:
Thought: [your reasoning about what to do next]
Action: [tool name to use]
Action Input: [parameters as JSON]
Observation: [tool result will appear here]

When you have enough information:
Thought: I can now answer the original question
Final Answer: [your response to the user]

Current History:
{scratchpad}

Begin!
"""

    PLANNING_TEMPLATE = """
Break down the following task into a step-by-step plan.

Task: {task}

Context: {context}

Provide a numbered list of steps. Each step should:
1. Be specific and actionable.
2. State which tool to use.
3. Note dependencies on previous steps.

Plan:
"""

    def build_react_prompt(
        self,
        task: str,
        tools: List[Tool],
        scratchpad: str = ""
    ) -> str:
        tool_descriptions = "\n".join([f"- {t.name}: {t.description} (Params: {t.parameters})" for t in tools])
        return self.REACT_TEMPLATE.format(
            task=task,
            tool_descriptions=tool_descriptions,
            scratchpad=scratchpad
        )

    def build_planning_prompt(
        self,
        task: str,
        context: Dict[str, Any] = None
    ) -> str:
        return self.PLANNING_TEMPLATE.format(
            task=task,
            context=context or "No additional context provided."
        )

    def build_tool_messages(
        self,
        task: str,
        tools: List[Tool],
        history: List[Dict[str, Any]]
    ) -> List[Message]:
        """
        Builds a list of messages for native tool calling.
        """
        messages = [Message(role="system", content="You are a helpful assistant with access to tools.")]
        # Logic to convert history to messages...
        return messages
