import sqlite3
import json
from typing import Any, List, Dict, Optional
from datetime import datetime
from .base import BaseMemory

class Episode(BaseMemory):
    """
    Experience replay system for learning from past actions.
    """
    
    def __init__(self, db_path: str = "agent_memory.db"):
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS episodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task TEXT,
                    steps TEXT,
                    success BOOLEAN,
                    final_answer TEXT,
                    duration REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
    async def store_episode(
        self,
        task: str,
        steps: List[Dict],
        success: bool,
        final_answer: str,
        duration: float
    ) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO episodes (task, steps, success, final_answer, duration) VALUES (?, ?, ?, ?, ?)",
                (task, json.dumps(steps), success, final_answer, duration)
            )
            return cursor.lastrowid
            
    async def store(self, key: str, value: Any, metadata: Optional[Dict] = None) -> None:
        # Generic store if needed
        pass

    async def retrieve(self, query: str, k: int = 5) -> List[Dict]:
        """Find episodes by task similarity (basic keyword search)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT task, steps, success, final_answer FROM episodes WHERE task LIKE ? ORDER BY timestamp DESC LIMIT ?",
                (f"%{query}%", k)
            )
            return [
                {
                    "task": row[0],
                    "steps": json.loads(row[1]),
                    "success": bool(row[2]),
                    "final_answer": row[3]
                }
                for row in cursor.fetchall()
            ]

    async def clear(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM episodes")
