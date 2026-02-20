import json
import time
from typing import List, Dict, Any, Optional
from llm.provider import LLMProvider, Message
from tools.base import Tool
from tools.executor import ToolExecutor
from memory.short_term import ShortTermMemory
from state.manager import StateManager, TaskStatus

from core.executor import AgentExecutor
from core.observability import ExecutionTracer

class Agent:
    def __init__(
        self,
        llm: LLMProvider,
        tools: List[Tool],
        memory: Optional[MemoryManager] = None,
        enable_tracing: bool = True
    ):
        self.llm = llm
        self.tools = tools
        self.executor = AgentExecutor(llm, tools)
        self.memory = memory or MemoryManager()
        self.state_manager: Optional[StateManager] = None
        self.tracer = ExecutionTracer() if enable_tracing else None
        
    async def run(self, task: str, pattern: str = "react", **kwargs) -> Dict[str, Any]:
        """
        Run the agent on a specific task.
        """
        self.state_manager = StateManager(task=task)
        self.state_manager.update_status(TaskStatus.RUNNING)
        
        await self.memory.remember(task, role="user")
        
        if self.tracer:
            self.tracer.start_trace(task)
            
        start_time = time.time()
        if pattern == "react":
            result = await self.executor.execute_react_loop(task, self.state_manager, **kwargs)
        else:
            result = {"error": f"Pattern {pattern} not implemented"}
            
        duration = time.time() - start_time
            
        if self.tracer:
            self.tracer.end_trace(result)
            
        if "output" in result:
            await self.memory.remember(result["output"], role="assistant")
            # Store episode
            await self.memory.add_episode(
                task=task,
                steps=self.state_manager.get_state().history,
                success=self.state_manager.get_state().status == TaskStatus.COMPLETED,
                final_answer=result.get("output", ""),
                duration=duration
            )
            
        return {
            **result,
            "state": self.state_manager.get_state().model_dump()
        }
