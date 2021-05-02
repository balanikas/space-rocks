import functools
import time
from typing import Callable

func_timings = {}


def register(func):
    if func.__name__ not in func_timings:
        func_timings[func.__name__] = 0
    return func


def timer(func):
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
