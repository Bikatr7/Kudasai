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
from modules.jsonHandler import jsonHandler

if(typing.TYPE_CHECKING): ## used for cheating the circular import issue that occurs when i need to type check some things
    from modules.preloader import preloader


##-------------------start-of-Kijiku--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Kijiku:

    """
    
    Kijiku is a secondary class that is used to interact with the OpenAI API and translates the text by batch.\n
    
    """

##-------------------start-of-__init__()--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, inc_text_to_translate:str, inc_preloader:preloader) -> None:

        """

        Constructor for the Kijiku class.\n

        Parameters:\n
        text_to_translate (string) : the text to translate.\n
        inc_preloader (preloader) : the preloader object.\n

        Returns:\n
        None.\n

        """

        ## the preloader object
        self.preloader = inc_preloader

        ## the json handler object
        self.json_handler = jsonHandler(inc_preloader)

        ##--------------------------------------------------------------------------------------------------------------------------
        
        ## the text to translate
        self.text_to_translate =  [line for line in inc_text_to_translate.split('\n')]

        ## the translated text
        self.translated_text = []

        ## the text for j-e checking
        self.je_check_text = []

        ## the text for errors that occur during translation
        self.error_text = []

        ## the messages that will be sent to the api, contains a system message and a model message, system message is the instructions,
        ## model message is the text that will be translated  
        self.translation_batches = []

        ##--------------------------------------------------------------------------------------------------------------------------

        ## path to the openai api key
        self.api_key_path = os.path.join(self.preloader.file_handler.config_dir,'GPTApiKey.txt')

        ## the translation print result
        self.translation_print_result = ""

##-------------------start-of-translate()--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    async def translate(self) -> None:

        """

        Translate the text in the file at the path given.\n

        Parameters:\n
        self (object - Kijiku) : the Kijiku object.\n

        Returns:\n
        None.\n

        """

        ## ngl i have basically no idea what this does, but it's needed for openai async to work
        openai.aiosession.set(ClientSession())

        ## set this here cause the try-except could throw before we get past the settings configuration
        self.time_start = time.time()

        try:
        
            self.initialize()

            self.json_handler.validate_json()

            self.check_settings()

            ## set actual start time to the end of the settings configuration
            self.time_start = time.time()

            await self.commence_translation()

        except Exception as e:
            
            self.translation_print_result += "An error has occurred, outputting results so far..."

            self.preloader.file_handler.handle_critical_exception(e)

        finally:

            self.time_end = time.time() 

            self.assemble_results()

            ## more session stuff that i don't understand
            session = openai.aiosession.get()

            if(session):
                await session.close()

##-------------------start-of-initialize()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def initialize(self) -> None:

        """

        Sets the open api key.\n
        
        Parameters:\n
        self (object - Kijiku) : the Kijiku object.\n
        
        Returns:\n
        None\n

        """

        ## get saved api key if exists
        try:
            with open(self.api_key_path, 'r', encoding='utf-8') as file: 
                api_key = base64.b64decode((file.read()).encode('utf-8')).decode('utf-8')

            openai.api_key = api_key
        
            print("Used saved api key in " + self.api_key_path)
            self.preloader.file_handler.logger.log_action("Used saved api key in " + self.api_key_path)

        ## else try to get api key manually
        except (FileNotFoundError, AuthenticationError): 

            self.preloader.toolkit.clear_console()
                
            api_key = input("DO NOT DELETE YOUR COPY OF THE API KEY\n\nPlease enter the openapi key you have : ")

            ## if valid save the api key
            try: 

                openai.api_key = api_key

                self.preloader.file_handler.standard_overwrite_file(self.api_key_path, base64.b64encode(api_key.encode('utf-8')).decode('utf-8'))
                
            ## if invalid key exit
            except AuthenticationError: 
                    
                self.preloader.toolkit.clear_console()
                        
                print("Authorization error with setting up openai, please double check your api key as it appears to be incorrect.\n")
                self.preloader.file_handler.logger.log_action("Authorization error with setting up openai, please double check your api key as it appears to be incorrect.\n")

                self.preloader.toolkit.pause_console()
                        
                exit()

            ## other error, alert user and raise it
            except Exception as e: 

                self.preloader.toolkit.clear_console()
                        
                print("Unknown error with setting up openai, The error is as follows " + str(e)  + "\nThe exception will now be raised.\n")
                self.preloader.file_handler.logger.log_action("Unknown error with setting up openai, The error is as follows " + str(e)  + "\nThe exception will now be raised.\n")

                self.preloader.toolkit.pause_console()

                raise e
            
        ## try to load the kijiku rules
        try: 

            self.json_handler.load_kijiku_rules()

        ## if the kijiku rules don't exist, create them
        except: 
            
            self.json_handler.reset_kijiku_rules_to_default()

            self.json_handler.load_kijiku_rules()
            
        self.preloader.toolkit.clear_console()

##-------------------start-of-check-settings()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def check_settings(self) -> None:

        """

        Prompts the user to confirm the settings in the kijiku rules file.\n

        Parameters:\n
        self (object - Kijiku) : the Kijiku object.\n

        Returns:\n
        None.\n

        """

        print("Are these settings okay? (1 for yes or 2 for no) : \n\n")

        for key, value in self.json_handler.kijiku_rules["open ai settings"].items():
            print(key + " : " + str(value))

        if(input("\n") == "1"):
            pass
        else:
            self.json_handler.change_kijiku_settings()

        self.preloader.toolkit.clear_console()

##-------------------start-of-commence_translation()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    async def commence_translation(self) -> None:

        """

        Uses all the other functions to translate the text provided by Kudasai.\n

        Parameters:\n
        self (object - Kijiku) : the Kijiku object.\n
        
        Returns:\n
        None.\n

        """
        
        self.preloader.file_handler.logger.log_action("-------------------------")
        self.preloader.file_handler.logger.log_action("Kijiku Activated, Settings are as follows : ")
        self.preloader.file_handler.logger.log_action("-------------------------")

        for key,value in self.json_handler.kijiku_rules["open ai settings"].items():
            self.preloader.file_handler.logger.log_action(key + " : " + str(value))

        self.MODEL = self.json_handler.kijiku_rules["open ai settings"]["model"]
        self.translation_instructions = self.json_handler.kijiku_rules["open ai settings"]["system_message"]
        self.message_mode = int(self.json_handler.kijiku_rules["open ai settings"]["message_mode"])
        self.prompt_size = int(self.json_handler.kijiku_rules["open ai settings"]["num_lines"])
        self.sentence_fragmenter_mode = int(self.json_handler.kijiku_rules["open ai settings"]["sentence_fragmenter_mode"])
        self.je_check_mode = int(self.json_handler.kijiku_rules["open ai settings"]["je_check_mode"])

        self.preloader.toolkit.clear_console()

        self.preloader.file_handler.logger.log_action("-------------------------")
        self.preloader.file_handler.logger.log_action("Starting Prompt Building")
        self.preloader.file_handler.logger.log_action("-------------------------")

        self.build_translation_batches()

        cost = self.estimate_cost()
        print(cost)

        await asyncio.sleep(7)

        self.preloader.file_handler.logger.log_action("Starting Translation")
        print("Starting Translation...\n\n")

        ## requests to run asynchronously
        async_requests = []
        length = len(self.translation_batches)

        for i in range(0, length, 2):
            async_requests.append(self.handle_translation(i, length, self.translation_batches[i], self.translation_batches[i+1]))

        ## Use asyncio.gather to run tasks concurrently/asynchronously and wait for all of them to complete
        results = await asyncio.gather(*async_requests)

        print("\n\nTranslation Complete!\n\n")
        self.preloader.file_handler.logger.log_action("Translation Complete!")

        print("Starting Redistribution...\n\n")
        self.preloader.file_handler.logger.log_action("Starting Redistribution...")

        ## Sort results based on the index to maintain order
        sorted_results = sorted(results, key=lambda x: x[0])

        ## Redistribute the sorted results
        for index, translated_prompt, translated_message in sorted_results:
            self.redistribute(translated_prompt, translated_message)

        ## try to pair the text for j-e checking if the mode is 2
        if(self.je_check_mode == 2):
            self.je_check_text = self.fix_je()

        self.preloader.toolkit.clear_console()

        print("Done!\n\n")
        self.preloader.file_handler.logger.log_action("Done!")

##-------------------start-of-generate_prompt()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def generate_prompt(self, index:int) -> tuple[typing.List[str],int]:

        '''

        Generates prompts for the messages meant for the ai.\n

        Parameters:\n
        self (object - Kijiku) : the Kijiku object.\n
        index (int) an int representing where we currently are in the text file.\n

        Returns:\n
        prompt (list - string) a list of japanese lines that will be assembled into messages.\n
        index (int) an updated int representing where we currently are in the text file.\n

        '''

        prompt = []

        while(index < len(self.text_to_translate)):
            sentence = self.text_to_translate[index]

            if(len(prompt) < self.prompt_size):

                if(any(char in sentence for char in ["▼", "△", "◇"])):
                    prompt.append(sentence + '\n')
                    self.preloader.file_handler.logger.log_action("Sentence : " + sentence + ", Sentence is a pov change... leaving intact.\n")

                elif("part" in sentence.lower() or all(char in ["１","２","３","４","５","６","７","８","９", " "] for char in sentence) and not all(char in [" "] for char in sentence)):
                    prompt.append(sentence + '\n') 
                    self.preloader.file_handler.logger.log_action("Sentence : " + sentence + ", Sentence is part marker... leaving intact.\n")

                elif(bool(re.match(r'^[\W_\s\n-]+$', sentence)) and not any(char in sentence for char in ["」", "「", "«", "»"]) and sentence != '"..."' and sentence != "..."):
                    self.preloader.file_handler.logger.log_action("Sentence : " + sentence + ", Sentence is punctuation... skipping.\n")
            
                elif(bool(re.match(r'^[A-Za-z0-9\s\.,\'\?!]+\n*$', sentence) and "part" not in sentence.lower())):
                    self.preloader.file_handler.logger.log_action("Sentence is empty... skipping translation.\n")

                else:
                    prompt.append(sentence + "\n")
    
            else:
                return prompt, index
            
            index += 1

        return prompt, index
    
##-------------------start-of-build_translation_batches()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def build_translation_batches(self) -> None:

        '''

        Builds translations batches dict for ai prompt.\n
        
        Parameters:\n
        self (object - Kijiku) : the Kijiku object.\n

        Returns:\n
        None.\n

        '''

        i = 0

        while i < len(self.text_to_translate):
            prompt, i = self.generate_prompt(i)

            prompt = ''.join(prompt)

            if(self.message_mode == 1):
                system_msg = {}
                system_msg["role"] = "system"
                system_msg["content"] = self.translation_instructions

            else:
                system_msg = {}
                system_msg["role"] = "user"
                system_msg["content"] = self.translation_instructions

            self.translation_batches.append(system_msg)

            model_msg = {}
            model_msg["role"] = "user"
            model_msg["content"] = prompt

            self.translation_batches.append(model_msg)

        self.preloader.file_handler.logger.log_action("Built Messages : ")
        self.preloader.file_handler.logger.log_action("-------------------------")

        i = 0

        for message in self.translation_batches:

            i+=1

            if(i % 2 == 0):

                self.preloader.file_handler.logger.log_action(str(message))
        
            else:

                self.preloader.file_handler.logger.log_action(str(message))
                self.preloader.file_handler.logger.log_action("-------------------------")

##-------------------start-of-estimate_cost()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def estimate_cost(self) -> str:

        '''

        Attempts to estimate cost.\n
    
        Parameters:\n
        self (object - Kijiku) : the Kijiku object.\n

        Returns:\n
        None.\n

        '''
        
        try:
            encoding = tiktoken.encoding_for_model(self.MODEL)
            
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")

        if(self.MODEL == "gpt-3.5-turbo"):
            print("Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
            time.sleep(1)
            self.MODEL="gpt-3.5-turbo-0613"
            return self.estimate_cost()
        
        elif(self.MODEL == "gpt-3.5-turbo-0301"):
            print("Warning: gpt-3.5-turbo-0301 is outdated. gpt-3.5-turbo-0301's support ended September 13, Returning num tokens assuming gpt-3.5-turbo-0613.")
            time.sleep(1)
            self.MODEL="gpt-3.5-turbo-0613"
            return self.estimate_cost()

        elif(self.MODEL == "gpt-4"):
            print("Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-0613.")
            time.sleep(1)
            self.MODEL="gpt-4-0613"
            return self.estimate_cost()
        
        elif(self.MODEL == "gpt-4-0314"):
            print("Warning: gpt-4-0314 is outdated. gpt-4-0314's support ended September 13, Returning num tokens assuming gpt-4-0613.")
            time.sleep(1)
            self.MODEL="gpt-4-0613"
            return self.estimate_cost()
        
        elif(self.MODEL == "gpt-3.5-turbo-0613"):
            cost_per_thousand_tokens = 0.0015
            tokens_per_message = 4  ## every message follows <|start|>{role/name}\n{content}<|end|>\n
            tokens_per_name = -1  ## if there's a name, the role is omitted

        elif(self.MODEL == "gpt-4-0613"):
            cost_per_thousand_tokens = 0.06
            tokens_per_message = 3
            tokens_per_name = 1

        else:
            raise NotImplementedError(f"""Kudasai does not support : {self.MODEL}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
        
        num_tokens = 0

        for message in self.translation_batches:

            num_tokens += tokens_per_message

            for key, value in message.items():

                num_tokens += len(encoding.encode(value))

                if(key == "name"):
                    num_tokens += tokens_per_name

        num_tokens += 3  ## every reply is primed with <|start|>assistant<|message|>
        min_cost = round((float(num_tokens) / 1000.00) * cost_per_thousand_tokens, 5)

        estimate_cost_result = "Estimated Tokens in Messages : " + str(num_tokens) + ", Estimated Minimum Cost : $" + str(min_cost) + "\n"

        self.preloader.file_handler.logger.log_action(estimate_cost_result)
        self.preloader.file_handler.logger.log_action("-------------------------")

        return estimate_cost_result
    
##-------------------start-of-translate_message()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    ## backoff wrapper for retrying on errors
    @backoff.on_exception(backoff.expo, (ServiceUnavailableError, RateLimitError, Timeout, APIError, APIConnectionError))
    async def translate_message(self, translation_instructions:dict, translation_prompt:dict) -> str:

        '''

        Translates system and user message.\n

        Parameters:\n
        self (object - Kijiku) : the Kijiku object.\n
        translation_instructions (dict) : the system message also known as the instructions.\n
        translation_prompt (dict) : the user message also known as the prompt.\n

        Returns:\n
        output (string) a string that gpt gives to us also known as the translation.\n

        '''

        ## max_tokens and logit bias are currently excluded due to a lack of need, and the fact that i am lazy

        response = await openai.ChatCompletion.acreate(
            model=self.MODEL,
            messages=[
                translation_instructions,
                translation_prompt,
            ],

            temperature = float(self.json_handler.kijiku_rules["open ai settings"]["temp"]),
            top_p = float(self.json_handler.kijiku_rules["open ai settings"]["top_p"]),
            n = int(self.json_handler.kijiku_rules["open ai settings"]["top_p"]),
            stream = self.json_handler.kijiku_rules["open ai settings"]["stream"],
            stop = self.json_handler.kijiku_rules["open ai settings"]["stop"],
            presence_penalty = float(self.json_handler.kijiku_rules["open ai settings"]["presence_penalty"]),
            frequency_penalty = float(self.json_handler.kijiku_rules["open ai settings"]["frequency_penalty"]),

        )

        ## note, pylance flags this as a 'GeneralTypeIssue', however i see nothing wrong with it, and it works fine
        output = response['choices'][0]['message']['content'] ## type: ignore
        
        return output
    
##-------------------start-of-handle_translation()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    async def handle_translation(self, index:int, length:int, translation_instructions:dict, translation_prompt:dict) -> tuple[int, dict, str]:

        """

        Handles the translation for a given system and user message.\n

        Parameters:\n
        self (object - Kijiku) : the Kijiku object.\n
        index (int) : the index of the message in the original list.\n
        translation_instructions (dict) : the system message also known as the instructions.\n
        translation_prompt (dict) : the user message also known as the prompt.\n

        Returns:\n
        index (int) : the index of the message in the original list.\n
        translation_prompt (dict) : the user message also known as the prompt.\n
        translated_message (str) : the translated message.\n

        """

        translated_message = ""
        NUM_TRIES_ALLOWED = 1
        num_tries = 0

        while True:
        
            message_number = (index // 2) + 1
            print(f"Trying translation for batch {message_number} of {length//2}...")
            self.preloader.file_handler.logger.log_action(f"Trying translation for batch {message_number} of {length//2}...")

            translated_message = await self.translate_message(translation_instructions, translation_prompt)

            if(self.MODEL != "gpt-4-0613"):
                break

            if(await self.check_if_translation_is_good(translated_message, translation_prompt) or num_tries >= NUM_TRIES_ALLOWED):
                break

            else:
                num_tries += 1
                print(f"Batch {message_number} of {length//2} was malformed, retrying...")
                self.preloader.file_handler.logger.log_action(f"Batch {message_number} of {length//2} was malformed, retrying...")

        print(f"Translation for batch {message_number} of {length//2} successful!")
        self.preloader.file_handler.logger.log_action(f"Translation for batch {message_number} of {length//2} successful!")

        return index, translation_prompt, translated_message
    
##-------------------start-of-check_if_translation_is_good()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    async def check_if_translation_is_good(self, translated_message:str, translation_prompt:dict):

        """
        
        Checks if the translation is good, i.e. the number of lines in the prompt and the number of lines in the translated message are the same.\n

        Parameters:\n
        self (object - Kijiku) : the Kijiku object.\n
        translated_message (string) : the translated message\n
        translation_prompt (dict) : the user message also known as the prompt.\n

        Returns:\n
        is_valid (bool) : whether or not the translation is valid.\n

        """

        prompt = translation_prompt["content"]
        is_valid = False

        jap = [line for line in prompt.split('\n') if line.strip()]  ## Remove blank lines
        eng = [line for line in translated_message.split('\n') if line.strip()]  ## Remove blank lines

        if(len(jap) == len(eng)):
            is_valid = True
    
        return is_valid
    
##-------------------start-of-log_retry()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def log_retry(self, details):

        '''

        Logs the retry message.\n

        Parameters:\n
        details (dict) : the details of the retry.\n

        Returns:\n
        None.\n

        '''

        retry_msg = f"Backing off {details['wait']} seconds after {details['tries']} tries calling function {details['target']} due to {details['value']}."
        self.preloader.file_handler.logger.log_action(retry_msg)


##-------------------start-of-redistribute()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def redistribute(self, translation_prompt:dict, translated_message:str) -> None:

        '''

        Puts translated text back into the text file.\n

        Parameters:\n
        self (object - Kijiku) : the Kijiku object.\n
        translated_message (string) : the translated message\n

        Returns:\n
        None.\n

        '''

        if(self.je_check_mode == 1):
            self.je_check_text.append("\n-------------------------\n"+ str(translation_prompt["content"]) + "\n\n")
            self.je_check_text.append(translated_message + '\n')
        elif(self.je_check_mode == 2):
            self.je_check_text.append(str(translation_prompt["content"]))
            self.je_check_text.append(translated_message)

        ## mode 1 is the default mode, uses regex and other nonsense to split sentences
        if(self.sentence_fragmenter_mode == 1): 

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

                self.translated_text.append(sentence + '\n')

            for i in range(len(self.translated_text)):
                if self.translated_text[i] in patched_sentences:
                    index = patched_sentences.index(self.translated_text[i])
                    self.translated_text[i] = patched_sentences[index]

        ## mode 2 uses spacy to split sentences
        elif(self.sentence_fragmenter_mode == 2): 

            nlp = spacy.load("en_core_web_lg")

            doc = nlp(translated_message)
            sentences = [sent.text for sent in doc.sents]

            for sentence in sentences:
                self.translated_text.append(sentence + '\n')

        ## mode 3 just assumes gpt formatted it properly
        elif(self.sentence_fragmenter_mode == 3): 
            
            self.translated_text.append(translated_message + '\n\n')
        
##-------------------start-of-fix_je()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def fix_je(self) -> typing.List[str]:

        '''

        Fixes the J->E text to be more j-e check friendly.\n

        Note that fix_je() is not always accurate, and may use standard j-e formatting instead of the corrected formatting.\n

        Parameters:\n
        self (object - Kijiku) : the Kijiku object.\n

        Returns:\n
        final_list (list - str) : the fixed J->E text.\n

        '''
        
        i = 1
        final_list = []

        while i < len(self.je_check_text):
            jap = self.je_check_text[i-1].split('\n')
            eng = self.je_check_text[i].split('\n')

            jap = [line for line in jap if line.strip()]  ## Remove blank lines
            eng = [line for line in eng if line.strip()]  ## Remove blank lines    

            final_list.append("\n-------------------------\n")

            if(len(jap) == len(eng)):

                for jap_line,eng_line in zip(jap,eng):
                    if(jap_line and eng_line): ## check if jap_line and eng_line aren't blank
                        final_list.append(jap_line + '\n\n')
                        final_list.append(eng_line + '\n\n')
     

            else:

                final_list.append(self.je_check_text[i-1] + '\n\n')
                final_list.append(self.je_check_text[i] + '\n\n')

            i+=2

        return final_list

##-------------------start-of-assemble_results()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    def assemble_results(self) -> None:

        '''

        Outputs results to a string.\n

        Parameters:\n
        self (object - Kijiku) : the Kijiku object.\n

        Returns:\n
        None.\n

        '''

        self.translation_print_result += "Time Elapsed : " + self.preloader.toolkit.get_elapsed_time(self.time_start, self.time_end)

        self.translation_print_result += "\n\nDebug text have been written to : " + os.path.join(self.preloader.file_handler.output_dir, "debug log.txt")
        self.translation_print_result += "\nJ->E text have been written to : " + os.path.join(self.preloader.file_handler.output_dir, "jeCheck.txt")
        self.translation_print_result += "\nTranslated text has been written to : " + os.path.join(self.preloader.file_handler.output_dir, "translatedText.txt")
        self.translation_print_result += "\nErrors have been written to : " + os.path.join(self.preloader.file_handler.output_dir, "error log.txt") + "\n"
