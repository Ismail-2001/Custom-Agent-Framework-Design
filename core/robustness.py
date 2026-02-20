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
        max_retries: int = 5,
        base_delay: float = 1.0,
        *args,
        **kwargs
    ) -> Tuple[bool, Any]:
        """
        Execute function with exponential backoff retry.
        Handles rate limits specifically.
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                result = await func(*args, **kwargs)
                return True, result
            except Exception as e:
                last_error = e
                # Check for rate limit indicators in various provider exceptions
                error_str = str(e).lower()
                is_rate_limit = any(x in error_str for x in ["rate_limit", "429", "too many requests"])
                
                if is_rate_limit:
                    # Often APIs provide a "retry-after" in some form, 
                    # for now we'll just use a more aggressive backoff for 429s
                    wait_time = base_delay * (5 ** attempt) # Slower backoff for rate limits
                else:
                    wait_time = base_delay * (2 ** attempt)
                
                logging.warning(f"Attempt {attempt + 1} failed ({'Rate Limit' if is_rate_limit else 'Error'}): {e}. Retrying in {wait_time}s...")
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
