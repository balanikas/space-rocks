import functools
import time
from typing import Dict, Callable, Any

func_timings: Dict[str, float] = {}


def register(func: Callable[[Any], Any]):
    if func.__name__ not in func_timings:
        func_timings[func.__name__] = 0
    return func


def timer(func: Callable[..., Any]):
    register(func)

    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        func_timings[func.__name__] = (
            func_timings[func.__name__] + run_time * 1000
        ) / 2
        return value

    return wrapper_timer
