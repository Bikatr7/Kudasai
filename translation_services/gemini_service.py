## built-in libraries
import typing

## third party libraries
## pip install -q -U google-generativeai
from google.generativeai import GenerationConfig
import google.generativeai as genai

## custom modules
from modules.common.exceptions import InvalidAPIKeyException
from modules.common.decorators import do_nothing_decorator

class GeminiService:

    model:str = "gemini-pro"
    prompt:str
    temperature:float
    top_p:float
    top_k:int
    candidate_count:int
    stream:bool
    stop_sequences:typing.List[str] | None
    max_output_tokens:int | None = None

    client:genai.GenerativeModel
    generation_config:GenerationConfig

    decorator_to_use:typing.Callable = do_nothing_decorator

##-------------------start-of-set_api_key()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def set_api_key(api_key:str) -> None:

        """

        Sets the API key for the Gemini client.

        Parameters:
        api_key (string) : The API key to set.

        """

        genai.configure(api_key=api_key)

##-------------------start-of-set_decorator()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def set_decorator(decorator:typing.Callable) -> None:

        """

        Sets the decorator to use for the Gemini service. Should be a callable that returns a decorator.

        Parameters:
        decorator (callable) : The decorator to use.

        """

        GeminiService.decorator_to_use = decorator

##-------------------start-of-setup_client()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def setup_client() -> None:

        """

        Sets up the Gemini client.

        """

        GeminiService.client = genai.GenerativeModel(GeminiService.model)
        GeminiService.generation_config = GenerationConfig(candidate_count=GeminiService.candidate_count,
                                                           max_output_tokens=GeminiService.max_output_tokens,
                                                           stop_sequences=GeminiService.stop_sequences,
                                                            temperature=GeminiService.temperature,
                                                            top_p=GeminiService.top_p,
                                                            top_k=GeminiService.top_k)

##-------------------start-of-trans()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    async def translate_message(translation_prompt:str) -> str:

        """

        Translates a prompt.

        Parameters:
        translation_prompt (object - ModelTranslationMessage) : The prompt to translate.

        Returns:
        output (string) : The translation.

        """

        decorated_function = GeminiService.decorator_to_use(GeminiService._translate_message)
        return await decorated_function(translation_prompt)

##-------------------start-of-_translate_message()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    async def _translate_message(translation_prompt:str) -> str:

        """

        Translates a prompt.

        Parameters:
        translation_prompt (string) : The prompt to translate.

        Returns:
        output (string) a string that gpt gives to us also known as the translation.

        """

        response = await GeminiService.client.generate_content_async(
            contents=translation_prompt,
            stream = GeminiService.stream,
            GenerationConfig = GeminiService.generation_config

        )

        output = response.text
        
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

            generation_config = GenerationConfig(candidate_count=1, max_output_tokens=1)

            await GeminiService.client.generate_content_async(
                "Respond to this prompt with 1",generation_config=generation_config

            )

            validity = True

            return validity, None

        except Exception as e:

            return validity, e
        
##-------------------start-of-get_decorator()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def get_decorator() -> typing.Callable:

        """

        Returns the decorator to use for the Gemini service.

        Returns:
        decorator (callable) : The decorator to use.

        """

        return GeminiService.decorator_to_use
    
old="""

    model = genai.GenerativeModel('gemini-nano')

    generation_config = GenerationConfig(candidate_count=1, max_output_tokens=5)

    api_key = input("Enter your API key: ")
    genai.configure(api_key=api_key)

    response = await model.generate_content_async("Respond to this prompt with 1.", generation_config=generation_config)

    print(response.text)
"""