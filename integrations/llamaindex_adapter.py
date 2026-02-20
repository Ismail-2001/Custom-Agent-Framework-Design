from typing import Any, List, Dict
from tools.base import Tool
from memory.vector_store import VectorStoreMemory

# Try to import LlamaIndex components
try:
    from llama_index.core.tools import FunctionTool
    from llama_index.core.base.base_query_engine import BaseQueryEngine
except ImportError:
    FunctionTool = object
    BaseQueryEngine = object

class LlamaIndexAdapter:
    """
    Integrate with LlamaIndex.
    """
    
    @staticmethod
    def query_engine_to_tool(
        query_engine: Any,
        name: str,
        description: str
    ) -> Tool:
        """Convert LlamaIndex query engine to tool."""
        
        class LlamaIndexTool(Tool):
            async def _run(self, query: str):
                if hasattr(query_engine, "aquery"):
                    response = await query_engine.aquery(query)
                else:
                    response = query_engine.query(query)
                return str(response)
                
        return LlamaIndexTool(
            name=name,
            description=description,
            parameters={
                "type": "object", 
                "properties": {
                    "query": {"type": "string", "description": "The search query"}
                },
                "required": ["query"]
            }
        )
