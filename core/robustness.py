import asyncio
import logging
from typing import Callable, Any, TypeVar, Tuple

T = TypeVar("T")

class ErrorHandler:
    """
    Robust error handling and retry logic.
    """
    
    @staticmethod
    async def retry_with_backoff(
        func: Callable[..., Any],
        max_retries: int = 3,
        base_delay: float = 1.0,
        *args,
        **kwargs
    ) -> Tuple[bool, Any]:
        """
        Execute function with exponential backoff retry.
        Returns (success, result/error).
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                result = await func(*args, **kwargs)
                return True, result
            except Exception as e:
                last_error = e
                wait_time = base_delay * (2 ** attempt)
                logging.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
                
        return False, last_error

    @staticmethod
    def safe_execute(func: Callable[..., Any]):
        """Decorator for safe execution."""
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logging.error(f"Execution failed: {e}")
                return None
        return wrapper
