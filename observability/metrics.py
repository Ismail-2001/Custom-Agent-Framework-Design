from typing import Dict, Any, List
from datetime import datetime

class MetricsCollector:
    """
    Collect and aggregate performance metrics.
    """
    
    def __init__(self):
        self.metrics: List[Dict[str, Any]] = []
        
    def record_iteration(self, duration: float, tokens_used: int, tools_called: int):
        self.metrics.append({
            "type": "iteration",
            "timestamp": datetime.now().isoformat(),
            "duration": duration,
            "tokens_used": tokens_used,
            "tools_called": tools_called
        })
        
    def record_tool_call(self, tool_name: str, duration: float, success: bool, cost: float = None):
        self.metrics.append({
            "type": "tool_call",
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "duration": duration,
            "success": success,
            "cost": cost
        })
        
    def record_task_completion(self, success: bool, total_duration: float, iterations: int, total_cost: float):
        self.metrics.append({
            "type": "task_completion",
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "total_duration": total_duration,
            "iterations": iterations,
            "total_cost": total_cost
        })
        
    def get_metrics(self, metric_type: str = None) -> List[Dict]:
        if metric_type:
            return [m for m in self.metrics if m["type"] == metric_type]
        return self.metrics
        
    def get_summary(self) -> Dict[str, Any]:
        total_iterations = len([m for m in self.metrics if m["type"] == "iteration"])
        successful_tasks = len([m for m in self.metrics if m["type"] == "task_completion" and m["success"]])
        
        return {
            "total_iterations": total_iterations,
            "successful_tasks": successful_tasks,
            "total_metrics": len(self.metrics)
        }
