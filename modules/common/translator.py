## built-in libaries
import typing
import base64
import re
import shutil
import time
import typing
import asyncio
import os
import logging

## third party modules
from kairyou import KatakanaUtil
from easytl import EasyTL, Message, SystemTranslationMessage, ModelTranslationMessage

import backoff

## custom modules
from handlers.json_handler import JsonHandler

from modules.common.file_ensurer import FileEnsurer
from modules.common.toolkit import Toolkit
from modules.common.exceptions import OpenAIAuthenticationError, MaxBatchDurationExceededException, DeepLAuthorizationException, OpenAIInternalServerError, OpenAIRateLimitError, OpenAIAPITimeoutError, GoogleAuthError, OpenAIAPIStatusError, OpenAIAPIConnectionError, DeepLException, GoogleAPIError
from modules.common.decorators import permission_error_decorator
from modules.common.gender_util import GenderUtil

##-------------------start-of-Translator--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Translator:

    """
    
    Translator is a class that is used to interact with translation methods and translate text.
    Currently supports OpenAI, Gemini, DeepL, and Google Translate.
    
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

    ## same as above, but for deepl, just the text to be translated
    deepl_translation_batches:typing.List[str] = []

    ## also the same for google translate
    google_translate_translation_batches:typing.List[str] = []

    num_occurred_malformed_batches = 0

    ## semaphore to limit the number of concurrent batches
    _semaphore = asyncio.Semaphore(5)

    ##--------------------------------------------------------------------------------------------------------------------------

    TRANSLATION_METHOD:typing.Literal["openai", "gemini", "deepl", "google translate"] = "deepl"

    translation_print_result = ""

    ##--------------------------------------------------------------------------------------------------------------------------

    prompt_assembly_mode:int
    number_of_lines_per_batch:int
    sentence_fragmenter_mode:int
    je_check_mode:int
    number_of_malformed_batch_retries:int
    batch_retry_timeout:float
    num_concurrent_batches:int
    gender_context_insertion:bool
    is_cote:bool

    decorator_to_use:typing.Callable

    is_cli = False

    pre_provided_api_key = ""

##-------------------start-of-get_max_batch_duration()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def get_max_batch_duration() -> float:

        """
        
        Returns the max batch duration.
        Structured as a function so that it can be used as a lambda function in the backoff decorator. As decorators call the function when they are defined/runtime, not when they are called. Which I learned the hard way.

        Returns:
        max_batch_duration (float) : the max batch duration.

        """

        return Translator.max_batch_duration
    
##-------------------start-of-log_retry()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def log_retry(details) -> None:

        """

        Logs the retry message.

        Parameters:
        details (dict) : the details of the retry.

        """

        retry_msg = f"Retrying translation after {details['wait']} seconds after {details['tries']} tries {details['target']} due to {details['exception']}."

        logging.warning(retry_msg)

##-------------------start-of-log_failure()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def log_failure(details) -> None:

        """
        
        Logs the translation batch failure message.

        Parameters:
        details (dict) : the details of the failure.

        Raises:
        MaxBatchDurationExceededException : An exception that is raised when the max batch duration is exceeded.

        """

        error_msg = f"Exceeded allowed duration of {details['wait']} seconds, returning untranslated text after {details['tries']} tries {details['target']}."

        logging.error(error_msg)

        raise MaxBatchDurationExceededException(error_msg)

##-------------------start-of-translate()--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    async def translate() -> None:

        """

        Translate the text in the file at the path given.

        """

        ## set this here cause the try-except could throw before we get past the settings configuration
        time_start = time.time()

        try:
        
            await Translator.initialize()

            JsonHandler.validate_json()

            if(not Translator.is_cli and Translator.TRANSLATION_METHOD != "google translate"):
                await Translator.check_settings()

            ## set actual start time to the end of the settings configuration
            time_start = time.time()

            await Translator.commence_translation()

        except Exception as e:
            
            Translator.translation_print_result += "An error has occurred, outputting results so far..."

            FileEnsurer.handle_critical_exception(e)

        finally:

            time_end = time.time() 

            Translator.assemble_results(time_start, time_end)

            if(Translator.is_cli):
                Toolkit.pause_console()

##-------------------start-of-initialize()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    async def initialize() -> None:

        """

        Sets the API Key for the respective service and loads the translation settings.
    
        """

        translation_methods = {
            "1": ("openai", FileEnsurer.openai_api_key_path),
            "2": ("gemini", FileEnsurer.gemini_api_key_path),
            "3": ("deepl", FileEnsurer.deepl_api_key_path),
            "4": ("google translate", FileEnsurer.google_translate_service_key_json_path)
        }

        if(not Translator.is_cli):
            method = input("What method would you like to use for translation? (1 for OpenAI, 2 for Gemini, 3 for Deepl, 4 for Google Translate), or any other key to exit) : \n")

            if(method not in translation_methods.keys()):
                print("\nThank you for using Kudasai, goodbye.")
                time.sleep(2)
                FileEnsurer.exit_kudasai()
            
            Toolkit.clear_console()

        else:
            method = Translator.TRANSLATION_METHOD

        Translator.TRANSLATION_METHOD, api_key_path = translation_methods.get(method, ("deepl", FileEnsurer.deepl_api_key_path))
        
        if(Translator.pre_provided_api_key != ""):
            if(Translator.TRANSLATION_METHOD == "google translate"):
                encoded_key = base64.b64encode(Translator.pre_provided_api_key.encode('utf-8')).decode('utf-8')

            else:
                encoded_key = Translator.pre_provided_api_key

            Translator.pre_provided_api_key = ""
            
            with open(api_key_path, 'w+', encoding='utf-8') as file: 
                file.write(encoded_key)

        await Translator.init_api_key(Translator.TRANSLATION_METHOD.capitalize(), api_key_path, EasyTL.set_credentials, EasyTL.test_credentials)
        
        ## try to load the translation settings
        try: 
            JsonHandler.load_translation_settings()
        ## if the translation settings don't exist, create them
        except: 
            JsonHandler.reset_translation_settings_to_default()
            JsonHandler.load_translation_settings()
        
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

        def get_api_key_from_file():
            with open(api_key_path, 'r', encoding='utf-8') as file: 
                return base64.b64decode((file.read()).encode('utf-8')).decode('utf-8')

        def save_api_key(api_key):
            if(service != "Google translate"):
                encoded_key = base64.b64encode(api_key.encode('utf-8')).decode('utf-8')
                FileEnsurer.standard_overwrite_file(api_key_path, encoded_key, omit=True)
            else:
                FileEnsurer.standard_overwrite_file(api_key_path, api_key, omit=True)

        ## get saved API key if exists
        try:

            if(service != "Google translate"):
                api_key = get_api_key_from_file()
            else:
                api_key = api_key_path

            api_key_setter(service.lower(), api_key)

            is_valid, e = api_key_tester(service.lower())

            ## if not valid, raise the exception that caused the test to fail
            if(not is_valid and e is not None):
                raise e

            logging.info(f"Used saved API key in {api_key_path}")        

            time.sleep(2)

        ## else try to get API key manually
        except:

            Toolkit.clear_console()

            input_message = (
                f"DO NOT DELETE YOUR COPY OF THE API KEY\n\nPlease enter the {service} API key you have : " 
                if(service != "Google translate") 
                else "DO NOT DELETE YOUR COPY OF THE SERVICE JSON\n\nPlease enter the contents of the service json file (on one line): "
            )
                
            api_key = input(input_message).strip('"').strip("'").strip()

            ## preemptively save the api key for google translate
            if(service == "Google translate"):
                save_api_key(api_key)
                time.sleep(1)
                api_key = api_key_path

            try: 

                api_key_setter(service.lower(), api_key)

                is_valid, e = api_key_tester(service.lower())

                if(not is_valid and e is not None):
                    raise e
                
                save_api_key(api_key)
                
            ## if invalid key exit
            except (GoogleAuthError, OpenAIAuthenticationError, DeepLAuthorizationException):
                    
                Toolkit.clear_console()

                logging.error(f"Authorization error while setting up {service}, please double check your API key as it appears to be incorrect.") 

                Toolkit.pause_console()
                        
                exit(1)

            ## other error, alert user and raise it
            except Exception as e: 

                Toolkit.clear_console()
                        
                logging.error(f"Unknown error while setting up {service}, The error is as follows " + str(e)  + "\nThe exception will now be raised.")

                Toolkit.pause_console()

                raise e

##-------------------start-of-reset_static_variables()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def reset_static_variables() -> None:

        """

        Resets the static variables.
        Done to prevent issues with the webgui.

        """

        Translator.text_to_translate = []
        Translator.translated_text = []
        Translator.je_check_text = []
        Translator.error_text = []
        Translator.openai_translation_batches = []
        Translator.gemini_translation_batches = []
        Translator.deepl_translation_batches = []
        Translator.google_translate_translation_batches = []
        Translator.num_occurred_malformed_batches = 0
        Translator.translation_print_result = ""
        Translator.TRANSLATION_METHOD = "deepl"
        Translator.pre_provided_api_key = ""
        Translator.is_cli = False

##-------------------start-of-check-settings()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    async def check_settings() -> None:

        """

        Prompts the user to confirm the settings in the translation settings file.

        """

        print("Are these settings okay? (1 for yes or 2 for no):")

        method_to_section_dict = {
            "openai": ("openai settings", "OpenAI", FileEnsurer.openai_api_key_path),
            "gemini": ("gemini settings", "Gemini", FileEnsurer.gemini_api_key_path),
            "deepl": ("deepl settings", "DeepL", FileEnsurer.deepl_api_key_path),
            "google translate": (None, None, FileEnsurer.google_translate_service_key_json_path)
        }

        section_to_target, method_name, api_key_path = method_to_section_dict[Translator.TRANSLATION_METHOD]

        try:

            JsonHandler.log_translation_settings(output_to_console=True, specific_section=section_to_target)

        except:
            Toolkit.clear_console()

            if(input("It's likely that you're using an outdated version of the translation settings file, press 1 to reset these to default or 2 to exit and resolve manually : ") == "1"):
                Toolkit.clear_console()
                JsonHandler.reset_translation_settings_to_default()
                JsonHandler.load_translation_settings()

                print("Are these settings okay? (1 for yes or 2 for no) : \n")
                JsonHandler.log_translation_settings(output_to_console=True, specific_section=section_to_target)
            else:
                FileEnsurer.exit_kudasai()

        if(input("\n") != "1"):
            JsonHandler.change_translation_settings()

        Toolkit.clear_console()

        print("Do you want to change your API key? (1 for yes or 2 for no) : ")

        if(input("\n") == "1"):
            if(os.path.exists(api_key_path)):
                os.remove(api_key_path)
                await Translator.init_api_key(method_name, api_key_path, EasyTL.set_credentials, EasyTL.test_credentials)

        Toolkit.clear_console()

##-------------------start-of-commence_translation()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    async def commence_translation(is_webgui:bool=False) -> None:

        """

        Uses all the other functions to translate the text provided by Kudasai.

        Parameters:
        is_webgui (bool | optional | default=False) : A bool representing whether the function is being called by the webgui.

        """

        if(os.path.exists(FileEnsurer.external_translation_genders_path) and not is_webgui):
            logging.info("External genders.json file found, overriding config...")
            shutil.copy2(FileEnsurer.external_translation_genders_path, FileEnsurer.config_translation_genders_path)

        logging.debug(f"Translator Activated, Translation Method : {Translator.TRANSLATION_METHOD} "
                     f"Settings are as follows : ")
        
        JsonHandler.log_translation_settings()

        Translator.prompt_assembly_mode = int(JsonHandler.current_translation_settings["base translation settings"]["prompt_assembly_mode"])
        Translator.number_of_lines_per_batch = int(JsonHandler.current_translation_settings["base translation settings"]["number_of_lines_per_batch"])
        Translator.sentence_fragmenter_mode = int(JsonHandler.current_translation_settings["base translation settings"]["sentence_fragmenter_mode"])
        Translator.je_check_mode = int(JsonHandler.current_translation_settings["base translation settings"]["je_check_mode"])
        Translator.num_of_malform_retries = int(JsonHandler.current_translation_settings["base translation settings"]["number_of_malformed_batch_retries"])
        Translator.max_batch_duration = float(JsonHandler.current_translation_settings["base translation settings"]["batch_retry_timeout"])
        Translator.num_concurrent_batches = int(JsonHandler.current_translation_settings["base translation settings"]["number_of_concurrent_batches"])
        Translator.gender_context_insertion = bool(JsonHandler.current_translation_settings["base translation settings"]["gender_context_insertion"])
        Translator.is_cote = bool(JsonHandler.current_translation_settings["base translation settings"]["is_cote"])

        Translator._semaphore = asyncio.Semaphore(Translator.num_concurrent_batches)

        Translator.openai_model = JsonHandler.current_translation_settings["openai settings"]["openai_model"]
        Translator.openai_system_message = JsonHandler.current_translation_settings["openai settings"]["openai_system_message"]
        Translator.openai_temperature = float(JsonHandler.current_translation_settings["openai settings"]["openai_temperature"])
        Translator.openai_top_p = float(JsonHandler.current_translation_settings["openai settings"]["openai_top_p"])
        Translator.openai_n = int(JsonHandler.current_translation_settings["openai settings"]["openai_n"])
        Translator.openai_stream = bool(JsonHandler.current_translation_settings["openai settings"]["openai_stream"])
        Translator.openai_stop = JsonHandler.current_translation_settings["openai settings"]["openai_stop"]
        Translator.openai_logit_bias = JsonHandler.current_translation_settings["openai settings"]["openai_logit_bias"]
        Translator.openai_max_tokens = JsonHandler.current_translation_settings["openai settings"]["openai_max_tokens"]
        Translator.openai_presence_penalty = float(JsonHandler.current_translation_settings["openai settings"]["openai_presence_penalty"])
        Translator.openai_frequency_penalty = float(JsonHandler.current_translation_settings["openai settings"]["openai_frequency_penalty"])

        Translator.gemini_model = JsonHandler.current_translation_settings["gemini settings"]["gemini_model"]
        Translator.gemini_prompt = JsonHandler.current_translation_settings["gemini settings"]["gemini_prompt"]
        Translator.gemini_temperature = float(JsonHandler.current_translation_settings["gemini settings"]["gemini_temperature"])
        Translator.gemini_top_p = JsonHandler.current_translation_settings["gemini settings"]["gemini_top_p"]
        Translator.gemini_top_k = JsonHandler.current_translation_settings["gemini settings"]["gemini_top_k"]
        Translator.gemini_candidate_count = JsonHandler.current_translation_settings["gemini settings"]["gemini_candidate_count"]
        Translator.gemini_stream = bool(JsonHandler.current_translation_settings["gemini settings"]["gemini_stream"])
        Translator.gemini_stop_sequences = JsonHandler.current_translation_settings["gemini settings"]["gemini_stop_sequences"]
        Translator.gemini_max_output_tokens = JsonHandler.current_translation_settings["gemini settings"]["gemini_max_output_tokens"]

        Translator.deepl_context = JsonHandler.current_translation_settings["deepl settings"]["deepl_context"]
        Translator.deepl_split_sentences = JsonHandler.current_translation_settings["deepl settings"]["deepl_split_sentences"]
        Translator.deepl_preserve_formatting = JsonHandler.current_translation_settings["deepl settings"]["deepl_preserve_formatting"]
        Translator.deepl_formality = JsonHandler.current_translation_settings["deepl settings"]["deepl_formality"]

        exception_dict = {
            "openai": (OpenAIAuthenticationError, OpenAIInternalServerError, OpenAIRateLimitError, OpenAIAPITimeoutError, OpenAIAPIConnectionError, OpenAIAPIStatusError),
            "gemini": GoogleAPIError,
            "deepl": DeepLException,
            "google translate": GoogleAPIError
        }
        
        Translator.decorator_to_use = backoff.on_exception(
            backoff.expo,
            max_time=lambda: Translator.get_max_batch_duration(),
            exception=exception_dict.get(Translator.TRANSLATION_METHOD, None),
            on_backoff=lambda details: Translator.log_retry(details),
            on_giveup=lambda details: Translator.log_failure(details),
            raise_on_giveup=False
        )

        Toolkit.clear_console()

        logging.info("Starting Prompt Building...")

        Translator.build_translation_batches()
        
        translation_methods = {
            "openai": JsonHandler.current_translation_settings["openai settings"]["openai_model"],
            "gemini": JsonHandler.current_translation_settings["gemini settings"]["gemini_model"],
            "deepl": "deepl",
            "google translate": "google translate"
        }
        
        model = translation_methods[Translator.TRANSLATION_METHOD]

        await Translator.handle_cost_estimate_prompt(model, omit_prompt=is_webgui or Translator.is_cli)

        Toolkit.clear_console()

        logging.info("Starting Translation...")

        ## requests to run asynchronously
        async_requests = Translator.build_async_requests(model)

        ## Use asyncio.gather to run tasks concurrently/asynchronously and wait for all of them to complete
        results = await asyncio.gather(*async_requests)

        logging.info("Redistributing Translated Text...")

        ## Sort results based on the index to maintain order
        sorted_results = sorted(results, key=lambda x: x[0])

        ## Redistribute the sorted results
        for _, translated_prompt, translated_message in sorted_results:
            Translator.redistribute(translated_prompt, translated_message)

        ## try to pair the text for j-e checking if the mode is 2
        if(Translator.je_check_mode == 2):
            Translator.je_check_text = Translator.fix_je()

        Toolkit.clear_console()

        logging.info("Done!")

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
        logging_message = "Built Messages: \n\n"

        translation_batches_methods = {
            method_name: getattr(Translator, f"{method_name}_translation_batches" if method_name != "google translate" else "google_translate_translation_batches")
            for method_name in ["openai", "gemini", "deepl", "google translate"]
        }

        translation_batches = translation_batches_methods[Translator.TRANSLATION_METHOD]
        batch_length = len(translation_batches)

        ## if openai/gemini which are llm, they have the instructions/prompt format
        if(Translator.TRANSLATION_METHOD not in ["deepl", "google translate"]):
            for batch_number, (instructions, prompt) in enumerate(zip(translation_batches[::2], translation_batches[1::2]), start=1):
                assert isinstance(instructions, (SystemTranslationMessage, str))
                assert isinstance(prompt, (ModelTranslationMessage, str))

                if(Translator.gender_context_insertion):
                    assumption = list(set(GenderUtil.get_gender_assumption_for_system_prompt(prompt if isinstance(prompt, str) else prompt.content)))
                    assumption_string = "Additional Information:\nCharacter Genders:\n" + "".join(assumption) if len(assumption) > 0 else ""
                    instructions = SystemTranslationMessage(content=f"{instructions.content if isinstance(instructions, Message) else instructions}\n{assumption_string}")

                logging_message += f"\n------------------------\n{instructions.content if isinstance(instructions, Message) else instructions}\n{prompt if isinstance(prompt, str) else prompt.content}"
                async_requests.append(Translator.handle_translation(model, batch_number, batch_length//2, prompt, instructions))
        
        ## if deepl/google translate, they only have the prompt
        else:
            for batch_number, batch in enumerate(translation_batches, start=1):
                assert isinstance(batch, str)
                logging_message += f"\n------------------------\n{batch}"
                async_requests.append(Translator.handle_translation(model, batch_number, batch_length, batch, None))

        logging.debug(logging_message)
        
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
        special_chars = ["▼", "△", "◇"]
        quotes = ["「", "」", "『", "』", "【", "】", "\"", "'"]
        part_chars = ["１","２","３","４","５","６","７","８","９", " "]
        
        while(index < len(Translator.text_to_translate)):

            sentence = Translator.text_to_translate[index].strip()
            lowercase_sentence = sentence.lower()
        
            has_quotes = any(char in sentence for char in quotes)
            is_part_in_sentence = "part" in lowercase_sentence
            is_special_char = any(char in sentence for char in special_chars)
            is_part_char = all(char in sentence for char in part_chars)
        
            if(len(prompt) < Translator.number_of_lines_per_batch):
                if(is_special_char or is_part_in_sentence or is_part_char):
                    prompt.append(f'{sentence}\n')
                    logging.debug(f"Sentence : {sentence} Sentence is a pov change or part marker... adding to prompt.")

                elif(non_word_pattern.match(sentence) or KatakanaUtil.is_punctuation(sentence) and not has_quotes):
                    logging.debug(f"Sentence : {sentence} Sentence is punctuation or spacing... skipping.")

                elif(sentence):
                    prompt.append(f'{sentence}\n')
                    logging.debug(f"Sentence : {sentence} Sentence is a valid sentence... adding to prompt.")
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

        while i < len(Translator.text_to_translate):

            batch, i = Translator.generate_text_to_translate_batches(i)
            batch = ''.join(batch)

            if(Translator.TRANSLATION_METHOD == 'openai'):

                if(Translator.prompt_assembly_mode == 1):
                    system_msg = SystemTranslationMessage(content=str(Translator.openai_system_message))
                else:
                    system_msg = SystemTranslationMessage(content=str(Translator.openai_system_message))

                Translator.openai_translation_batches.append(system_msg)
                model_msg = ModelTranslationMessage(content=batch)
                Translator.openai_translation_batches.append(model_msg)

            elif(Translator.TRANSLATION_METHOD == 'gemini'):
                Translator.gemini_translation_batches.append(Translator.gemini_prompt)
                Translator.gemini_translation_batches.append(batch)

            elif(Translator.TRANSLATION_METHOD == 'deepl'):
                Translator.deepl_translation_batches.append(batch)

            elif(Translator.TRANSLATION_METHOD == 'google translate'):
                Translator.google_translate_translation_batches.append(batch)

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

        translation_instructions_methods = {
            "openai": Translator.openai_system_message,
            "gemini": Translator.gemini_prompt,
            "deepl": None,
            "google translate": None
        }
        
        translation_instructions = translation_instructions_methods[Translator.TRANSLATION_METHOD]

        ## get cost estimate and confirm
        num_entities, min_cost, model = EasyTL.calculate_cost(text=Translator.text_to_translate, service=Translator.TRANSLATION_METHOD, model=model,translation_instructions=translation_instructions)

        print("Note that the cost estimate is not always accurate, and may be higher than the actual cost. However cost calculation now includes output tokens.\n")

        if(Translator.TRANSLATION_METHOD == "gemini"):
            logging.info(f"As of Kudasai {Toolkit.CURRENT_VERSION}, Gemini Pro 1.0 is free to use under 15 requests per minute, Gemini Pro 1.5 is free to use under 2 requests per minute. Requests correspond to number_of_current_batches in the translation settings.")
        
        entity_word = "tokens" if Translator.TRANSLATION_METHOD in ["openai", "gemini"] else "characters"

        logging.info(f"Estimated number of {entity_word} : " + str(num_entities))
        logging.info("Estimated minimum cost : " + str(min_cost) + " USD")

        if(not omit_prompt):
            if(input("\nContinue? (1 for yes or 2 for no) : ") == "1"):
                logging.info("User confirmed translation.")

            else:
                logging.info("User cancelled translation.")
                FileEnsurer.exit_kudasai()

        return model
    
##-------------------start-of-handle_translation()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    async def handle_translation(model:str, 
                                 batch_number:int,
                                 length_of_batch:int, 
                                 text_to_translate:typing.Union[str, ModelTranslationMessage],
                                 translation_instructions:typing.Union[str, SystemTranslationMessage, None]) -> tuple[int, str, str]: 

        """

        Handles the translation requests for the specified service.

        Parameters:
        model (string) : The model of the service used to translate the text.
        batch_number (int) : Which batch we are currently on.
        length_of_batch (int) : How long the batches are.
        text_to_translate (typing.Union[str, ModelTranslationMessage]) : The text to translate.
        translation_instructions (typing.Union[str, SystemTranslationMessage, None]) : The translation instructions.

        Returns:
        batch_number (int) : The batch index.
        text_to_translate (str) : The text to translate.
        translated_text (str) : The translated text

        """

        ## Basically limits the number of concurrent batches
        async with Translator._semaphore:
            num_tries = 0

            while True:

                ## For the webgui
                if(FileEnsurer.do_interrupt == True):
                    raise Exception("Interrupted by user.")
                
                logging.info(f"Trying translation for batch {batch_number} of {length_of_batch}...")

                try:

                    translation_methods = {
                        "openai": EasyTL.openai_translate_async,
                        "gemini": EasyTL.gemini_translate_async,
                        "deepl": EasyTL.deepl_translate_async,
                        "google translate": EasyTL.googletl_translate_async
                    }
                    
                    translation_params = {
                        "openai": {
                            "text": text_to_translate,
                            "decorator": Translator.decorator_to_use,
                            "translation_instructions": translation_instructions,
                            "model": model,
                            "temperature": Translator.openai_temperature,
                            "top_p": Translator.openai_top_p,
                            "stop": Translator.openai_stop,
                            "max_tokens": Translator.openai_max_tokens,
                            "presence_penalty": Translator.openai_presence_penalty,
                            "frequency_penalty": Translator.openai_frequency_penalty
                        },
                        "gemini": {
                            "text": text_to_translate,
                            "decorator": Translator.decorator_to_use,
                            "model": model,
                            "temperature": Translator.gemini_temperature,
                            "top_p": Translator.gemini_top_p,
                            "top_k": Translator.gemini_top_k,
                            "stop_sequences": Translator.gemini_stop_sequences,
                            "max_output_tokens": Translator.gemini_max_output_tokens
                        },
                        "deepl": {
                            "text": text_to_translate,
                            "decorator": Translator.decorator_to_use,
                            "context": Translator.deepl_context,
                            "split_sentences": Translator.deepl_split_sentences,
                            "preserve_formatting": Translator.deepl_preserve_formatting,
                            "formality": Translator.deepl_formality
                        },
                        "google translate": {
                            "text": text_to_translate,
                            "decorator": Translator.decorator_to_use
                        }
                    }
                    
                    assert isinstance(text_to_translate, ModelTranslationMessage if Translator.TRANSLATION_METHOD == "openai" else str)
                    
                    translated_message = await translation_methods[Translator.TRANSLATION_METHOD](**translation_params[Translator.TRANSLATION_METHOD])

                ## will only occur if the max_batch_duration is exceeded, so we just return the untranslated text
                except MaxBatchDurationExceededException:

                    logging.error(f"Batch {batch_number} of {length_of_batch} was not translated due to exceeding the max request duration, returning the untranslated text...")
                    break

                ## do not even bother if not a gpt 4 model, because gpt-3 seems unable to format properly
                ## since gemini is free, we can just try again if it's malformed
                ## deepl should produce properly formatted text so we don't need to check
                if("gpt-4" not in model and Translator.TRANSLATION_METHOD == "openai"):
                    break

                if(await Translator.check_if_translation_is_good(translated_message, text_to_translate)): # type: ignore
                    break

                if(num_tries >= Translator.num_of_malform_retries):
                    logging.warning(f"Batch {batch_number} of {length_of_batch} was malformed but exceeded the max number of retries ({Translator.num_of_malform_retries})")
                    break

                else:
                    num_tries += 1
                    logging.warning(f"Batch {batch_number} of {length_of_batch} was malformed, retrying...")
                    Translator.num_occurred_malformed_batches += 1

            if(isinstance(text_to_translate, ModelTranslationMessage)):
                text_to_translate = text_to_translate.content

            if(isinstance(translated_message, typing.List)):
                translated_message = ''.join(translated_message) # type: ignore

            logging.info(f"Translation for batch {batch_number} of {length_of_batch} completed.")

            return batch_number, text_to_translate, translated_message # type: ignore
    
##-------------------start-of-check_if_translation_is_good()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    async def check_if_translation_is_good(translated_message:typing.Union[typing.List[str], str], text_to_translate:typing.Union[ModelTranslationMessage, str]) -> bool:

        """
        
        Checks if the translation is good, i.e. the number of lines in the prompt and the number of lines in the translated message are the same.

        Parameters:
        translated_message (str) : the translated message.
        text_to_translate (typing.Union[str, Message]) : the translation prompt.

        Returns:
        is_valid (bool) : whether or not the translation is valid.

        """

        if(not isinstance(text_to_translate, str)):
            prompt = text_to_translate.content

        else:
            prompt = text_to_translate

        if(isinstance(translated_message, list)):
            translated_message = ''.join(translated_message)
            
        jap = [line for line in prompt.split('\n') if line.strip()]  ## Remove blank lines
        eng = [line for line in translated_message.split('\n') if line.strip()]  ## Remove blank lines
    
        return len(jap) == len(eng)
    
##-------------------start-of-redistribute()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def redistribute(text_to_translate:typing.Union[Message, str], translated_message:str) -> None:

        """

        Puts translated text back into the text file.

        Parameters:
        text_to_translate (typing.Union[str, Message]) : the translation prompt.
        translated_message (str) : the translated message.

        """

        if(not isinstance(text_to_translate, str)):
            prompt = text_to_translate.content

        else:
            prompt = text_to_translate

        ## Separates with hyphens if the mode is 1 
        if(Translator.je_check_mode == 1):

            Translator.je_check_text.append("\n-------------------------\n"+ prompt + "\n\n")
            Translator.je_check_text.append(translated_message + '\n')
        
        ## Mode two tries to pair the text for j-e checking, see fix_je() for more details
        elif(Translator.je_check_mode == 2):
            Translator.je_check_text.append(prompt)
            Translator.je_check_text.append(translated_message)

        ## mode 1 is the default mode, uses regex and other nonsense to split sentences
        if(Translator.sentence_fragmenter_mode == 1): 

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

                Translator.translated_text.append(sentence + '\n')

            for i in range(len(Translator.translated_text)):
                if Translator.translated_text[i] in patched_sentences:
                    index = patched_sentences.index(Translator.translated_text[i])
                    Translator.translated_text[i] = patched_sentences[index]

        ## mode 2 just assumes the translation method formatted it properly
        elif(Translator.sentence_fragmenter_mode == 2):
            
            Translator.translated_text.append(translated_message + '\n\n')
        
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

        while(i < len(Translator.je_check_text)):
            jap = Translator.je_check_text[i-1].split('\n')
            eng = Translator.je_check_text[i].split('\n')

            jap = [line for line in jap if(line.strip())]  # Remove blank lines
            eng = [line for line in eng if(line.strip())]  # Remove blank lines    

            final_list.append("-------------------------\n")

            if(len(jap) == len(eng)):
                for(jap_line, eng_line) in zip(jap, eng):
                    if(jap_line and eng_line):  # check if jap_line and eng_line aren't blank
                        final_list.append(jap_line + '\n\n')
                        final_list.append(eng_line + '\n\n')
                        final_list.append("--------------------------------------------------\n")
            else:
                final_list.append(Translator.je_check_text[i-1] + '\n\n')
                final_list.append(Translator.je_check_text[i] + '\n\n')
                final_list.append("--------------------------------------------------\n")

            i += 2

        return final_list
    
##-------------------start-of-assemble_results()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def assemble_results(time_start:float, time_end:float) -> None:

        """

        Generates the Translator translation print result, does not directly output/return, but rather sets Translator.translation_print_result to the output.

        Parameters:
        time_start (float) : When the translation started.
        time_end (float) : When the translation finished.

        """

        result = (
            f"Time Elapsed : {Toolkit.get_elapsed_time(time_start, time_end)}\n"
            f"Number of malformed batches : {Translator.num_occurred_malformed_batches}\n\n"
            f"Debug text have been written to : {FileEnsurer.debug_log_path}\n"
            f"J->E text have been written to : {FileEnsurer.je_check_path}\n"
            f"Translated text has been written to : {FileEnsurer.translated_text_path}\n"
            f"Errors have been written to : {FileEnsurer.error_log_path}\n"
        )
        
        Translator.translation_print_result = result

##-------------------start-of-write_translator_results()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    @permission_error_decorator()
    def write_translator_results() -> None:

        """
        
        This function is called to write the results of the Translator module to the output directory.

        """

        ## ensures the output directory exists, cause it could get moved or fucked with.
        FileEnsurer.standard_create_directory(FileEnsurer.output_dir)

        with open(FileEnsurer.error_log_path, 'a+', encoding='utf-8') as file:
            file.writelines(Translator.error_text)

        with open(FileEnsurer.je_check_path, 'w', encoding='utf-8') as file:
            file.writelines(Translator.je_check_text)

        with open(FileEnsurer.translated_text_path, 'w', encoding='utf-8') as file:
            file.writelines(Translator.translated_text)

        ## Instructions to create a copy of the output for archival
        FileEnsurer.standard_create_directory(FileEnsurer.archive_dir)

        timestamp = Toolkit.get_timestamp(is_archival=True)

        list_of_result_tuples = [('kudasai_translated_text', Translator.translated_text), 
                                 ('kudasai_je_check_text', Translator.je_check_text), 
                                 ('kudasai_error_log', Translator.error_text),
                                 ('debug_log', FileEnsurer.standard_read_file(FileEnsurer.debug_log_path))]

        FileEnsurer.archive_results(list_of_result_tuples, 
                                    module='translator', timestamp=timestamp)