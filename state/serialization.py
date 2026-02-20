import json
from typing import Any
from state.manager import AgentState

class StateSerializer:
    """
    State serialization/deserialization.
    """
    
    def serialize(self, state: AgentState, format: str = "json") -> bytes:
        """Convert state to bytes."""
        if format == "json":
            return json.dumps(state.model_dump(), indent=2).encode('utf-8')
        else:
            raise ValueError(f"Unsupported format: {format}")
            
    def deserialize(self, data: bytes, format: str = "json") -> AgentState:
        """Reconstruct state from bytes."""
        if format == "json":
            state_dict = json.loads(data.decode('utf-8'))
            return AgentState(**state_dict)
        else:
            raise ValueError(f"Unsupported format: {format}")
