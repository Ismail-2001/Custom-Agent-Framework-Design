from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class AgentState(BaseModel):
    task: str
    status: TaskStatus = TaskStatus.PENDING
    history: List[Dict[str, Any]] = Field(default_factory=list)
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None

class StateManager:
    """
    Manages the current state of an agent execution with checkpoint support.
    """
    def __init__(self, task: str, persistence = None):
        self.state = AgentState(task=task)
        self.persistence = persistence
        
    def add_history(self, event_type: str, data: Any):
        self.state.history.append({
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            "data": data
        })
        
    def update_status(self, status: TaskStatus):
        self.state.status = status
        if status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            self.state.end_time = datetime.now()
            
    def get_state(self) -> AgentState:
        return self.state
        
    async def checkpoint(self, label: str = None) -> str:
        """Save current state as checkpoint."""
        if self.persistence:
            return await self.persistence.save(self.state, label)
        return ""
        
    async def restore(self, checkpoint_id: str) -> bool:
        """Restore state from checkpoint."""
        if self.persistence:
            restored_state = await self.persistence.load(checkpoint_id)
            if restored_state:
                self.state = restored_state
                return True
        return False
