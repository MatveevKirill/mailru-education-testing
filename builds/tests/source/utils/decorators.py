import time

from selenium.common.exceptions import TimeoutException


def wait(
    _method,
    _error=TimeoutException,
    _timeout: float = 7.0,
    _check: bool = False,
    _interval: float = 0.5,
    **kwargs
):
    start_time = time.time()
    last_exception = None
    while time.time() - start_time < _timeout:
        try:
            result = _method(**kwargs)
            if _check:
                if result:
                    return result
                last_exception = f'Method {_method.__name__} returned {result}'
            else:
                return result
        except _error as e:
            last_exception = e
        time.sleep(_interval)

    raise TimeoutError(f"Method '{_method.__name__}' timeout in {_timeout}sec with exception '{last_exception}'.")
