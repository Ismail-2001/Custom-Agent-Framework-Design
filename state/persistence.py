import json
import sqlite3
from typing import Dict, Any, Optional
from datetime import datetime
from state.manager import AgentState

class StatePersistence:
    """
    State persistence layer with multiple backend support.
    """
    
    def __init__(self, backend: str = "sqlite", db_path: str = "agent_state.db"):
        self.backend = backend
        self.db_path = db_path
        if backend == "sqlite":
            self._init_sqlite()
            
    def _init_sqlite(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS checkpoints (
                    checkpoint_id TEXT PRIMARY KEY,
                    task TEXT,
                    label TEXT,
                    state_data TEXT,
                    status TEXT,
                    timestamp DATETIME DEFAULT (STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'))
                )
            """)
            
    async def save(self, state: AgentState, label: Optional[str] = None) -> str:
        """Save state and return checkpoint ID."""
        checkpoint_id = f"{state.task[:20]}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        if label:
            checkpoint_id = f"{label}_{checkpoint_id}"
            
        # Pydantic's model_dump_json handles datetime serialization to ISO strings
        state_json = state.model_dump_json()
        
        if self.backend == "sqlite":
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO checkpoints (checkpoint_id, task, label, state_data, status) VALUES (?, ?, ?, ?, ?)",
                    (checkpoint_id, state.task, label or "", state_json, state.status.value)
                )
        elif self.backend == "json":
            with open(f"{checkpoint_id}.json", "w") as f:
                f.write(state_json)
                
        return checkpoint_id
        
    async def load(self, checkpoint_id: str) -> Optional[AgentState]:
        """Load state from checkpoint."""
        if self.backend == "sqlite":
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT state_data FROM checkpoints WHERE checkpoint_id = ?",
                    (checkpoint_id,)
                )
                row = cursor.fetchone()
                if row:
                    state_dict = json.loads(row[0])
                    return AgentState(**state_dict)
        elif self.backend == "json":
            try:
                with open(f"{checkpoint_id}.json", "r") as f:
                    state_dict = json.load(f)
                    return AgentState(**state_dict)
            except FileNotFoundError:
                pass
                
        return None
        
    async def list_checkpoints(self, task_id: Optional[str] = None, limit: int = 10) -> list:
        """List available checkpoints."""
        if self.backend == "sqlite":
            with sqlite3.connect(self.db_path) as conn:
                if task_id:
                    cursor = conn.execute(
                        "SELECT checkpoint_id, task, status, timestamp, label FROM checkpoints WHERE task LIKE ? ORDER BY timestamp DESC LIMIT ?",
                        (f"%{task_id}%", limit)
                    )
                else:
                    cursor = conn.execute(
                        "SELECT checkpoint_id, task, status, timestamp, label FROM checkpoints ORDER BY timestamp DESC LIMIT ?",
                        (limit,)
                    )
                return [
                    {
                        "checkpoint_id": row[0], 
                        "task": row[1], 
                        "status": row[2], 
                        "timestamp": row[3],
                        "label": row[4]
                    }
                    for row in cursor.fetchall()
                ]
        return []
