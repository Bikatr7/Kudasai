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
    prompt:str = ""
    temperature:float = 0.5
    top_p:float = 0.9
    top_k:int = 40
    candidate_count:int = 1
    stream:bool = False
    stop_sequences:typing.List[str] | None = None
    max_output_tokens:int | None = None

    client:genai.GenerativeModel
    generation_config:GenerationConfig

    decorator_to_use:typing.Union[typing.Callable, None] = None

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
    def redefine_client() -> None:

        """

        Redefines the Gemini client and generation config. This should be called before making any requests to the Gemini service, or after changing any of the service's settings.

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
    async def translate_message(translation_instructions:str, translation_prompt:str) -> str:

        """

        Translates a prompt.

        Parameters:
        translation_prompt (object - ModelTranslationMessage) : The prompt to translate.

        Returns:
        output (string) : The translation.

        """

        if(GeminiService.decorator_to_use is None):
            return await GeminiService._translate_message(translation_instructions, translation_prompt)

        decorated_function = GeminiService.decorator_to_use(GeminiService._translate_message(translation_instructions, translation_prompt))
        return await decorated_function()

##-------------------start-of-_translate_message()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    async def _translate_message(translation_instructions:str, translation_prompt:str) -> str:

        """

        Translates a prompt.

        Parameters:
        translation_prompt (string) : The prompt to translate.

        Returns:
        output (string) a string that gpt gives to us also known as the translation.

        """

        response = await GeminiService.client.generate_content_async(
            contents=translation_instructions + "\n" + translation_prompt,
            generation_config=GeminiService.generation_config,  
            stream=GeminiService.stream
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
    def get_decorator() -> typing.Union[typing.Callable, None]:

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