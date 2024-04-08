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
from easytl import EasyTL, Message, SystemTranslationMessage, ModelTranslationMessage

import backoff

## custom modules
from handlers.json_handler import JsonHandler

from modules.common.file_ensurer import FileEnsurer
from modules.common.logger import Logger
from modules.common.toolkit import Toolkit
from modules.common.exceptions import AuthenticationError, MaxBatchDurationExceededException, AuthenticationError, InternalServerError, RateLimitError, APITimeoutError, GoogleAuthError
from modules.common.decorators import permission_error_decorator

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
    openai_translation_batches:typing.List[SystemTranslationMessage | ModelTranslationMessage] = []

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

    decorator_to_use:typing.Callable

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
            await Kijiku.init_api_key("OpenAI", FileEnsurer.openai_api_key_path, EasyTL.set_api_key, EasyTL.test_api_key_validity)

        else:
            await Kijiku.init_api_key("Gemini", FileEnsurer.gemini_api_key_path, EasyTL.set_api_key, EasyTL.test_api_key_validity)

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

        ## get saved API key if exists
        try:
            with open(api_key_path, 'r', encoding='utf-8') as file: 
                api_key = base64.b64decode((file.read()).encode('utf-8')).decode('utf-8')

            api_key_setter(service.lower(), api_key)

            is_valid, e = await api_key_tester(service.lower())

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

                api_key_setter(service.lower(), api_key)

                is_valid, e = await api_key_tester(service.lower())

                if(not is_valid and e is not None):
                    raise e

                FileEnsurer.standard_overwrite_file(api_key_path, base64.b64encode(api_key.encode('utf-8')).decode('utf-8'), omit=True)
                
            ## if invalid key exit
            except (GoogleAuthError, AuthenticationError):
                    
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
                    await Kijiku.init_api_key("OpenAI", FileEnsurer.openai_api_key_path, EasyTL.set_api_key, EasyTL.test_api_key_validity)

            else:
    
                if(os.path.exists(FileEnsurer.gemini_api_key_path)):

                    os.remove(FileEnsurer.gemini_api_key_path)
                    await Kijiku.init_api_key("Gemini", FileEnsurer.gemini_api_key_path, EasyTL.set_api_key, EasyTL.test_api_key_validity)

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
        Logger.log_action("Kijiku Activated, LLM Type : " + Kijiku.LLM_TYPE)
        Logger.log_barrier()
        Logger.log_action("Settings are as follows : ")
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

        Kijiku.openai_model = JsonHandler.current_kijiku_rules["openai settings"]["openai_model"]
        Kijiku.openai_system_message = JsonHandler.current_kijiku_rules["openai settings"]["openai_system_message"]
        Kijiku.openai_temperature = float(JsonHandler.current_kijiku_rules["openai settings"]["openai_temperature"])
        Kijiku.openai_top_p = float(JsonHandler.current_kijiku_rules["openai settings"]["openai_top_p"])
        Kijiku.openai_n = int(JsonHandler.current_kijiku_rules["openai settings"]["openai_n"])
        Kijiku.openai_stream = bool(JsonHandler.current_kijiku_rules["openai settings"]["openai_stream"])
        Kijiku.openai_stop = JsonHandler.current_kijiku_rules["openai settings"]["openai_stop"]
        Kijiku.openai_logit_bias = JsonHandler.current_kijiku_rules["openai settings"]["openai_logit_bias"]
        Kijiku.openai_max_tokens = JsonHandler.current_kijiku_rules["openai settings"]["openai_max_tokens"]
        Kijiku.openai_presence_penalty = float(JsonHandler.current_kijiku_rules["openai settings"]["openai_presence_penalty"])
        Kijiku.openai_frequency_penalty = float(JsonHandler.current_kijiku_rules["openai settings"]["openai_frequency_penalty"])

        Kijiku.gemini_model = JsonHandler.current_kijiku_rules["gemini settings"]["gemini_model"]
        Kijiku.gemini_prompt = JsonHandler.current_kijiku_rules["gemini settings"]["gemini_prompt"]
        Kijiku.gemini_temperature = float(JsonHandler.current_kijiku_rules["gemini settings"]["gemini_temperature"])
        Kijiku.gemini_top_p = float(JsonHandler.current_kijiku_rules["gemini settings"]["gemini_top_p"])
        Kijiku.gemini_top_k = JsonHandler.current_kijiku_rules["gemini settings"]["gemini_top_k"]
        Kijiku.gemini_candidate_count = JsonHandler.current_kijiku_rules["gemini settings"]["gemini_candidate_count"]
        Kijiku.gemini_stream = bool(JsonHandler.current_kijiku_rules["gemini settings"]["gemini_stream"])
        Kijiku.gemini_stop_sequences = JsonHandler.current_kijiku_rules["gemini settings"]["gemini_stop_sequences"]
        Kijiku.gemini_max_output_tokens = JsonHandler.current_kijiku_rules["gemini settings"]["gemini_max_output_tokens"]


        if(Kijiku.LLM_TYPE == "openai"):
            Kijiku.decorator_to_use = backoff.on_exception(backoff.expo, max_time=lambda: Kijiku.get_max_batch_duration(), exception=(AuthenticationError, InternalServerError, RateLimitError, APITimeoutError), on_backoff=lambda details: Kijiku.log_retry(details), on_giveup=lambda details: Kijiku.log_failure(details), raise_on_giveup=False)

        else:
            Kijiku.decorator_to_use = backoff.on_exception(backoff.expo, max_time=lambda: Kijiku.get_max_batch_duration(), exception=(Exception), on_backoff=lambda details: Kijiku.log_retry(details), on_giveup=lambda details: Kijiku.log_failure(details), raise_on_giveup=False)

        Toolkit.clear_console()

        Logger.log_barrier()
        Logger.log_action("Starting Prompt Building")
        Logger.log_barrier()

        Kijiku.build_translation_batches()

        model = JsonHandler.current_kijiku_rules["openai settings"]["openai_mode"] if Kijiku.LLM_TYPE == "openai" else JsonHandler.current_kijiku_rules["gemini settings"]["gemini_mode"]

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

            instructions = translation_batches[i]
            prompt = translation_batches[i+1]

            assert isinstance(instructions, SystemTranslationMessage) or isinstance(instructions, str)
            assert isinstance(prompt, ModelTranslationMessage) or isinstance(prompt, str)

            async_requests.append(Kijiku.handle_translation(model, i, len(translation_batches), instructions, prompt))

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
            lowercase_sentence = sentence.lower()

            has_quotes = any(char in sentence for char in ["「", "」", "『", "』", "【", "】", "\"", "'"])
            is_part_in_sentence = "part" in lowercase_sentence

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
    
##-------------------start-of-build_translation_batches()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def build_translation_batches() -> None:

        """

        Builds translations batches dict for the specified service.

        """

        i = 0

        while i < len(Kijiku.text_to_translate):

            batch, i = Kijiku.generate_text_to_translate_batches(i)
            batch = ''.join(batch)

            if(Kijiku.LLM_TYPE == 'openai'):

                if(Kijiku.prompt_assembly_mode == 1):
                    system_msg = SystemTranslationMessage(content=str(Kijiku.openai_system_message))
                else:
                    system_msg = SystemTranslationMessage(content=str(Kijiku.openai_system_message))

                Kijiku.openai_translation_batches.append(system_msg)
                model_msg = ModelTranslationMessage(content=batch)
                Kijiku.openai_translation_batches.append(model_msg)

            else:
                Kijiku.gemini_translation_batches.append(Kijiku.gemini_prompt)
                Kijiku.gemini_translation_batches.append(batch)

        Logger.log_barrier()
        Logger.log_action("Built Messages : ")
        Logger.log_barrier()

        i = 0

        for message in (Kijiku.openai_translation_batches if Kijiku.LLM_TYPE == 'openai' else Kijiku.gemini_translation_batches):

            i+=1

            message = str(message) if Kijiku.LLM_TYPE == 'gemini' else message.content # type: ignore

            if(i % 2 == 1):
                Logger.log_barrier()

            Logger.log_action(message)

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

        translation_instructions = Kijiku.openai_system_message if Kijiku.LLM_TYPE == "openai" else Kijiku.gemini_prompt

        ## get cost estimate and confirm
        num_tokens, min_cost, model = EasyTL.calculate_cost(text=Kijiku.text_to_translate, service=Kijiku.LLM_TYPE, model=model,translation_instructions=translation_instructions)

        print("\nNote that the cost estimate is not always accurate, and may be higher than the actual cost. However cost calculation now includes output tokens.\n")

        Logger.log_barrier()
        Logger.log_action("Calculating cost")
        Logger.log_barrier()

        if(Kijiku.LLM_TYPE == "gemini"):
            Logger.log_action(f"As of Kudasai {Toolkit.CURRENT_VERSION}, Gemini Pro 1.0 is free to use under 60 requests per minute, Gemini Pro 1.5 is free to use under 2 requests per minute.\nIt is up to you to set these in the settings json.\nIt is currently unknown whether the ultra model parameter is connecting to the actual ultra model and not a pro one. As it works, but does not appear on any documentation.\n", output=True, omit_timestamp=True)
        
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
    async def handle_translation(model:str, index:int, length:int, translation_instructions:typing.Union[str, SystemTranslationMessage], translation_prompt:typing.Union[str, ModelTranslationMessage]) -> tuple[int, str, str]:

        """

        Handles the translation requests for the specified service.

        Parameters:
        model (string) : The model of the service used to translate the text.
        index (int) : The index of the translation batch.
        length (int) : The length of the translation batch.
        translation_instructions (typing.Union[str, Message]) : The translation instructions.
        translation_prompt (typing.Union[str, Message]) : The translation prompt.

        Returns:
        index (int) : The index of the translation batch.
        translation_prompt (typing.Union[str, Message]) : The translation prompt.
        translated_message (str) : The translated message.

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
                        translated_message = await EasyTL.openai_translate_async(text=translation_prompt,
                                                                                decorator=Kijiku.decorator_to_use,
                                                                                translation_instructions=translation_instructions,
                                                                                model=model,
                                                                                temperature=Kijiku.openai_temperature,
                                                                                top_p=Kijiku.openai_top_p,
                                                                                stop=Kijiku.openai_stop,
                                                                                max_tokens=Kijiku.openai_max_tokens,
                                                                                presence_penalty=Kijiku.openai_presence_penalty,
                                                                                frequency_penalty=Kijiku.openai_frequency_penalty)

                    else:

                        assert isinstance(translation_prompt, str)

                        translated_message = await EasyTL.gemini_translate_async(text=translation_prompt,
                                                                                 decorator=Kijiku.decorator_to_use,
                                                                                 model=model,
                                                                                 temperature=Kijiku.gemini_temperature,
                                                                                 top_p=Kijiku.gemini_top_p,
                                                                                 top_k=Kijiku.gemini_top_k,
                                                                                 stop_sequences=Kijiku.gemini_stop_sequences,
                                                                                 max_output_tokens=Kijiku.gemini_max_output_tokens)

                ## will only occur if the max_batch_duration is exceeded, so we just return the untranslated text
                except MaxBatchDurationExceededException:

                    translated_message = str(translation_prompt)

                    Logger.log_error(f"Batch {message_number} of {length//2} was not translated due to exceeding the max request duration, returning the untranslated text...", output=True)
                    break

                ## do not even bother if not a gpt 4 model, because gpt-3 seems unable to format properly
                ## since gemini is free, we can just try again if it's malformed
                if("gpt-4" not in model and Kijiku.LLM_TYPE != "gemini"): 
                    break

                assert isinstance(translated_message, str)
                assert isinstance(translation_prompt, str)

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

            return index, str(translation_prompt), str(translated_message)
    
##-------------------start-of-check_if_translation_is_good()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    async def check_if_translation_is_good(translated_message:str, translation_prompt:typing.Union[SystemTranslationMessage, str]) -> bool:

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

        Fixes the J->E text to be more j-e checker friendly.

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
