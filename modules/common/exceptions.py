## third-party libraries

## for importing, other scripts will use from common.exceptions instead of from the third-party libraries themselves
from openai import AuthenticationError, InternalServerError, RateLimitError, APIError, APIConnectionError, APITimeoutError

##-------------------start-of-MaxBatchDurationExceededException--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class MaxBatchDurationExceededException(Exception):

    """

    MaxBatchDurationExceededException is an exception that is raised when the max batch duration is exceeded.

    """

    pass

##-------------------start-of-InvalidAPIKeyException--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class InvalidAPIKeyException(Exception):

    """

    InvalidAPIKeyException is an exception that is raised when the API key is invalid.

    """

    def __init__(self, model_name:str) -> None:

        """

        Parameters:
        model_name (string) : The name of the model that the API key is invalid for.

        """

        self.message = f"The API key is invalid for the model {model_name}."