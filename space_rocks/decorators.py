import functools
import time


def slow_down(_func=None, *, rate=1):
    def decorator_slow_down(func):
        @functools.wraps(func)
        def wrapper_slow_down(*args, **kwargs):
            wrapper_slow_down.num_calls += 1
            if wrapper_slow_down.num_calls == rate:
                wrapper_slow_down.num_calls = 0
                return func(*args, **kwargs)

        wrapper_slow_down.num_calls = 0
        return wrapper_slow_down

    if _func is None:
        return decorator_slow_down
    else:
        return decorator_slow_down(_func)


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
