## built-in libraries
from __future__ import annotations ## used for cheating the circular import issue that occurs when i need to type check some things

import base64
import re
import os
import time
import typing
import asyncio


## third party modules
from aiohttp import ClientSession

import openai
import backoff
import tiktoken
import spacy

from openai.error import APIConnectionError, APIError, AuthenticationError, ServiceUnavailableError, RateLimitError, Timeout

## custom modules
from handlers.json_handler import JsonHandler
from modules.file_ensurer import FileEnsurer
from modules.logger import Logger

from .Kijiku import Kijiku

if(typing.TYPE_CHECKING): ## used for cheating the circular import issue that occurs when i need to type check some things
    from modules.toolkit import Toolkit


##-------------------start-of-Kijiku--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Kijiku:

    """
    
    Kijiku is a secondary class that is used to interact with the OpenAI API and translates the text by batch.
    
    """
    
    ## the text to translate
    text_to_translate =  []

    ## the translated text
    translated_text = []

    ## the text for j-e checking
    je_check_text = []

    ## the text for errors that occur during translation
    error_text = []

    ## the messages that will be sent to the api, contains a system message and a model message, system message is the instructions,
    ## model message is the text that will be translated  
    translation_batches = []

    ##--------------------------------------------------------------------------------------------------------------------------

    translation_print_result = ""

    ##--------------------------------------------------------------------------------------------------------------------------

    MODEL = ""
    translation_instructions = ""
    message_mode = 0 
    prompt_size = 0
    sentence_fragmenter_mode = 0
    je_check_mode = 0

##-------------------start-of-translate()--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    async def translate() -> None:

        """

        Translate the text in the file at the path given.

        """

        ## ngl i have basically no idea what this does, but it's needed for openai async to work
        openai.aiosession.set(ClientSession())

        ## set this here cause the try-except could throw before we get past the settings configuration
        time_start = time.time()

        try:
        
            await Kijiku.initialize()

            JsonHandler.validate_json()

            Kijiku.check_settings()

            ## set actual start time to the end of the settings configuration
            time_start = time.time()

            await Kijiku.commence_translation()

        except Exception as e:
            
            Kijiku.translation_print_result += "An error has occurred, outputting results so far..."

            FileEnsurer.handle_critical_exception(e)

        finally:

            time_end = time.time() 

            Kijiku.assemble_results(time_start, time_end)

            ## more session stuff that i don't understand
            session = openai.aiosession.get()

            if(session):
                await session.close()

##-------------------start-of-initialize()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    async def initialize() -> None:

        """

        Sets the open api key.
    
        """

        ## get saved api key if exists
        try:
            with open(FileEnsurer.openai_api_key_path, 'r', encoding='utf-8') as file: 
                api_key = base64.b64decode((file.read()).encode('utf-8')).decode('utf-8')

            openai.api_key = api_key

            ## make dummy request to check if api key is valid
            await openai.Completion.acreate(
                engine="davinci",
                prompt="This is a test.",
                max_tokens=5
            )
        
            print("Used saved api key in " + FileEnsurer.openai_api_key_path)
            Logger.log_action("Used saved api key in " + FileEnsurer.openai_api_key_path)

        ## else try to get api key manually
        except:

            Toolkit.clear_console()
                
            api_key = input("DO NOT DELETE YOUR COPY OF THE API KEY\n\nPlease enter the openapi key you have : ")

            ## if valid save the api key
            try: 

                openai.api_key = api_key

                ## make dummy request to check if api key is valid
                await openai.Completion.acreate(
                    engine="davinci",
                    prompt="This is a test.",
                    max_tokens=5
                )

                FileEnsurer.standard_overwrite_file(FileEnsurer.openai_api_key_path, base64.b64encode(api_key.encode('utf-8')).decode('utf-8'), omit=True)
                
            ## if invalid key exit
            except AuthenticationError: 
                    
                Toolkit.clear_console()
                        
                print("Authorization error with setting up openai, please double check your api key as it appears to be incorrect.\n")
                Logger.log_action("Authorization error with setting up openai, please double check your api key as it appears to be incorrect.\n")

                Toolkit.pause_console()
                        
                exit()

            ## other error, alert user and raise it
            except Exception as e: 

                Toolkit.clear_console()
                        
                print("Unknown error with setting up openai, The error is as follows " + str(e)  + "\nThe exception will now be raised.\n")
                Logger.log_action("Unknown error with setting up openai, The error is as follows " + str(e)  + "\nThe exception will now be raised.\n")

                Toolkit.pause_console()

                raise e
            
        ## try to load the kijiku rules
        try: 

            JsonHandler.load_kijiku_rules()

        ## if the kijiku rules don't exist, create them
        except: 
            
            JsonHandler.reset_kijiku_rules_to_default()

            JsonHandler.load_kijiku_rules()
            
        Toolkit.clear_console()

##-------------------start-of-check-settings()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def check_settings() -> None:

        """

        Prompts the user to confirm the settings in the kijiku rules file.\n

        """

        print("Are these settings okay? (1 for yes or 2 for no) : \n\n")

        ## Reset settings to default if the json is botched
        if("open ai settings" not in JsonHandler.current_kijiku_rules):
            JsonHandler.reset_kijiku_rules_to_default()

        for key, value in JsonHandler.current_kijiku_rules["open ai settings"].items():
            print(key + " : " + str(value))

        if(input("\n") == "1"):
            pass
        else:
            JsonHandler.change_kijiku_settings()

        Toolkit.clear_console()

##-------------------start-of-commence_translation()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    async def commence_translation() -> None:

        """

        Uses all the other functions to translate the text provided by Kudasai.\n

        """
        
        Logger.log_action("-------------------------")
        Logger.log_action("Kijiku Activated, Settings are as follows : ")
        Logger.log_action("-------------------------")

        for key,value in JsonHandler.current_kijiku_rules["open ai settings"].items():
            Logger.log_action(key + " : " + str(value))

        Kijiku.MODEL = JsonHandler.current_kijiku_rules["open ai settings"]["model"]
        Kijiku.translation_instructions = JsonHandler.current_kijiku_rules["open ai settings"]["system_message"]
        Kijiku.message_mode = int(JsonHandler.current_kijiku_rules["open ai settings"]["message_mode"])
        Kijiku.prompt_size = int(JsonHandler.current_kijiku_rules["open ai settings"]["num_lines"])
        Kijiku.sentence_fragmenter_mode = int(JsonHandler.current_kijiku_rules["open ai settings"]["sentence_fragmenter_mode"])
        Kijiku.je_check_mode = int(JsonHandler.current_kijiku_rules["open ai settings"]["je_check_mode"])

        Toolkit.clear_console()

        Logger.log_action("-------------------------")
        Logger.log_action("Starting Prompt Building")
        Logger.log_action("-------------------------")

        Kijiku.build_translation_batches()

        cost = Kijiku.estimate_cost()

        print(cost)

        await asyncio.sleep(7)

        Logger.log_action("Starting Translation")
        print("Starting Translation...\n\n")

        ## requests to run asynchronously
        async_requests = []
        length = len(Kijiku.translation_batches)

        for i in range(0, length, 2):
            async_requests.append(Kijiku.handle_translation(i, length, Kijiku.translation_batches[i], Kijiku.translation_batches[i+1]))

        ## Use asyncio.gather to run tasks concurrently/asynchronously and wait for all of them to complete
        results = await asyncio.gather(*async_requests)

        print("\n\nTranslation Complete!\n\n")
        Logger.log_action("Translation Complete!")

        print("Starting Redistribution...\n\n")
        Logger.log_action("Starting Redistribution...")

        ## Sort results based on the index to maintain order
        sorted_results = sorted(results, key=lambda x: x[0])

        ## Redistribute the sorted results
        for index, translated_prompt, translated_message in sorted_results:
            Kijiku.redistribute(translated_prompt, translated_message)

        ## try to pair the text for j-e checking if the mode is 2
        if(Kijiku.je_check_mode == 2):
            Kijiku.je_check_text = Kijiku.fix_je()

        Toolkit.clear_console()

        print("Done!\n\n")
        Logger.log_action("Done!")

##-------------------start-of-generate_prompt()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def generate_prompt(index:int) -> tuple[typing.List[str],int]:

        """

        Generates prompts for the messages meant for the ai.

        Parameters:
        index (int) an int representing where we currently are in the text file.

        Returns:
        prompt (list - string) a list of japanese lines that will be assembled into messages.
        index (int) an updated int representing where we currently are in the text file.

        """

        prompt = []

        while(index < len(Kijiku.text_to_translate)):
            sentence = Kijiku.text_to_translate[index]

            if(len(prompt) < Kijiku.prompt_size):

                if(any(char in sentence for char in ["▼", "△", "◇"])):
                    prompt.append(sentence + '\n')
                    Logger.log_action("Sentence : " + sentence + ", Sentence is a pov change... leaving intact.\n")

                elif("part" in sentence.lower() or all(char in ["１","２","３","４","５","６","７","８","９", " "] for char in sentence) and not all(char in [" "] for char in sentence)):
                    prompt.append(sentence + '\n') 
                    Logger.log_action("Sentence : " + sentence + ", Sentence is part marker... leaving intact.\n")

                elif(bool(re.match(r'^[\W_\s\n-]+$', sentence)) and not any(char in sentence for char in ["」", "「", "«", "»",'"','"'])):
                    Logger.log_action("Sentence : " + sentence + ", Sentence is punctuation... skipping.\n")
            
                elif(bool(re.match(r'^[A-Za-z0-9\s\.,\'\?!]+\n*$', sentence) and "part" not in sentence.lower())):
                    Logger.log_action("Sentence is empty... skipping translation.\n")

                else:
                    prompt.append(sentence + "\n")
    
            else:
                return prompt, index
            
            index += 1

        return prompt, index
    
##-------------------start-of-build_translation_batches()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def build_translation_batches() -> None:

        """

        Builds translations batches dict for ai prompt.
        
        """

        i = 0

        while i < len(Kijiku.text_to_translate):
            prompt, i = Kijiku.generate_prompt(i)

            prompt = ''.join(prompt)

            if(Kijiku.message_mode == 1):
                system_msg = {}
                system_msg["role"] = "system"
                system_msg["content"] = Kijiku.translation_instructions

            else:
                system_msg = {}
                system_msg["role"] = "user"
                system_msg["content"] = Kijiku.translation_instructions

            Kijiku.translation_batches.append(system_msg)

            model_msg = {}
            model_msg["role"] = "user"
            model_msg["content"] = prompt

            Kijiku.translation_batches.append(model_msg)

        Logger.log_action("Built Messages : ")
        Logger.log_action("-------------------------")

        i = 0

        for message in Kijiku.translation_batches:

            i+=1

            if(i % 2 == 0):

                Logger.log_action(str(message))
        
            else:

                Logger.log_action(str(message))
                Logger.log_action("-------------------------")

##-------------------start-of-estimate_cost()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def estimate_cost() -> str:

        """

        Attempts to estimate cost.

        """
        
        try:
            encoding = tiktoken.encoding_for_model(Kijiku.MODEL)
            
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")

        if(Kijiku.MODEL == "gpt-3.5-turbo"):
            print("Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
            time.sleep(1)
            Kijiku.MODEL="gpt-3.5-turbo-0613"
            return Kijiku.estimate_cost()
        
        elif(Kijiku.MODEL == "gpt-3.5-turbo-0301"):
            print("Warning: gpt-3.5-turbo-0301 is outdated. gpt-3.5-turbo-0301's support ended September 13, Returning num tokens assuming gpt-3.5-turbo-0613.")
            time.sleep(1)
            Kijiku.MODEL="gpt-3.5-turbo-0613"
            return Kijiku.estimate_cost()

        elif(Kijiku.MODEL == "gpt-4"):
            print("Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-0613.")
            time.sleep(1)
            Kijiku.MODEL="gpt-4-0613"
            return Kijiku.estimate_cost()
        
        elif(Kijiku.MODEL == "gpt-4-0314"):
            print("Warning: gpt-4-0314 is outdated. gpt-4-0314's support ended September 13, Returning num tokens assuming gpt-4-0613.")
            time.sleep(1)
            Kijiku.MODEL="gpt-4-0613"
            return Kijiku.estimate_cost()
        
        elif(Kijiku.MODEL == "gpt-3.5-turbo-0613"):
            cost_per_thousand_tokens = 0.0015
            tokens_per_message = 4  ## every message follows <|start|>{role/name}\n{content}<|end|>\n
            tokens_per_name = -1  ## if there's a name, the role is omitted

        elif(Kijiku.MODEL == "gpt-4-0613"):
            cost_per_thousand_tokens = 0.06
            tokens_per_message = 3
            tokens_per_name = 1

        else:
            raise NotImplementedError(f"""Kudasai does not support : {Kijiku.MODEL}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
        
        num_tokens = 0

        for message in Kijiku.translation_batches:

            num_tokens += tokens_per_message

            for key, value in message.items():

                num_tokens += len(encoding.encode(value))

                if(key == "name"):
                    num_tokens += tokens_per_name

        num_tokens += 3  ## every reply is primed with <|start|>assistant<|message|>
        min_cost = round((float(num_tokens) / 1000.00) * cost_per_thousand_tokens, 5)

        estimate_cost_result = "Estimated Tokens in Messages : " + str(num_tokens) + ", Estimated Minimum Cost : $" + str(min_cost) + "\n"

        Logger.log_action(estimate_cost_result)
        Logger.log_action("-------------------------")

        return estimate_cost_result
    
##-------------------start-of-translate_message()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    ## backoff wrapper for retrying on errors
    @backoff.on_exception(backoff.expo, (ServiceUnavailableError, RateLimitError, Timeout, APIError, APIConnectionError),on_backoff=Kijiku.log_retry)
    @staticmethod
    async def translate_message(translation_instructions:dict, translation_prompt:dict) -> str:

        """

        Translates system and user message.

        Parameters:
        translation_instructions (dict) : the system message also known as the instructions.
        translation_prompt (dict) : the user message also known as the prompt.

        Returns:
        output (string) a string that gpt gives to us also known as the translation.\n

        """

        ## max_tokens and logit bias are currently excluded due to a lack of need, and the fact that i am lazy

        response = await openai.ChatCompletion.acreate(
            model=Kijiku.MODEL,
            messages=[
                translation_instructions,
                translation_prompt,
            ],

            temperature = float(JsonHandler.current_kijiku_rules["open ai settings"]["temp"]),
            top_p = float(JsonHandler.current_kijiku_rules["open ai settings"]["top_p"]),
            n = int(JsonHandler.current_kijiku_rules["open ai settings"]["top_p"]),
            stream = JsonHandler.current_kijiku_rules["open ai settings"]["stream"],
            stop = JsonHandler.current_kijiku_rules["open ai settings"]["stop"],
            presence_penalty = float(JsonHandler.current_kijiku_rules["open ai settings"]["presence_penalty"]),
            frequency_penalty = float(JsonHandler.current_kijiku_rules["open ai settings"]["frequency_penalty"]),

        )

        ## note, pylance flags this as a 'GeneralTypeIssue', however i see nothing wrong with it, and it works fine
        output = response['choices'][0]['message']['content'] ## type: ignore
        
        return output
    
##-------------------start-of-handle_translation()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    async def handle_translation(index:int, length:int, translation_instructions:dict, translation_prompt:dict) -> tuple[int, dict, str]:

        """

        Handles the translation for a given system and user message.

        Parameters:\n
        index (int) : the index of the message in the original list.
        translation_instructions (dict) : the system message also known as the instructions.
        translation_prompt (dict) : the user message also known as the prompt.

        Returns:\n
        index (int) : the index of the message in the original list.
        translation_prompt (dict) : the user message also known as the prompt.
        translated_message (str) : the translated message.

        """

        translated_message = ""
        NUM_TRIES_ALLOWED = 1
        num_tries = 0

        while True:
        
            message_number = (index // 2) + 1
            print(f"Trying translation for batch {message_number} of {length//2}...")
            Logger.log_action(f"Trying translation for batch {message_number} of {length//2}...")

            translated_message = await Kijiku.translate_message(translation_instructions, translation_prompt)

            if(Kijiku.MODEL != "gpt-4-0613"):
                break

            if(await Kijiku.check_if_translation_is_good(translated_message, translation_prompt) or num_tries >= NUM_TRIES_ALLOWED):
                break

            else:
                num_tries += 1
                print(f"Batch {message_number} of {length//2} was malformed, retrying...")
                Logger.log_action(f"Batch {message_number} of {length//2} was malformed, retrying...")

        print(f"Translation for batch {message_number} of {length//2} successful!")
        Logger.log_action(f"Translation for batch {message_number} of {length//2} successful!")

        return index, translation_prompt, translated_message
    
##-------------------start-of-check_if_translation_is_good()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    async def check_if_translation_is_good(translated_message:str, translation_prompt:dict):

        """
        
        Checks if the translation is good, i.e. the number of lines in the prompt and the number of lines in the translated message are the same.

        Parameters:
        translated_message (string) : the translated message.
        translation_prompt (dict) : the user message also known as the prompt.

        Returns:
        is_valid (bool) : whether or not the translation is valid.

        """

        prompt = translation_prompt["content"]
        is_valid = False

        jap = [line for line in prompt.split('\n') if line.strip()]  ## Remove blank lines
        eng = [line for line in translated_message.split('\n') if line.strip()]  ## Remove blank lines

        if(len(jap) == len(eng)):
            is_valid = True
    
        return is_valid
    
##-------------------start-of-log_retry()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def log_retry(details):

        """

        Logs the retry message.

        Parameters:\n
        details (dict) : the details of the retry.

        """

        retry_msg = f"Backing off {details['wait']} seconds after {details['tries']} tries calling function {details['target']} due to {details['value']}."
        Logger.log_action(retry_msg)


##-------------------start-of-redistribute()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def redistribute(translation_prompt:dict, translated_message:str) -> None:

        """

        Puts translated text back into the text file.

        Parameters:
        Kijiku (object - Kijiku) : the Kijiku object.
        translated_message (string) : the translated message.

        """

        if(Kijiku.je_check_mode == 1):
            Kijiku.je_check_text.append("\n-------------------------\n"+ str(translation_prompt["content"]) + "\n\n")
            Kijiku.je_check_text.append(translated_message + '\n')
        elif(Kijiku.je_check_mode == 2):
            Kijiku.je_check_text.append(str(translation_prompt["content"]))
            Kijiku.je_check_text.append(translated_message)

        ## mode 1 is the default mode, uses regex and other nonsense to split sentences
        if(Kijiku.sentence_fragmenter_mode == 1): 

            sentences = re.findall(r"(.*?(?:(?:\"|\'|-|~|!|\?|%|\(|\)|\.\.\.|\.|---|\[|\])))(?:\s|$)", translated_message)

            patched_sentences = []
            build_string = None

            for sentence in sentences:
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

        ## mode 2 uses spacy to split sentences
        elif(Kijiku.sentence_fragmenter_mode == 2): 

            nlp = spacy.load("en_core_web_lg")

            doc = nlp(translated_message)
            sentences = [sent.text for sent in doc.sents]

            for sentence in sentences:
                Kijiku.translated_text.append(sentence + '\n')

        ## mode 3 just assumes gpt formatted it properly
        elif(Kijiku.sentence_fragmenter_mode == 3): 
            
            Kijiku.translated_text.append(translated_message + '\n\n')
        
##-------------------start-of-fix_je()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def fix_je() -> typing.List[str]:

        """

        Fixes the J->E text to be more j-e check friendly.\n

        Note that fix_je() is not always accurate, and may use standard j-e formatting instead of the corrected formatting.\n

        Returns:\n
        final_list (list - str) : the fixed J->E text.\n

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

        Outputs results to a string.

        """

        Kijiku.translation_print_result += "Time Elapsed : " + Toolkit.get_elapsed_time(time_start, time_end)

        Kijiku.translation_print_result += "\n\nDebug text have been written to : " + os.path.join(FileEnsurer.output_dir, "debug log.txt")
        Kijiku.translation_print_result += "\nJ->E text have been written to : " + os.path.join(FileEnsurer.output_dir, "jeCheck.txt")
        Kijiku.translation_print_result += "\nTranslated text has been written to : " + os.path.join(FileEnsurer.output_dir, "translatedText.txt")
        Kijiku.translation_print_result += "\nErrors have been written to : " + os.path.join(FileEnsurer.output_dir, "error log.txt") + "\n"
