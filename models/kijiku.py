## built-in libaries
import typing
import base64
import re
import time
import typing
import asyncio
import os

## third party modules
from kairyou import KatakanaUtil

import tiktoken
import backoff

## custom modules
from handlers.json_handler import JsonHandler

from modules.common.file_ensurer import FileEnsurer
from modules.common.logger import Logger
from modules.common.toolkit import Toolkit
from modules.common.exceptions import AuthenticationError, MaxBatchDurationExceededException, AuthenticationError, InternalServerError, RateLimitError, APITimeoutError
from modules.common.decorators import permission_error_decorator

from custom_classes.messages import SystemTranslationMessage, ModelTranslationMessage, Message

from translation_services.openai_service import OpenAIService
from translation_services.gemini_service import GeminiService

##-------------------start-of-Kijiku--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Kijiku:

    """
    
    Kijiku is a secondary class that is used to interact with LLMs and translate text.
    Currently supports OpenAI and Gemini.
    
    """
    
    text_to_translate:typing.List[str] = []

    translated_text:typing.List[str] = []

    je_check_text:typing.List[str] = []

    error_text:typing.List[str] = []

    ## the messages that will be sent to the api, contains a system message and a model message, system message is the instructions,
    ## model message is the text that will be translated  
    openai_translation_batches:typing.List[Message] = []

    ## meanwhile for gemini, we just need to send the prompt and the text to be translated concatenated together
    gemini_translation_batches:typing.List[str] = []

    num_occurred_malformed_batches = 0

    ## semaphore to limit the number of concurrent batches
    _semaphore = asyncio.Semaphore(5)

    ##--------------------------------------------------------------------------------------------------------------------------

    LLM_TYPE:typing.Literal["openai", "gemini"] = "openai"

    translation_print_result = ""

    ##--------------------------------------------------------------------------------------------------------------------------

    prompt_assembly_mode:int
    number_of_lines_per_batch:int
    sentence_fragmenter_mode:int
    je_check_mode:int
    number_of_malformed_batch_retries:int
    batch_retry_timeout:float
    num_concurrent_batches:int

##-------------------start-of-get_max_batch_duration()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def get_max_batch_duration() -> float:

        """
        
        Returns the max batch duration.
        Structured as a function so that it can be used as a lambda function in the backoff decorator. As decorators call the function when they are defined/runtime, not when they are called.

        Returns:
        max_batch_duration (float) : the max batch duration.

        """

        return Kijiku.max_batch_duration
    
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

##-------------------start-of-translate()--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    async def translate() -> None:

        """

        Translate the text in the file at the path given.

        """

        Logger.clear_batch()

        ## set this here cause the try-except could throw before we get past the settings configuration
        time_start = time.time()

        try:
        
            await Kijiku.initialize()

            JsonHandler.validate_json()

            await Kijiku.check_settings()

            ## set actual start time to the end of the settings configuration
            time_start = time.time()

            await Kijiku.commence_translation()

        except Exception as e:
            
            Kijiku.translation_print_result += "An error has occurred, outputting results so far..."

            FileEnsurer.handle_critical_exception(e)

        finally:

            time_end = time.time() 

            Kijiku.assemble_results(time_start, time_end)

##-------------------start-of-initialize()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    async def initialize() -> None:

        """

        Sets the API Key for the respective service and loads the kijiku rules.
    
        """

        print("What LLM do you want to use? (1 for OpenAI or 2 for Gemini) : ")

        if(input("\n") == "1"):
            Kijiku.LLM_TYPE = "openai"
        
        else:
            Kijiku.LLM_TYPE = "gemini"

        Toolkit.clear_console()

        if(Kijiku.LLM_TYPE == "openai"):
            await Kijiku.init_api_key("OpenAI", FileEnsurer.openai_api_key_path, OpenAIService.set_api_key, OpenAIService.test_api_key_validity)

        else:
            await Kijiku.init_api_key("Gemini", FileEnsurer.gemini_api_key_path, GeminiService.set_api_key, GeminiService.test_api_key_validity)

        ## try to load the kijiku rules
        try: 

            JsonHandler.load_kijiku_rules()

        ## if the kijiku rules don't exist, create them
        except: 
            
            JsonHandler.reset_kijiku_rules_to_default()

            JsonHandler.load_kijiku_rules()
            
        Toolkit.clear_console()

##-------------------start-of-init_openai_api_key()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    async def init_api_key(service:str, api_key_path:str, api_key_setter:typing.Callable, api_key_tester:typing.Callable) -> None:

        """

        Sets up the api key for the respective service.

        Parameters:
        service (string) : the name of the service.
        api_key_path (string) : the path to the api key.
        api_key_setter (callable) : the function that sets the api key.
        api_key_tester (callable) : the function that tests the api key.

        """

        if(service != "OpenAI"):
            GeminiService.redefine_client()

        ## get saved API key if exists
        try:
            with open(api_key_path, 'r', encoding='utf-8') as file: 
                api_key = base64.b64decode((file.read()).encode('utf-8')).decode('utf-8')

            api_key_setter(api_key)

            is_valid, e = await api_key_tester()

            ## if not valid, raise the exception that caused the test to fail
            if(not is_valid and e is not None):
                raise e
        
            Logger.log_action("Used saved API key in " + api_key_path, output=True)
            Logger.log_barrier()

            time.sleep(2)

        ## else try to get API key manually
        except:

            Toolkit.clear_console()
                
            api_key = input(f"DO NOT DELETE YOUR COPY OF THE API KEY\n\nPlease enter the {service} API key you have : ")

            ## if valid save the API key
            try: 

                api_key_setter(api_key)

                is_valid, e = await api_key_tester()

                if(not is_valid and e is not None):
                    raise e

                FileEnsurer.standard_overwrite_file(api_key_path, base64.b64encode(api_key.encode('utf-8')).decode('utf-8'), omit=True)
                
            ## if invalid key exit
            except AuthenticationError: 
                    
                Toolkit.clear_console()
                        
                Logger.log_action(f"Authorization error while setting up {service}, please double check your API key as it appears to be incorrect.", output=True)

                Toolkit.pause_console()
                        
                exit()

            ## other error, alert user and raise it
            except Exception as e: 

                Toolkit.clear_console()
                        
                Logger.log_action(f"Unknown error while setting up {service}, The error is as follows " + str(e)  + "\nThe exception will now be raised.", output=True)

                Toolkit.pause_console()

                raise e

##-------------------start-of-reset_static_variables()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def reset_static_variables() -> None:

        """

        Resets the static variables.
        Done to prevent issues with the webgui.

        """

        Logger.clear_batch()

        Kijiku.text_to_translate = []
        Kijiku.translated_text = []
        Kijiku.je_check_text = []
        Kijiku.error_text = []
        Kijiku.openai_translation_batches = []
        Kijiku.gemini_translation_batches = []
        Kijiku.num_occurred_malformed_batches = 0
        Kijiku.translation_print_result = ""
        Kijiku.LLM_TYPE = "openai"

##-------------------start-of-check-settings()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    async def check_settings() -> None:

        """

        Prompts the user to confirm the settings in the kijiku rules file.

        """

        print("Are these settings okay? (1 for yes or 2 for no) : \n\n")

        try:

            JsonHandler.print_kijiku_rules(output=True)

        except:
            Toolkit.clear_console()

            if(input("It's likely that you're using an outdated version of the kijiku rules file, press 1 to reset these to default or 2 to exit and resolve manually : ") == "1"):
                Toolkit.clear_console()
                JsonHandler.reset_kijiku_rules_to_default()
                JsonHandler.load_kijiku_rules()

                print("Are these settings okay? (1 for yes or 2 for no) : \n\n")
                JsonHandler.print_kijiku_rules(output=True)

            else:
                FileEnsurer.exit_kudasai()

        if(input("\n") == "1"):
            pass
        else:
            JsonHandler.change_kijiku_settings()

        Toolkit.clear_console()

        print("Do you want to change your API key? (1 for yes or 2 for no) : ")

        if(input("\n") == "1"):

            if(Kijiku.LLM_TYPE == "openai"):

                if(os.path.exists(FileEnsurer.openai_api_key_path)):

                    os.remove(FileEnsurer.openai_api_key_path)
                    await Kijiku.init_api_key("OpenAI", FileEnsurer.openai_api_key_path, OpenAIService.set_api_key, OpenAIService.test_api_key_validity)

            else:
    
                if(os.path.exists(FileEnsurer.gemini_api_key_path)):

                    os.remove(FileEnsurer.gemini_api_key_path)
                    await Kijiku.init_api_key("Gemini", FileEnsurer.gemini_api_key_path, GeminiService.set_api_key, GeminiService.test_api_key_validity)

        Toolkit.clear_console()

##-------------------start-of-commence_translation()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    async def commence_translation(is_webgui:bool=False) -> None:

        """

        Uses all the other functions to translate the text provided by Kudasai.

        Parameters:
        is_webgui (bool | optional | default=False) : A bool representing whether the function is being called by the webgui.

        """
        
        Logger.log_barrier()
        Logger.log_action("Kijiku Activated, Settings are as follows : ")
        Logger.log_barrier()

        JsonHandler.print_kijiku_rules()

        Kijiku.prompt_assembly_mode = int(JsonHandler.current_kijiku_rules["base kijiku settings"]["prompt_assembly_mode"])
        Kijiku.number_of_lines_per_batch = int(JsonHandler.current_kijiku_rules["base kijiku settings"]["number_of_lines_per_batch"])
        Kijiku.sentence_fragmenter_mode = int(JsonHandler.current_kijiku_rules["base kijiku settings"]["sentence_fragmenter_mode"])
        Kijiku.je_check_mode = int(JsonHandler.current_kijiku_rules["base kijiku settings"]["je_check_mode"])
        Kijiku.num_of_malform_retries = int(JsonHandler.current_kijiku_rules["base kijiku settings"]["number_of_malformed_batch_retries"])
        Kijiku.max_batch_duration = float(JsonHandler.current_kijiku_rules["base kijiku settings"]["batch_retry_timeout"])
        Kijiku.num_concurrent_batches = int(JsonHandler.current_kijiku_rules["base kijiku settings"]["number_of_concurrent_batches"])

        Kijiku._semaphore = asyncio.Semaphore(Kijiku.num_concurrent_batches)

        OpenAIService.model = JsonHandler.current_kijiku_rules["openai settings"]["openai_model"]
        OpenAIService.system_message = JsonHandler.current_kijiku_rules["openai settings"]["openai_system_message"]
        OpenAIService.temperature = float(JsonHandler.current_kijiku_rules["openai settings"]["openai_temperature"])
        OpenAIService.top_p = float(JsonHandler.current_kijiku_rules["openai settings"]["openai_top_p"])
        OpenAIService.n = int(JsonHandler.current_kijiku_rules["openai settings"]["openai_n"])
        OpenAIService.stream = bool(JsonHandler.current_kijiku_rules["openai settings"]["openai_stream"])
        OpenAIService.stop = JsonHandler.current_kijiku_rules["openai settings"]["openai_stop"]
        OpenAIService.logit_bias = JsonHandler.current_kijiku_rules["openai settings"]["openai_logit_bias"]
        OpenAIService.max_tokens = JsonHandler.current_kijiku_rules["openai settings"]["openai_max_tokens"]
        OpenAIService.presence_penalty = float(JsonHandler.current_kijiku_rules["openai settings"]["openai_presence_penalty"])
        OpenAIService.frequency_penalty = float(JsonHandler.current_kijiku_rules["openai settings"]["openai_frequency_penalty"])

        GeminiService.model = JsonHandler.current_kijiku_rules["gemini settings"]["gemini_model"]
        GeminiService.prompt = JsonHandler.current_kijiku_rules["gemini settings"]["gemini_prompt"]
        GeminiService.temperature = float(JsonHandler.current_kijiku_rules["gemini settings"]["gemini_temperature"])
        GeminiService.top_p = JsonHandler.current_kijiku_rules["gemini settings"]["gemini_top_p"]
        GeminiService.top_k = JsonHandler.current_kijiku_rules["gemini settings"]["gemini_top_k"]
        GeminiService.candidate_count = JsonHandler.current_kijiku_rules["gemini settings"]["gemini_candidate_count"]
        GeminiService.stream = bool(JsonHandler.current_kijiku_rules["gemini settings"]["gemini_stream"])
        GeminiService.stop_sequences = JsonHandler.current_kijiku_rules["gemini settings"]["gemini_stop_sequences"]
        GeminiService.max_output_tokens = JsonHandler.current_kijiku_rules["gemini settings"]["gemini_max_output_tokens"]

        if(Kijiku.LLM_TYPE == "openai"):

            ## set the decorator to use
            decorator_to_use = backoff.on_exception(backoff.expo, max_time=lambda: Kijiku.get_max_batch_duration(), exception=(AuthenticationError, InternalServerError, RateLimitError, APITimeoutError), on_backoff=lambda details: Kijiku.log_retry(details), on_giveup=lambda details: Kijiku.log_failure(details), raise_on_giveup=False)

            OpenAIService.set_decorator(decorator_to_use)

        else:
        
            decorator_to_use = backoff.on_exception(backoff.expo, max_time=lambda: Kijiku.get_max_batch_duration(), exception=(Exception), on_backoff=lambda details: Kijiku.log_retry(details), on_giveup=lambda details: Kijiku.log_failure(details), raise_on_giveup=False)

            GeminiService.redefine_client()
            GeminiService.set_decorator(decorator_to_use)

        Toolkit.clear_console()

        Logger.log_barrier()
        Logger.log_action("Starting Prompt Building")
        Logger.log_barrier()

        if(Kijiku.LLM_TYPE == "openai"):
            Kijiku.build_openai_translation_batches()
            model = OpenAIService.model

        else:
            Kijiku.build_gemini_translation_batches()
            model = GeminiService.model

        await Kijiku.handle_cost_estimate_prompt(model, omit_prompt=is_webgui)

        Toolkit.clear_console()

        Logger.log_barrier()
        
        Logger.log_action("Starting Translation...", output=not is_webgui)
        Logger.log_barrier()

        ## requests to run asynchronously
        async_requests = Kijiku.build_async_requests(model)

        ## Use asyncio.gather to run tasks concurrently/asynchronously and wait for all of them to complete
        results = await asyncio.gather(*async_requests)

        Logger.log_barrier()
        Logger.log_action("Translation Complete!", output=not is_webgui)

        Logger.log_barrier()
        Logger.log_action("Starting Redistribution...", output=not is_webgui)

        Logger.log_barrier()

        ## Sort results based on the index to maintain order
        sorted_results = sorted(results, key=lambda x: x[0])

        ## Redistribute the sorted results
        for index, translated_prompt, translated_message in sorted_results:
            Kijiku.redistribute(translated_prompt, translated_message)

        ## try to pair the text for j-e checking if the mode is 2
        if(Kijiku.je_check_mode == 2):
            Kijiku.je_check_text = Kijiku.fix_je()

        Toolkit.clear_console()

        Logger.log_action("Done!", output=not is_webgui)
        Logger.log_barrier()

        ## assemble error text based of the error list
        Kijiku.error_text = Logger.errors

##-------------------start-of-build_async_requests()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def build_async_requests(model:str) -> list[typing.Coroutine]:

        """

        Builds the asynchronous requests.

        Parameters:
        model (string) : the model used to translate the text.

        Returns:
        async_requests (list - coroutine) : A list of coroutines that represent the asynchronous requests.

        """

        async_requests = []

        translation_batches = Kijiku.openai_translation_batches if Kijiku.LLM_TYPE == "openai" else Kijiku.gemini_translation_batches

        for i in range(0, len(translation_batches), 2):
            async_requests.append(Kijiku.handle_translation(model, i, len(translation_batches), translation_batches[i], translation_batches[i+1]))

        return async_requests

##-------------------start-of-generate_text_to_translate_batches()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def generate_text_to_translate_batches(index:int) -> tuple[typing.List[str],int]:

        """

        Generates prompts for the messages meant for the API.

        Parameters:
        index (int) : An int representing where we currently are in the text file.

        Returns:
        prompt (list - string) : A list of Japanese lines that will be assembled into messages.
        index (int) : An updated int representing where we currently are in the text file.

        """

        prompt = []
        non_word_pattern = re.compile(r'^[\W_\s\n-]+$')

        while(index < len(Kijiku.text_to_translate)):

            sentence = Kijiku.text_to_translate[index]
            stripped_sentence = sentence.strip()
            lower_sentence = sentence.lower()

            has_quotes = any(char in sentence for char in ["「", "」", "『", "』", "【", "】", "\"", "'"])
            is_part_in_sentence = "part" in lower_sentence

            if(len(prompt) < Kijiku.number_of_lines_per_batch):

                if(any(char in sentence for char in ["▼", "△", "◇"])):
                    prompt.append(f'{sentence}\n')
                    Logger.log_action(f"Sentence : {sentence}, Sentence is a pov change... adding to prompt.")

                elif(stripped_sentence == ''):
                    Logger.log_action(f"Sentence : {sentence} is empty... skipping.")

                elif(is_part_in_sentence or all(char in ["１","２","３","４","５","６","７","８","９", " "] for char in sentence)):
                    prompt.append(f'{sentence}\n') 
                    Logger.log_action(f"Sentence : {sentence}, Sentence is part marker... adding to prompt.")

                elif(non_word_pattern.match(sentence) or KatakanaUtil.is_punctuation(stripped_sentence) and not has_quotes):
                    Logger.log_action(f"Sentence : {sentence}, Sentence is punctuation... skipping.")
                    
                else:
                    prompt.append(f'{sentence}\n')
                    Logger.log_action(f"Sentence : {sentence}, Sentence is a valid sentence... adding to prompt.")

            else:
                return prompt, index

            index += 1

        return prompt, index
    
##-------------------start-of-build_openai_translation_batches()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def build_openai_translation_batches() -> None:

        """

        Builds translations batches dict for the OpenAI service.
        
        """

        i = 0

        while i < len(Kijiku.text_to_translate):
            batch, i = Kijiku.generate_text_to_translate_batches(i)

            batch = ''.join(batch)

            ## message mode one structures the first message as a system message and the second message as a model message
            if(Kijiku.prompt_assembly_mode == 1):
                system_msg = SystemTranslationMessage(content=str(OpenAIService.system_message))

            ## while message mode two structures the first message as a model message and the second message as a model message too, typically used for non-gpt-4 models if at all
            else:
                system_msg = ModelTranslationMessage(content=str(OpenAIService.system_message))

            Kijiku.openai_translation_batches.append(system_msg)

            model_msg = ModelTranslationMessage(content=batch)

            Kijiku.openai_translation_batches.append(model_msg)

        Logger.log_barrier()
        Logger.log_action("Built Messages : ")
        Logger.log_barrier()

        i = 0

        for message in Kijiku.openai_translation_batches:

            i+=1

            if(i % 2 == 0):

                Logger.log_action(str(message))
        
            else:

                Logger.log_action(str(message))
                Logger.log_barrier()

##-------------------start-of-build_gemini_translation_batches()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def build_gemini_translation_batches() -> None:

        """

        Builds translations batches dict for the Gemini service.
        
        """

        i = 0

        while i < len(Kijiku.text_to_translate):
            batch, i = Kijiku.generate_text_to_translate_batches(i)

            batch = ''.join(batch)

            ## Gemini does not use system messages or model messages, and instead just takes a string input, so we just need to place the prompt before the text to be translated
            Kijiku.gemini_translation_batches.append(GeminiService.prompt)
            Kijiku.gemini_translation_batches.append(batch)

        Logger.log_barrier()
        Logger.log_action("Built Messages : ")
        Logger.log_barrier()

        i = 0

        for message in Kijiku.gemini_translation_batches:

            i+=1

            if(i % 2 == 0):

                Logger.log_action(str(message))
        
            else:

                Logger.log_action(str(message))
                Logger.log_barrier()

##-------------------start-of-estimate_cost()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def estimate_cost(model:str, price_case:int | None = None) -> typing.Tuple[int, float, str]:

        """

        Attempts to estimate cost.

        Parameters:
        model (string) : the model used to translate the text.
        price_case (int) : the price case used to calculate the cost.

        Returns:
        num_tokens (int) : the number of tokens used.
        min_cost (float) : the minimum cost of translation.
        model (string) : the model used to translate the text.

        """

        MODEL_COSTS = {
            "gpt-3.5-turbo": {"price_case": 2, "input_cost": 0.0010, "output_cost": 0.0020},
            "gpt-4": {"price_case": 4, "input_cost": 0.01, "output_cost": 0.03},
            "gpt-4-turbo-preview": {"price_case": 4, "input_cost": 0.01, "output_cost": 0.03},
            "gpt-3.5-turbo-0613": {"price_case": 1, "input_cost": 0.0015, "output_cost": 0.0020},
            "gpt-3.5-turbo-0301": {"price_case": 1, "input_cost": 0.0015, "output_cost": 0.0020},
            "gpt-3.5-turbo-1106": {"price_case": 2, "input_cost": 0.0010, "output_cost": 0.0020},
            "gpt-3.5-turbo-0125": {"price_case": 7, "input_cost": 0.0005, "output_cost": 0.0015},
            "gpt-3.5-turbo-16k-0613": {"price_case": 3, "input_cost": 0.0030, "output_cost": 0.0040},
            "gpt-4-1106-preview": {"price_case": 4, "input_cost": 0.01, "output_cost": 0.03},
            "gpt-4-0125-preview": {"price_case": 4, "input_cost": 0.01, "output_cost": 0.03},
            "gpt-4-0314": {"price_case": 5, "input_cost": 0.03, "output_cost": 0.06},
            "gpt-4-0613": {"price_case": 5, "input_cost": 0.03, "output_cost": 0.06},
            "gpt-4-32k-0314": {"price_case": 6, "input_cost": 0.06, "output_cost": 0.012},
            "gpt-4-32k-0613": {"price_case": 6, "input_cost": 0.06, "output_cost": 0.012},
            "gemini-1.0-pro-001": {"price_case": 8, "input_cost": 0.0, "output_cost": 0.0},
            "gemini-1.0-pro-vision-001": {"price_case": 8, "input_cost": 0.0, "output_cost": 0.0},
            "gemini-1.0-pro": {"price_case": 8, "input_cost": 0.0, "output_cost": 0.0},
            "gemini-1.0-pro-vision": {"price_case": 8, "input_cost": 0.0, "output_cost": 0.0},
            "gemini-pro": {"price_case": 8, "input_cost": 0.0, "output_cost": 0.0},
            "gemini-pro-vision": {"price_case": 8, "input_cost": 0.0, "output_cost": 0.0}
        }

        assert model in FileEnsurer.ALLOWED_OPENAI_MODELS or model in FileEnsurer.ALLOWED_GEMINI_MODELS, f"""Kudasai does not support : {model}"""

        ## default models are first, then the rest are sorted by price case
        if(price_case is None):

            if(model == "gpt-3.5-turbo"):
                print("Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-1106 as it is the most recent version of gpt-3.5-turbo.")
                return Kijiku.estimate_cost("gpt-3.5-turbo-1106", price_case=2)
            
            elif(model == "gpt-4"):
                print("Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-1106-preview as it is the most recent version of gpt-4.")
                return Kijiku.estimate_cost("gpt-4-1106-preview", price_case=4)
            
            elif(model == "gpt-4-turbo-preview"):
                print("Warning: gpt-4-turbo-preview may change over time. Returning num tokens assuming gpt-4-0125-preview as it is the most recent version of gpt-4-turbo-preview.")
                return Kijiku.estimate_cost("gpt-4-0125-preview", price_case=4)
            
            elif(model == "gpt-3.5-turbo-0613"):
                print("Warning: gpt-3.5-turbo-0613 is considered depreciated by OpenAI as of November 6, 2023 and could be shutdown as early as June 13, 2024. Consider switching to gpt-3.5-turbo-1106.")
                return Kijiku.estimate_cost(model, price_case=1)

            elif(model == "gpt-3.5-turbo-0301"):
                print("Warning: gpt-3.5-turbo-0301 is considered depreciated by OpenAI as of June 13, 2023 and could be shutdown as early as June 13, 2024. Consider switching to gpt-3.5-turbo-1106 unless you are specifically trying to break the filter.")
                return Kijiku.estimate_cost(model, price_case=1)
            
            elif(model == "gpt-3.5-turbo-1106"):
                return Kijiku.estimate_cost(model, price_case=2)
            
            elif(model == "gpt-3.5-turbo-0125"):
                return Kijiku.estimate_cost(model, price_case=7)
            
            elif(model == "gpt-3.5-turbo-16k-0613"):
                print("Warning: gpt-3.5-turbo-16k-0613 is considered depreciated by OpenAI as of November 6, 2023 and could be shutdown as early as June 13, 2024. Consider switching to gpt-3.5-turbo-1106.")
                return Kijiku.estimate_cost(model, price_case=3)
            
            elif(model == "gpt-4-1106-preview"):
                return Kijiku.estimate_cost(model, price_case=4)
            
            elif(model == "gpt-4-0125-preview"):
                return Kijiku.estimate_cost(model, price_case=4)
            
            elif(model == "gpt-4-0314"):
                print("Warning: gpt-4-0314 is considered depreciated by OpenAI as of June 13, 2023 and could be shutdown as early as June 13, 2024. Consider switching to gpt-4-0613.")
                return Kijiku.estimate_cost(model, price_case=5)
            
            elif(model == "gpt-4-0613"):
                return Kijiku.estimate_cost(model, price_case=5)
            
            elif(model == "gpt-4-32k-0314"):
                print("Warning: gpt-4-32k-0314 is considered depreciated by OpenAI as of June 13, 2023 and could be shutdown as early as June 13, 2024. Consider switching to gpt-4-32k-0613.")
                return Kijiku.estimate_cost(model, price_case=6)
            
            elif(model == "gpt-4-32k-0613"):
                return Kijiku.estimate_cost(model, price_case=6)
            
            elif(model == "gemini-pro"):
                print(f"Warning: gemini-pro may change over time. Returning num tokens assuming gemini-1.0-pro-001 as it is the most recent version of gemini-1.0-pro.")
                return Kijiku.estimate_cost("gemini-1.0-pro-001", price_case=8)
            
            elif(model == "gemini-pro-vision"):
                print("Warning: gemini-pro-vision may change over time. Returning num tokens assuming gemini-1.0-pro-vision-001 as it is the most recent version of gemini-1.0-pro-vision.")
                return Kijiku.estimate_cost("gemini-1.0-pro-vision-001", price_case=8)
            
            elif(model == "gemini-1.0-pro"):
                print(f"Warning: gemini-1.0-pro may change over time. Returning num tokens assuming gemini-1.0-pro-001 as it is the most recent version of gemini-1.0-pro.")
                return Kijiku.estimate_cost(model, price_case=8)
            
            elif(model == "gemini-1.0-pro-vision"):
                print("Warning: gemini-1.0-pro-vision may change over time. Returning num tokens assuming gemini-1.0-pro-vision-001 as it is the most recent version of gemini-1.0-pro-vision.")
                return Kijiku.estimate_cost(model, price_case=8)
            
            elif(model == "gemini-1.0-pro-001"):
                return Kijiku.estimate_cost(model, price_case=8)
            
            elif(model == "gemini-1.0-pro-vision-001"):
                return Kijiku.estimate_cost(model, price_case=8)
            
        else:

            cost_details = MODEL_COSTS.get(model)

            if(not cost_details):
                raise ValueError(f"Cost details not found for model: {model}.")

            ## break down the text into a string than into tokens
            text = ''.join(Kijiku.text_to_translate)

            if(Kijiku.LLM_TYPE == "openai"):
                encoding = tiktoken.encoding_for_model(model)
                num_tokens = len(encoding.encode(text))

            else:
                num_tokens = GeminiService.count_tokens(text)

            input_cost = cost_details["input_cost"]
            output_cost = cost_details["output_cost"]

            min_cost_for_input = (num_tokens / 1000) * input_cost
            min_cost_for_output = (num_tokens / 1000) * output_cost
            min_cost = min_cost_for_input + min_cost_for_output

            return num_tokens, min_cost, model
        
        ## type checker doesn't like the chance of None being returned, so we raise an exception here if it gets to this point
        raise Exception("An unknown error occurred while calculating the minimum cost of translation.")
    
##-------------------start-of-handle_cost_estimate_prompt()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    async def handle_cost_estimate_prompt(model:str, omit_prompt:bool=False) -> str:

        """

        Handles the cost estimate prompt.

        Parameters:
        model (string) : the model used to translate the text.
        omit_prompt (bool) : whether or not to omit the prompt.
        
        Returns:
        model (string) : the model used to translate the text.
        
        """ 

        ## get cost estimate and confirm
        num_tokens, min_cost, model = Kijiku.estimate_cost(model)

        print("\nNote that the cost estimate is not always accurate, and may be higher than the actual cost. However cost calculation now includes output tokens.\n")

        Logger.log_barrier()
        Logger.log_action("Calculating cost")
        Logger.log_barrier()

        if(Kijiku.LLM_TYPE == "gemini"):
            print("As of Kudasai v3.4.0, Gemini Pro is Free to use")
        
        Logger.log_action("Estimated number of tokens : " + str(num_tokens), output=True, omit_timestamp=True)
        Logger.log_action("Estimated minimum cost : " + str(min_cost) + " USD", output=True, omit_timestamp=True)
        Logger.log_barrier()

        if(not omit_prompt):
            if(input("\nContinue? (1 for yes or 2 for no) : ") == "1"):
                Logger.log_action("User confirmed translation.")

            else:
                Logger.log_action("User cancelled translation.")
                Logger.push_batch()
                exit()

        return model
    
##-------------------start-of-handle_translation()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    async def handle_translation(model:str, index:int, length:int, translation_instructions:typing.Union[str, Message], translation_prompt:typing.Union[str, Message]) -> tuple[int, typing.Union[str, Message], str]:

        """
        Handles the translation for a given system and user message.

        Parameters:
        model (string) : the model used to translate the text.
        index (int) : the index of the message in the text file.
        length (int) : the length of the text file.
        translation_instructions (typing.Union[str, Message]) : the translation instructions.
        translation_prompt (typing.Union[str, Message]) : the translation prompt.

        Returns:
        index (int) : the index of the message in the text file.
        translation_prompt (typing.Union[str, Message]) : the translation prompt.
        translated_message (str) : the translated message.

        """

        ## Basically limits the number of concurrent batches
        async with Kijiku._semaphore:
            num_tries = 0

            while True:

                ## For the webgui
                if(FileEnsurer.do_interrupt == True):
                    raise Exception("Interrupted by user.")

                message_number = (index // 2) + 1
                Logger.log_action(f"Trying translation for batch {message_number} of {length//2}...", output=True)

                try:

                    if(Kijiku.LLM_TYPE == "openai"):
                        translated_message = await OpenAIService.translate_message(translation_instructions, translation_prompt) # type: ignore

                    else:
                        translated_message = await GeminiService.translate_message(translation_instructions, translation_prompt) # type: ignore

                ## will only occur if the max_batch_duration is exceeded, so we just return the untranslated text
                except MaxBatchDurationExceededException:
                    translated_message = translation_prompt.content if isinstance(translation_prompt, Message) else translation_prompt
                    Logger.log_error(f"Batch {message_number} of {length//2} was not translated due to exceeding the max request duration, returning the untranslated text...", output=True)
                    break

                ## do not even bother if not a gpt 4 model, because gpt-3 seems unable to format properly
                if("gpt-4" not in model):
                    break

                if(await Kijiku.check_if_translation_is_good(translated_message, translation_prompt)):
                    Logger.log_action(f"Translation for batch {message_number} of {length//2} successful!", output=True)
                    break

                if(num_tries >= Kijiku.num_of_malform_retries):
                    Logger.log_action(f"Batch {message_number} of {length//2} was malformed, but exceeded the maximum number of retries, Translation successful!", output=True)
                    break

                else:
                    num_tries += 1
                    Logger.log_error(f"Batch {message_number} of {length//2} was malformed, retrying...", output=True)
                    Kijiku.num_occurred_malformed_batches += 1

            return index, translation_prompt, translated_message
    
##-------------------start-of-check_if_translation_is_good()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    async def check_if_translation_is_good(translated_message:str, translation_prompt:typing.Union[Message, str]) -> bool:

        """
        
        Checks if the translation is good, i.e. the number of lines in the prompt and the number of lines in the translated message are the same.

        Parameters:
        translated_message (str) : the translated message.
        translation_prompt (typing.Union[str, Message]) : the translation prompt.

        Returns:
        is_valid (bool) : whether or not the translation is valid.

        """

        if(not isinstance(translation_prompt, str)):
            prompt = translation_prompt.content

        else:
            prompt = translation_prompt
            
        is_valid = False

        jap = [line for line in prompt.split('\n') if line.strip()]  ## Remove blank lines
        eng = [line for line in translated_message.split('\n') if line.strip()]  ## Remove blank lines

        if(len(jap) == len(eng)):
            is_valid = True
    
        return is_valid
    
##-------------------start-of-redistribute()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def redistribute(translation_prompt:typing.Union[Message, str], translated_message:str) -> None:

        """

        Puts translated text back into the text file.

        Parameters:
        translation_prompt (typing.Union[str, Message]) : the translation prompt.
        translated_message (str) : the translated message.

        """

        if(not isinstance(translation_prompt, str)):
            prompt = translation_prompt.content

        else:
            prompt = translation_prompt

        ## Separates with hyphens if the mode is 1 
        if(Kijiku.je_check_mode == 1):

            Kijiku.je_check_text.append("\n-------------------------\n"+ prompt + "\n\n")
            Kijiku.je_check_text.append(translated_message + '\n')
        
        ## Mode two tries to pair the text for j-e checking, see fix_je() for more details
        elif(Kijiku.je_check_mode == 2):
            Kijiku.je_check_text.append(prompt)
            Kijiku.je_check_text.append(translated_message)

        ## mode 1 is the default mode, uses regex and other nonsense to split sentences
        if(Kijiku.sentence_fragmenter_mode == 1): 

            sentences = re.findall(r"(.*?(?:(?:\"|\'|-|~|!|\?|%|\(|\)|\.\.\.|\.|---|\[|\])))(?:\s|$)", translated_message)

            patched_sentences = []
            build_string = None

            for sentence in sentences:

                sentence:str = sentence

                if(sentence.startswith("\"") and not sentence.endswith("\"") and build_string is None):
                    build_string = sentence
                    continue
                elif(not sentence.startswith("\"") and sentence.endswith("\"") and build_string is not None):
                    build_string += f" {sentence}"
                    patched_sentences.append(build_string)
                    build_string = None
                    continue
                elif(build_string is not None):
                    build_string += f" {sentence}"
                    continue

                Kijiku.translated_text.append(sentence + '\n')

            for i in range(len(Kijiku.translated_text)):
                if Kijiku.translated_text[i] in patched_sentences:
                    index = patched_sentences.index(Kijiku.translated_text[i])
                    Kijiku.translated_text[i] = patched_sentences[index]

        ## mode 2 just assumes the LLM formatted it properly
        elif(Kijiku.sentence_fragmenter_mode == 2):
            
            Kijiku.translated_text.append(translated_message + '\n\n')
        
##-------------------start-of-fix_je()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def fix_je() -> typing.List[str]:

        """

        Fixes the J->E text to be more j-e check friendly.

        Note that fix_je() is not always accurate, and may use standard j-e formatting instead of the corrected formatting.

        Returns:
        final_list (list - str) : the 'fixed' J->E text.

        """
        
        i = 1
        final_list = []

        while i < len(Kijiku.je_check_text):
            jap = Kijiku.je_check_text[i-1].split('\n')
            eng = Kijiku.je_check_text[i].split('\n')

            jap = [line for line in jap if line.strip()]  ## Remove blank lines
            eng = [line for line in eng if line.strip()]  ## Remove blank lines    

            final_list.append("-------------------------\n")

            if(len(jap) == len(eng)):

                for jap_line,eng_line in zip(jap,eng):
                    if(jap_line and eng_line): ## check if jap_line and eng_line aren't blank
                        final_list.append(jap_line + '\n\n')
                        final_list.append(eng_line + '\n\n')

                        final_list.append("--------------------------------------------------\n")
     

            else:

                final_list.append(Kijiku.je_check_text[i-1] + '\n\n')
                final_list.append(Kijiku.je_check_text[i] + '\n\n')

                final_list.append("--------------------------------------------------\n")

            i+=2

        return final_list

##-------------------start-of-assemble_results()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def assemble_results(time_start:float, time_end:float) -> None:

        """

        Generates the Kijiku translation print result, does not directly output/return, but rather sets Kijiku.translation_print_result to the output.

        Parameters:
        time_start (float) : When the translation started.
        time_end (float) : When the translation finished.

        """

        result = (
            f"Time Elapsed : {Toolkit.get_elapsed_time(time_start, time_end)}\n"
            f"Number of malformed batches : {Kijiku.num_occurred_malformed_batches}\n\n"
            f"Debug text have been written to : {FileEnsurer.debug_log_path}\n"
            f"J->E text have been written to : {FileEnsurer.je_check_path}\n"
            f"Translated text has been written to : {FileEnsurer.translated_text_path}\n"
            f"Errors have been written to : {FileEnsurer.error_log_path}\n"
        )
        
        Kijiku.translation_print_result = result

##-------------------start-of-write_kijiku_results()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    @permission_error_decorator()
    def write_kijiku_results() -> None:

        """
        
        This function is called to write the results of the Kijiku translation module to the output directory.

        """

        ## ensures the output directory exists, cause it could get moved or fucked with.
        FileEnsurer.standard_create_directory(FileEnsurer.output_dir)

        with open(FileEnsurer.error_log_path, 'a+', encoding='utf-8') as file:
            file.writelines(Kijiku.error_text)

        with open(FileEnsurer.je_check_path, 'w', encoding='utf-8') as file:
            file.writelines(Kijiku.je_check_text)

        with open(FileEnsurer.translated_text_path, 'w', encoding='utf-8') as file:
            file.writelines(Kijiku.translated_text)

        ## Instructions to create a copy of the output for archival
        FileEnsurer.standard_create_directory(FileEnsurer.archive_dir)

        timestamp = Toolkit.get_timestamp(is_archival=True)

        ## pushes the tl debug log to the file without clearing the file
        Logger.push_batch()
        Logger.clear_batch()

        list_of_result_tuples = [('kijiku_translated_text', Kijiku.translated_text), 
                                 ('kijiku_je_check_text', Kijiku.je_check_text), 
                                 ('kijiku_error_log', Kijiku.error_text),
                                 ('debug_log', FileEnsurer.standard_read_file(Logger.log_file_path))]

        FileEnsurer.archive_results(list_of_result_tuples, 
                                    module='kijiku', timestamp=timestamp)
