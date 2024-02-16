## third-party libraries

## for importing, other scripts will use from common.exceptions instead of from the third-party libraries themselves
from openai import AuthenticationError, InternalServerError, RateLimitError, APIError, APIConnectionError, APITimeoutError

##-------------------start-of-MaxBatchDurationExceededException--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class MaxBatchDurationExceededException(Exception):

    """

    MaxBatchDurationExceededException is an exception that is raised when the max batch duration is exceeded.

    """

    pass