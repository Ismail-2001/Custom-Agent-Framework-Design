from typing import Dict, List, Optional
from datetime import datetime
from state.manager import AgentState

class VersionInfo:
    def __init__(self, version: int, state: AgentState, message: str = ""):
        self.version = version
        self.state = state
        self.message = message
        self.timestamp = datetime.now()

class StateVersioning:
    """
    State version control system.
    """
    
    def __init__(self):
        self.versions: Dict[int, VersionInfo] = {}
        self.current_version: int = 0
        
    def commit(self, state: AgentState, message: str = "") -> int:
        """Save new version."""
        self.current_version += 1
        self.versions[self.current_version] = VersionInfo(
            self.current_version,
            state,
            message
        )
        return self.current_version
        
    def rollback(self, version: int) -> Optional[AgentState]:
        """Restore previous version."""
        if version in self.versions:
            self.current_version = version
            return self.versions[version].state
        return None
        
    def get_history(self, limit: int = 10) -> List[Dict]:
        """Get version history."""
        versions = sorted(self.versions.values(), key=lambda v: v.version, reverse=True)
        return [
            {
                "version": v.version,
                "message": v.message,
                "timestamp": v.timestamp.isoformat(),
                "status": v.state.status.value
            }
            for v in versions[:limit]
        ]
