## third-party libraries
## for importing, other scripts will use from common.exceptions instead of from the third-party libraries themselves
from easytl import AuthenticationError, InternalServerError, RateLimitError, APITimeoutError, APIConnectionError, APIStatusError
from easytl import AuthorizationException, QuotaExceededException
from easytl import GoogleAuthError

##-------------------start-of-MaxBatchDurationExceededException--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class MaxBatchDurationExceededException(Exception):

    """

    MaxBatchDurationExceededException is an exception that is raised when the max batch duration is exceeded.

    """

    def __init__(self, message:str) -> None:

        """

        Parameters:
        message (string) : The message to display.

        """

        self.message = message

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

##-------------------start-of-TooManyFileAccessAttemptsException--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class TooManyFileAccessAttemptsException(Exception):

    """

    TooManyFileAccessAttemptsException is an exception that is raised when too many attempts are made to access a file.

    """

    def __init__(self, message:str) -> None:

        """

        Parameters:
        message (string) : The message to display.

        """

        self.message = message