import time
from functools import wraps
from typing import Callable
import asyncio
from datetime import datetime, timedelta
from config.settings import RETRY_ATTEMPTS, RETRY_DELAY
import queue

class RateLimiter:
    def __init__(self, requests_per_minute):
        self.requests_per_minute = requests_per_minute
        self.requests = queue.Queue(maxsize=requests_per_minute)
        self.window_size = 60

    def acquire(self):
        now = datetime.now()

        # Remove old timestamps
        while not self.requests.empty():
            timestamp = self.requests.queue[0]
            if now - timestamp > timedelta(seconds=self.window_size):
                self.requests.get()
            else:
                break
        
        # If we've hit the limit, wait
        if self.requests.full():
            oldest = self.requests.queue[0]
            sleep_time = (oldest + timedelta(seconds=self.window_size) - now).total_seconds()
            if sleep_time > 0:
                time.sleep(sleep_time)

        # Add current request
        self.requests.put(now)

def rate_limit(func: Callable):
    """Decorator to apply rate limiting to a function"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        max_retries = RETRY_ATTEMPTS
        retry_delay = RETRY_DELAY

        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    print(f"Rate limit hit, waiting {retry_delay} seconds...")
                    time.sleep(retry_delay * (attempt+1)) # Exponential backoff
                    continue
                raise
    return wrapper