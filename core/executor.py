import time
from typing import List, Dict, Any, Optional, Callable
from llm.provider import LLMProvider, Message
from llm.prompt_builder import PromptBuilder
from llm.parser import ResponseParser, ReactOutput
from tools.base import Tool, ToolResult
from tools.executor import ToolExecutor
from core.robustness import ErrorHandler
from state.manager import StateManager, TaskStatus

from core.reflector import Reflector
from core.planner import TaskPlanner, Plan

class AgentExecutor:
    """
    Implements the core agent loop (Observe → Think → Act).
    Supports ReAct, Planning, and Adaptive execution.
    """
    
    def __init__(self, llm: LLMProvider, tools: List[Tool]):
        self.llm = llm
        self.tools = {t.name: t for t in tools}
        self.tool_executor = ToolExecutor()
        self.prompt_builder = PromptBuilder()
        self.parser = ResponseParser()
        self.reflector = Reflector(llm)
        self.planner = TaskPlanner(llm)
        
    async def execute_react_loop(
        self,
        task: str,
        state_manager: StateManager,
        max_iterations: int = 10,
        use_planning: bool = False,
        approval_callback: Optional[Callable[[str, Dict], bool]] = None
    ) -> Dict[str, Any]:
        """
        Main loop implementation with optional adaptive planning.
        """
        scratchpad = ""
        current_plan: Optional[Plan] = None
        
        if use_planning:
            state_manager.add_history("system", "Creating initial plan...")
            current_plan = await self.planner.create_plan(task)
            state_manager.add_history("plan", current_plan.model_dump())
            scratchpad += f"\nCurrent Plan:\n" + "\n".join([f"- {s.task}" for s in current_plan.steps]) + "\n"
        
        for i in range(max_iterations):
            # Build prompt
            prompt = self.prompt_builder.build_react_prompt(task, list(self.tools.values()), scratchpad)
            
            # GENERATE WITH RETRY
            success, response = await ErrorHandler.retry_with_backoff(
                self.llm.generate,
                messages=[Message(role="user", content=prompt)]
            )
            
            if not success:
                 state_manager.update_status(TaskStatus.FAILED)
                 return {"error": f"LLM Generation failed: {response}"}
            
            # PARSE
            parsed: ReactOutput = self.parser.parse_react_response(response.content)
            
            # LOG THOUGHT
            state_manager.add_history("thought", parsed.thought)
            
            # REFLECTION & ADAPTIVE REPLANNING
            if i > 0 and i % 3 == 0:
                critique = await self.reflector.critique(task, state_manager.get_state().history)
                state_manager.add_history("reflection", critique)
                
                reflection_msg = f"Reflection: {critique.get('critique')} Suggestion: {critique.get('suggestion')}"
                scratchpad += f"\n{reflection_msg}\n"
                
                # Trigger replan if not progressing
                if use_planning and not critique.get("is_progressing", True):
                    state_manager.add_history("system", "Progress stalled. Replanning...")
                    current_plan = await self.planner.replan(current_plan, "Stalled progress", critique.get("suggestion"))
                    state_manager.add_history("plan_update", current_plan.model_dump())
                    scratchpad += f"\nUpdated Plan:\n" + "\n".join([f"- {s.task}" for s in current_plan.steps]) + "\n"
                
            if parsed.is_complete:
                state_manager.update_status(TaskStatus.COMPLETED)
                return {"output": parsed.final_answer}
            
            if parsed.action:
                # ACT
                state_manager.add_history("action", {"tool": parsed.action, "input": parsed.action_input})
                
                if parsed.action not in self.tools:
                    observation = f"Error: Tool '{parsed.action}' not found."
                else:
                    tool = self.tools[parsed.action]
                    
                    # HITL: Request approval if needed
                    approved = True
                    if tool.requires_approval:
                        if approval_callback:
                            state_manager.add_history("system", f"Requesting approval for tool: {parsed.action}")
                            approved = await approval_callback(parsed.action, parsed.action_input or {})
                        else:
                            # If no callback provided but approval required, skip/warn
                            approved = False
                            observation = f"Error: Tool '{parsed.action}' requires human approval but no approval mechanism is configured."
                    
                    if approved:
                        tool_result = await self.tool_executor.execute(tool, parsed.action_input or {})
                        observation = str(tool_result.output) if tool_result.success else f"Error: {tool_result.error}"
                    elif not observation: # If manually denied
                        observation = f"User denied execution of tool '{parsed.action}'."
                
                # OBSERVE
                state_manager.add_history("observation", observation)
                
                # Update scratchpad
                scratchpad += f"\nThought: {parsed.thought}\nAction: {parsed.action}\nAction Input: {parsed.action_input}\nObservation: {observation}\n"
            else:
                # LLM didn't provide an action but isn't finished
                scratchpad += f"\nThought: {parsed.thought}\nWait, I need to provide an Action or Final Answer."

        state_manager.update_status(TaskStatus.FAILED)
        return {"error": "Max iterations reached"}
