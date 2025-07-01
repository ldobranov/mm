import asyncio
import functools
import logging

def retry(times=3, delay=1.0):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(times):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    logging.warning(f"[RETRY] {func.__name__} failed attempt {attempt+1}: {e}")
                    await asyncio.sleep(delay)
            return None
        return wrapper
    return decorator
