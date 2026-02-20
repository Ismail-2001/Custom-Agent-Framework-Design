import json
import re
from typing import Dict, Any, Optional, Tuple
from pydantic import BaseModel

class ReactOutput(BaseModel):
    thought: str
    action: Optional[str] = None
    action_input: Optional[Dict[str, Any]] = None
    final_answer: Optional[str] = None
    is_complete: bool = False

class ResponseParser:
    """
    Parses LLM outputs into structured formats.
    """
    
    def parse_react_response(self, text: str) -> ReactOutput:
        """
        Extract thought, action, and input from ReAct format.
        """
        thought_match = re.search(r"Thought:\s*(.*?)(?:\nAction:|\nFinal Answer:|$)", text, re.DOTALL)
        action_match = re.search(r"Action:\s*(.*)", text)
        action_input_match = re.search(r"Action Input:\s*(.*)", text)
        final_answer_match = re.search(r"Final Answer:\s*(.*)", text, re.DOTALL)
        
        thought = thought_match.group(1).strip() if thought_match else ""
        action = action_match.group(1).strip() if action_match else None
        
        action_input = None
        if action_input_match:
            try:
                action_input = json.loads(action_input_match.group(1).strip())
            except:
                # Fallback: try to find JSON block
                json_match = re.search(r"\{.*\}", action_input_match.group(1).strip())
                if json_match:
                    try:
                        action_input = json.loads(json_match.group(0))
                    except:
                        pass
        
        final_answer = final_answer_match.group(1).strip() if final_answer_match else None
        
        return ReactOutput(
            thought=thought,
            action=action,
            action_input=action_input,
            final_answer=final_answer,
            is_complete=final_answer is not None
        )

    def extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON from text block."""
        try:
            return json.loads(text)
        except:
            json_match = re.search(r"(\{.*\})", text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
        return {}
