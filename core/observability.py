import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

class ExecutionTracer:
    """
    Records detailed traces of agent execution for audit and debugging.
    """
    def __init__(self, log_dir: str = "logs/traces"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.current_trace: List[Dict] = []
        self.run_id: str = ""
        
    def start_trace(self, task: str):
        self.run_id = f"trace_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        self.current_trace = [{
            "timestamp": datetime.now().isoformat(),
            "event": "start",
            "task": task
        }]
        
    def log_event(self, event_type: str, data: Any):
        self.current_trace.append({
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            "data": data
        })
        
    def end_trace(self, final_result: Any):
        self.current_trace.append({
            "timestamp": datetime.now().isoformat(),
            "event": "end",
            "result": final_result
        })
        
        filepath = os.path.join(self.log_dir, f"{self.run_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.current_trace, f, indent=2)
        return filepath

class Debugger:
    """
    Analyzes traces to identify bottlenecks or failures.
    """
    @staticmethod
    def analyze_trace(filepath: str) -> Dict[str, Any]:
        with open(filepath, "r", encoding="utf-8") as f:
            trace = json.load(f)
            
        stats = {
            "total_steps": len(trace),
            "actions": 0,
            "errors": 0,
            "duration": 0
        }
        
        # Simple analysis logic
        for event in trace:
            if event["event"] == "action": stats["actions"] += 1
            if "error" in str(event.get("data", "")).lower(): stats["errors"] += 1
            
        return stats
