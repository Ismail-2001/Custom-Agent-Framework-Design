import logging
from typing import Optional, Dict, Any
from datetime import datetime

class AgentLogger:
    """
    Structured logging for agent execution.
    """
    
    def __init__(self, agent_id: str, log_level: str = "INFO"):
        self.agent_id = agent_id
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Configure logger
        self.logger = logging.getLogger(f"Agent_{agent_id}")
        self.logger.setLevel(getattr(logging, log_level))
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(getattr(logging, log_level))
        formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        
    def log_iteration_start(self, iteration: int, task: str):
        self.logger.info(f"Iteration {iteration} - Task: {task[:50]}...")
        
    def log_thought(self, thought: str, metadata: Optional[Dict] = None):
        self.logger.debug(f"Thought: {thought}")
        
    def log_action(self, action: str, parameters: Dict, metadata: Optional[Dict] = None):
        self.logger.info(f"Action: {action} | Params: {parameters}")
        
    def log_tool_call(self, tool: str, input: Dict, output: Any, duration: float):
        self.logger.info(f"Tool: {tool} | Duration: {duration:.2f}s | Output: {str(output)[:100]}")
        
    def log_error(self, error: Exception, context: Dict, recoverable: bool = True):
        level = logging.WARNING if recoverable else logging.ERROR
        self.logger.log(level, f"Error: {error} | Context: {context}")
        
    def log_state_transition(self, from_state: str, to_state: str, reason: str):
        self.logger.info(f"State: {from_state} → {to_state} | Reason: {reason}")
