import typing
import time

##--------------------start-of-permission_error_decorator------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def permission_error_decorator() -> typing.Callable:

    """
    
    Returns a decorator that will catch a PermissionError and keep trying until the file is no longer in use.

    """

    def decorator(func):
        def wrapper(*args, **kwargs):

            while True:
                try:
                    return func(*args, **kwargs)

                except PermissionError:
                    time.sleep(0.1)
                
        return wrapper
    return decorator