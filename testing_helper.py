from time import monotonic


def record_time(function):
    def wrap(*args, **kwargs):
        start_time = monotonic()
        function_return = function(*args, **kwargs)
        print(f"Run time {monotonic() - start_time} seconds")
        return function_return

    return wrap
