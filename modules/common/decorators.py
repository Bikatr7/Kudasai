## build-in libraries
import typing
import time
import asyncio

## custom modules
from modules.common.exceptions import TooManyFileAccessAttemptsException

##--------------------start-of-permission_error_decorator------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def permission_error_decorator() -> typing.Callable:

    """
    
    Returns a decorator that will catch a PermissionError and keep trying until the file is no longer in use.

    """

    def decorator(func):

        max_retries = 20

        def wrapper(*args, **kwargs):
            retries = 0
            while(retries < max_retries):
                try:
                    return func(*args, **kwargs)
                except PermissionError:
                    retries += 1
                    time.sleep(0.1)  

            raise TooManyFileAccessAttemptsException(f"Failed to execute {func.__name__} after {max_retries} retries.")
        
        return wrapper
    return decorator

##--------------------start-of-do_nothing_decorator------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def do_nothing_decorator(func) -> typing.Callable:

    """
    
    Returns a decorator wrapper that will do nothing.

    """

    if(asyncio.iscoroutinefunction(func)):
        async def wrapper_async(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper_async
    
    else:
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
