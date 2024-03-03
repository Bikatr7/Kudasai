## built-in libraries
import typing

## third-party libraries
from openai import AsyncOpenAI

## custom modules
from modules.common.exceptions import InvalidAPIKeyException
from custom_classes.messages import SystemTranslationMessage, Message

class OpenAIService:

    ## async client session
    client = AsyncOpenAI(max_retries=0, api_key="DummyKey")

    model:str
    system_message:typing.Optional[typing.Union[SystemTranslationMessage, str]] = None
    temperature:float
    top_p:float
    n:int
    stream:bool
    stop:typing.List[str] | None
    logit_bias:typing.Dict[str, float] | None
    max_tokens:int | None
    presence_penalty:float
    frequency_penalty:float

    decorator_to_use:typing.Union[typing.Callable, None] = None

##-------------------start-of-set_api_key()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def set_api_key(api_key:str) -> None:

        """

        Sets the API key for the OpenAI client.

        Parameters:
        api_key (string) : The API key to set.

        """

        OpenAIService.client.api_key = api_key

##-------------------start-of-set_decorator()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def set_decorator(decorator:typing.Callable) -> None:

        """

        Sets the decorator to use for the OpenAI service. Should be a callable that returns a decorator.

        Parameters:
        decorator (callable) : The decorator to use.

        """

        OpenAIService.decorator_to_use = decorator

##-------------------start-of-trans()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    async def translate_message(translation_instructions:Message, translation_prompt:Message) -> str:

        """
        
        Translates a system and user message.

        Parameters:
        translation_instructions (object - SystemTranslationMessage | ModelTranslationMessage) : The system message also known as the instructions.
        translation_prompt (object - ModelTranslationMessage) : The user message also known as the prompt.

        Returns:
        output (string) a string that gpt gives to us also known as the translation.

        """

        if(OpenAIService.decorator_to_use == None):
            return await OpenAIService._translate_message(translation_instructions, translation_prompt)

        decorated_function = OpenAIService.decorator_to_use(OpenAIService._translate_message)
        return await decorated_function(translation_instructions, translation_prompt)

##-------------------start-of-_translate_message()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    ## backoff wrapper for retrying on errors, As of OpenAI > 1.0.0, it comes with a built in backoff system, but I've grown accustomed to this one so I'm keeping it.
    @staticmethod
    async def _translate_message(translation_instructions:Message, translation_prompt:Message) -> str:

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
                translation_instructions.to_dict(),
                translation_prompt.to_dict()
            ],  # type: ignore

            temperature = OpenAIService.temperature,
            top_p = OpenAIService.top_p,
            n = OpenAIService.n,
            stream = OpenAIService.stream,
            stop = OpenAIService.stop,
            presence_penalty = OpenAIService.presence_penalty,
            frequency_penalty = OpenAIService.frequency_penalty,
            max_tokens = OpenAIService.max_tokens       

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
        
##-------------------start-of-get_decorator()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def get_decorator() -> typing.Union[typing.Callable, None]:

        """

        Returns the decorator to use for the OpenAI service.

        Returns:
        decorator (callable) : The decorator to use.

        """

        return OpenAIService.decorator_to_use