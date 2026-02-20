from typing import List, Dict, Any, Optional, Tuple
from tools.base import Tool
from llm.provider import LLMProvider, Message
from state.manager import AgentState

class DecisionMaker:
    """
    Selects optimal actions based on context and available tools.
    """
    def __init__(self, llm: LLMProvider):
        self.llm = llm
        
    async def select_action(
        self,
        observation: str,
        tools: List[Tool],
        state: AgentState
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        In a simplified framework, the Decision Maker might just be part of the ReAct loop.
        In a more advanced one, it evaluates multiple options.
        """
        # For Phase 2, we integrate this logic into the Executor/Agent loop
        pass

    def should_terminate(self, state: AgentState) -> bool:
        """Check termination conditions."""
        if state.history and len(state.history) > 20: # Max iterations safety
            return True
        return False
