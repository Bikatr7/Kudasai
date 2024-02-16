## built-in libraries
import typing

## third-party libraries
import backoff

from openai import AsyncOpenAI

## custom modules
from modules.common.exceptions import AuthenticationError, InternalServerError, RateLimitError, APIError, APIConnectionError, APITimeoutError, InvalidAPIKeyException, MaxBatchDurationExceededException
from modules.common.logger import Logger

from custom_classes.messages import SystemTranslationMessage, ModelTranslationMessage

class OpenAIService:

    ## async client session
    client = AsyncOpenAI(max_retries=0, api_key="DummyKey")

    max_batch_duration:float
    model:str
    temperature:float
    top_p:float
    n:int
    stream:bool
    stop:typing.List[str] | None
    presence_penalty:float
    frequency_penalty:float
    max_tokens:int

##-------------------start-of-set_api_key()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def set_api_key(api_key:str) -> None:

        """

        Sets the API key for the OpenAI client.

        Parameters:
        api_key (string) : The API key to set.

        """

        OpenAIService.client.api_key = api_key

##-------------------start-of-translate_message()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    ## backoff wrapper for retrying on errors, As of OpenAI > 1.0.0, it comes with a built in backoff system, but I've grown accustomed to this one so I'm keeping it.
    @staticmethod
    @backoff.on_exception(backoff.expo, max_time=lambda: OpenAIService.get_max_batch_duration(), exception=(AuthenticationError, InternalServerError, RateLimitError, APIError, APIConnectionError, APITimeoutError), on_backoff=lambda details: OpenAIService.log_retry(details), on_giveup=lambda details: OpenAIService.log_failure(details), raise_on_giveup=False)
    async def translate_message(translation_instructions:SystemTranslationMessage | ModelTranslationMessage, translation_prompt:ModelTranslationMessage) -> str:

        """

        Translates a system and user message.

        Parameters:
        translation_instructions (object - SystemTranslationMessage | ModelTranslationMessage) : The system message also known as the instructions.
        translation_prompt (object - ModelTranslationMessage) : The user message also known as the prompt.

        Returns:
        output (string) a string that gpt gives to us also known as the translation.

        """

        if(OpenAIService.client.api_key == "DummyKey"):
            raise InvalidAPIKeyException("OpenAI")

        ## logit bias is currently excluded due to a lack of need, and the fact that i am lazy

        response = await OpenAIService.client.chat.completions.create(
            model=OpenAIService.model,
            messages=[
                translation_instructions,
                translation_prompt,
            ], # type: ignore | Seems to work for now.

            temperature = OpenAIService.temperature,
            top_p = OpenAIService.top_p,
            n = OpenAIService.n,
            stream = OpenAIService.stream,
            stop = OpenAIService.stop,
            presence_penalty = OpenAIService.presence_penalty,
            frequency_penalty = OpenAIService.frequency_penalty,
            ##max_tokens = OpenAIService.max_tokens       

        )

        ## if anyone knows how to type hint this please let me know
        output = response.choices[0].message.content
        
        return output
    
##-------------------start-of-test_api_key_validity()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    async def test_api_key_validity() -> typing.Tuple[bool, typing.Union[Exception, None]]:

        """

        Tests the validity of the API key.

        Returns:
        validity (bool) : True if the API key is valid, False if it is not.
        e (Exception) : The exception that was raised, if any.

        """

        validity = False

        try:

            await OpenAIService.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role":"user","content":"This is a test."}],
                max_tokens=1
            )

            validity = True

            return validity, None

        except Exception as e:

            return validity, e
    
##-------------------start-of-get_max_batch_duration()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def get_max_batch_duration() -> float:

        """
        
        Returns the max batch duration.
        Structured as a function so that it can be used as a lambda function in the backoff decorator. As decorators call the function when they are defined/runtime, not when they are called.

        Returns:
        max_batch_duration (float) : the max batch duration.

        """

        return OpenAIService.max_batch_duration
    
##-------------------start-of-log_retry()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def log_retry(details) -> None:

        """

        Logs the retry message.

        Parameters:
        details (dict) : the details of the retry.

        """

        retry_msg = f"Retrying translation after {details['wait']} seconds after {details['tries']} tries {details['target']} due to {details['exception']}."

        Logger.log_barrier()
        Logger.log_action(retry_msg)
        Logger.log_barrier()

##-------------------start-of-log_failure()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def log_failure(details) -> None:

        """
        
        Logs the translation batch failure message.

        Parameters:
        details (dict) : the details of the failure.

        """

        error_msg = f"Exceeded duration, returning untranslated text after {details['tries']} tries {details['target']}."

        Logger.log_barrier()
        Logger.log_error(error_msg)
        Logger.log_barrier()

        raise MaxBatchDurationExceededException(error_msg)