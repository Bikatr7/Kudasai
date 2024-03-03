## build-in libraries
import typing
import time

## custom modules
from modules.common.exceptions import TooManyFileAccessAttemptsException

##--------------------start-of-permission_error_decorator------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def permission_error_decorator() -> typing.Callable:

    """
    
    Returns a decorator that will catch a PermissionError and keep trying until the file is no longer in use.
    Timeout is set to 100 retries or 20 seconds.
    Mostly done because my computer has this weird issue, likely won't be noticed by anyone else.

    """

    def decorator(func):

        max_retries = 100

        def wrapper(*args, **kwargs):
            retries = 0
            while(retries < max_retries):
                try:
                    return func(*args, **kwargs)
                except PermissionError:
                    retries += 1
                    time.sleep(0.2)  

            raise TooManyFileAccessAttemptsException(f"Failed to execute {func.__name__} after {max_retries} retries.")
        
        return wrapper
    return decorator