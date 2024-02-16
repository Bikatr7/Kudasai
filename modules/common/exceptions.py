## third-party libraries
from openai import AuthenticationError, InternalServerError, RateLimitError, APIError, APIConnectionError, APITimeoutError

##-------------------start-of-MaxBatchDurationExceeded--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class MaxBatchDurationExceeded(Exception):

    """

    MaxBatchDurationExceeded is an exception that is raised when the max batch duration is exceeded.

    """

    pass