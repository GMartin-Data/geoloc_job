"""
This module sums up different utilities used in the whole app.
This includes:
- client configuration and creation
- tool function to get today's date
- timer decorator
"""

from datetime import datetime
import functools
import os
import time

from dotenv import load_dotenv
from httpx import Client


def configure() -> None:
    """Set working environment"""
    load_dotenv()
    conf = dict(
        api_id=os.getenv("ADZUNA_API_ID"),
        api_key=os.getenv("ADZUNA_API_KEY"),
        api_url=os.getenv("ADZUNA_BASE_URL"),
        ua=os.getenv("USER_AGENT"),
    )
    return conf


def create_client(user_agent: str) -> Client:
    """Create and configure a httpx Client for requesting"""
    c = Client()
    c.headers.update({"Content-Type": "application/json", "User-Agent": user_agent})
    return c


def get_date():
    """Help for file horodating"""
    return datetime.now().strftime("%Y-%m-%d")


def timer(func):
    """Print the runtime of the decorated function"""

    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        # Before
        start_time = time.perf_counter()
        # Calling the function and storing value to return
        value = func(*args, **kwargs)
        # After
        end_time = time.perf_counter()
        run_time = end_time - start_time
        print(f"Finished {func.__name__!r} in {run_time: .4f} seconds.")
        return value

    return wrapper_timer
