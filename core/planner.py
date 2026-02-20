from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from llm.provider import LLMProvider, Message
from llm.parser import ResponseParser

class PlanStep(BaseModel):
    id: int
    task: str
    tool: Optional[str] = None
    dependencies: List[int] = []

class Plan(BaseModel):
    steps: List[PlanStep]

class TaskPlanner:
    """
    Decomposes complex tasks into actionable steps.
    """
    def __init__(self, llm: LLMProvider):
        self.llm = llm
        self.parser = ResponseParser()
        
    async def create_plan(self, task: str, context: Optional[Dict] = None) -> Plan:
        prompt = f"Decompose the following task into steps. Task: {task}. Context: {context}\nOutput valid JSON with format: {{'steps': [{{'id': 1, 'task': '...', 'tool': '...', 'dependencies': []}}]}}"
        
        response = await self.llm.generate([Message(role="user", content=prompt)])
        plan_data = self.parser.extract_json(response.content)
        
        steps = [PlanStep(**step) for step in plan_data.get("steps", [])]
        return Plan(steps=steps)

    async def replan(self, current_plan: Plan, execution_result: Any, feedback: str = "") -> Plan:
        """
        Update plan based on execution results or feedback.
        """
        # Convert current plan to string summary
        plan_summary = "\n".join([f"{s.id}. {s.task} (Status: {'Done' if s.id < 0 else 'Pending'})" for s in current_plan.steps])
        
        prompt = f"""
Execution Update:
{execution_result}

Feedback:
{feedback}

Current Plan:
{plan_summary}

Please update the plan to address the feedback or failure. Remove completed steps and add necessary new steps.
Output valid JSON with format: {{'steps': [{{'id': 1, 'task': '...', 'tool': '...', 'dependencies': []}}]}}
"""
        response = await self.llm.generate([Message(role="user", content=prompt)])
        plan_data = self.parser.extract_json(response.content)
        
        steps = [PlanStep(**step) for step in plan_data.get("steps", [])]
        return Plan(steps=steps)
