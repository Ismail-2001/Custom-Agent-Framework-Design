import sqlite3
import json
from typing import Any, List, Dict, Optional
from .base import BaseMemory

class LongTermMemory(BaseMemory):
    """
    Persistent key-value store using SQLite.
    """
    
    def __init__(self, db_path: str = "agent_memory.db"):
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS facts (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    metadata TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS experiences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task TEXT,
                    outcome TEXT,
                    details TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
    async def store(self, key: str, value: Any, metadata: Optional[Dict] = None) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO facts (key, value, metadata) VALUES (?, ?, ?)",
                (key, json.dumps(value), json.dumps(metadata or {}))
            )
            
    async def retrieve(self, query: str, k: int = 5) -> List[Dict]:
        """Simple prefix/exact match retrieval for key-value facts."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT key, value, metadata FROM facts WHERE key LIKE ? LIMIT ?",
                (f"%{query}%", k)
            )
            return [
                {"key": row[0], "value": json.loads(row[1]), "metadata": json.loads(row[2])}
                for row in cursor.fetchall()
            ]
            
    async def store_experience(self, task: str, outcome: str, details: Dict) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO experiences (task, outcome, details) VALUES (?, ?, ?)",
                (task, outcome, json.dumps(details))
            )
            
    async def clear(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM facts")
            conn.execute("DELETE FROM experiences")
