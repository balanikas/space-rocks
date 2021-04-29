import functools
import time


def slow_down(_func=None, *, rate=1):
    """Sleep given amount of seconds before calling the function"""

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
    if not func.__name__ in func_timings:
        func_timings[func.__name__] = 0
    return func


def timer(func):
    """Print the runtime of the decorated function"""

    register(func)

    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()  # 1
        value = func(*args, **kwargs)
        end_time = time.perf_counter()  # 2
        run_time = end_time - start_time  # 3
        # print(f"Finished {func.__name__!r} in {run_time*1000:.4f} ms")
        func_timings[func.__name__] = (
            func_timings[func.__name__] + run_time * 1000
        ) / 2
        return value

    return wrapper_timer
