## built in modules
import base64
import re
import os
import time
import typing


## third party modules
import openai
import backoff
import tiktoken
import spacy

from openai.error import APIConnectionError, APIError, AuthenticationError, ServiceUnavailableError, RateLimitError, Timeout

## custom modules
from modules.preloader import preloader
from modules.jsonHandler import jsonHandler

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
        inc_text_to_translate (string) : the path to the text file to translate.\n
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
        self.messages = []

        ##--------------------------------------------------------------------------------------------------------------------------

        ## path to the openai api key
        self.api_key_path = os.path.join(self.preloader.file_handler.config_dir,'GPTApiKey.txt')

        self.translation_print_result = ""

##-------------------start-of-translate()--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def translate(self) -> None:

        """

        Translate the text in the file at the path given.\n

        Parameters:\n
        self (object - Kijiku) : the Kijiku object.\n

        Returns:\n
        None.\n

        """

        self.time_start = time.time()

        try:
        
            self.initialize()

            self.json_handler.validate_json()

            self.check_settings()

            self.commence_translation()

        except Exception as e:
            
            self.translation_print_result += "An error has occurred, outputting results so far..."

            self.preloader.file_handler.handle_critical_exception(e)

        finally:

            self.time_end = time.time() ## end time

            self.assemble_results() ## assemble the results

##-------------------start-of-initialize()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def initialize(self) -> None:

        """

        Sets the open api key.\n
        
        Parameters:\n
        self (object - Kijiku) : the Kijiku object.\n
        
        Returns:\n
        None\n

        """

        try:
            with open(self.api_key_path, 'r', encoding='utf-8') as file:  ## get saved api key if exists
                api_key = base64.b64decode((file.read()).encode('utf-8')).decode('utf-8')

            openai.api_key = api_key
        
            self.preloader.file_handler.logger.log_action("Used saved api key in " + self.api_key_path)

        except (FileNotFoundError, AuthenticationError): ## else try to get api key manually
                
            api_key = input("DO NOT DELETE YOUR COPY OF THE API KEY\n\nPlease enter the openapi key you have : ")

            try: ## if valid save the api key

                openai.api_key = api_key

                self.preloader.file_handler.standard_overwrite_file(self.api_key_path, base64.b64encode(api_key.encode('utf-8')).decode('utf-8'))
                
            except AuthenticationError: ## if invalid key exit
                    
                self.preloader.toolkit.clear_console()
                        
                print("Authorization error with setting up openai, please double check your api key as it appears to be incorrect.\n")
                self.preloader.toolkit.pause_console()
                        
                exit()

            except Exception as e: ## other error, alert user and raise it

                self.preloader.toolkit.clear_console()
                        
                print("Unknown error with setting up openai, The error is as follows " + str(e)  + "\nThe exception will now be raised.\n")
                self.preloader.toolkit.pause_console()

                raise e
            
        try: ## try to load the kijiku rules

            self.json_handler.load_kijiku_rules()

        except: ## if the kijiku rules don't exist, create them
            
            self.json_handler.reset_kijiku_rules_to_default()

            self.json_handler.load_kijiku_rules()

##-------------------start-of-check-settings()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def check_settings(self):

        """

        Prompts the user to confirm the settings in the kijiku rules file.\n

        Parameters:\n
        self (object - Kijiku) : the Kijiku object.\n

        Returns:\n
        None\n

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

    def commence_translation(self) -> None:

        """
            
        Uses all the other functions to translate the text provided by Kudasai\n

        Parameters:\n
        self (object - Kijiku) : the Kijiku object.\n
        
        Returns:\n
        None\n

        """
        
        i = 0

        self.preloader.file_handler.logger.log_action("-------------------------")
        self.preloader.file_handler.logger.log_action("Kijiku Activated, Settings are as follows : ")
        self.preloader.file_handler.logger.log_action("-------------------------")

        for key,value in self.json_handler.kijiku_rules["open ai settings"].items():
            self.preloader.file_handler.logger.log_action(key + " : " + str(value))

        self.MODEL = self.json_handler.kijiku_rules["open ai settings"]["model"]
        self.system_message = self.json_handler.kijiku_rules["open ai settings"]["system_message"]
        self.message_mode = int(self.json_handler.kijiku_rules["open ai settings"]["message_mode"])
        self.prompt_size = int(self.json_handler.kijiku_rules["open ai settings"]["num_lines"])
        self.sentence_fragmenter_mode = int(self.json_handler.kijiku_rules["open ai settings"]["sentence_fragmenter_mode"])
        self.je_check_mode = int(self.json_handler.kijiku_rules["open ai settings"]["je_check_mode"])

        self.preloader.toolkit.clear_console()

        self.preloader.file_handler.logger.log_action("-------------------------")
        self.preloader.file_handler.logger.log_action("Starting Prompt Building")
        self.preloader.file_handler.logger.log_action("-------------------------")

        self.build_messages()

        print(self.estimate_cost())

        time.sleep(7)

        self.preloader.file_handler.logger.log_action("Starting Translation")

        while(i+2 <= len(self.messages)):

            self.preloader.toolkit.clear_console()

            print("Trying " + str(i+2) + " of " + str(len(self.messages)))
            self.preloader.file_handler.logger.log_action("Trying " + str(i+2) + " of " + str(len(self.messages)))

            translated_message = self.translate_message(self.messages[i], self.messages[i+1])

            self.redistribute(translated_message)

            i+=2

        self.preloader.toolkit.clear_console()

##-------------------start-of-generate_prompt()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def generate_prompt(self, index:int) -> tuple[typing.List[str],int]:

        '''

        generates prompts for the messages meant for the ai\n

        Parameters:\n
        self (object - Kijiku) : the Kijiku object.\n
        index (int) an int representing where we currently are in the text file\n

        Returns:\n
        prompt (list - string) a list of japanese lines that will be assembled into messages\n
        index (int) an updated int representing where we currently are in the text file\n

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
    
##-------------------start-of-build_messages()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def build_messages(self) -> None:

        '''

        builds messages dict for ai\n
        
        Parameters:\n
        self (object - Kijiku) : the Kijiku object.\n

        Returns:\n
        None\n

        '''

        i = 0

        while i < len(self.text_to_translate):
            prompt, i = self.generate_prompt(i)

            prompt = ''.join(prompt)

            if(self.message_mode == 1):
                system_msg = {}
                system_msg["role"] = "system"
                system_msg["content"] = self.system_message

            else:
                system_msg = {}
                system_msg["role"] = "user"
                system_msg["content"] = self.system_message

            self.messages.append(system_msg)

            model_msg = {}
            model_msg["role"] = "user"
            model_msg["content"] = prompt

            self.messages.append(model_msg)

        self.preloader.file_handler.logger.log_action("Built Messages : ")
        self.preloader.file_handler.logger.log_action("-------------------------")

        i = 0

        for message in self.messages:

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
        None\n

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

        for message in self.messages:

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
    def translate_message(self, system_message:dict, user_message:dict) -> str:

        '''

        translates system and user message\n

        Parameters:\n
        self (object - Kijiku) : the Kijiku object.\n
        system_message (dict) : the system message also known as the instructions\n
        user_message (dict) : the user message also known as the prompt\n

        Returns:\n
        output (string) a string that gpt gives to us also known as the translation\n

        '''

        ## max_tokens and logit bias are currently excluded due to a lack of need, and the fact that i am lazy

        response = openai.ChatCompletion.create(
            model=self.MODEL,
            messages=[
                system_message,
                user_message,
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

        self.preloader.file_handler.logger.log_action("Prompt was : \n" + user_message["content"])

        self.preloader.file_handler.logger.log_action("Response from openai was : \n\n" + output)

        if(self.je_check_mode == 1):
            self.je_check_text.append("\n-------------------------\n"+ str(user_message["content"]) + "\n\n")
        elif(self.je_check_mode == 2):
            self.je_check_text.append(str(user_message["content"]))
        
        return output

##-------------------start-of-redistribute()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def redistribute(self, translated_message:str) -> None:

        '''

        Puts translated text back into the text file.\n

        Parameters:\n
        self (object - Kijiku) : the Kijiku object.\n
        translated_message (string) : the translated message\n

        Returns:\n
        None.\n

        '''

        ## mode 1 is the default mode, uses regex and other nonsense to split sentences
        if(self.sentence_fragmenter_mode == 1): 

            sentences = re.findall(r"(.*?(?:(?:\"|\'|-|~|!|\?|%|\(|\)|\.\.\.|\.|---|\[|\])))(?:\s|$)", translated_message)

            patched_sentences = []
            build_string = None

            self.preloader.file_handler.logger.log_action("Distributed result was : \n")

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

                self.preloader.file_handler.logger.log_action(sentence + '\n')

            for i in range(len(self.translated_text)):
                if self.translated_text[i] in patched_sentences:
                    index = patched_sentences.index(self.translated_text[i])
                    self.translated_text[i] = patched_sentences[index]

        ## mode 2 uses spacy to split sentences
        elif(self.sentence_fragmenter_mode == 2): 

            nlp = spacy.load("en_core_web_lg")

            doc = nlp(translated_message)
            sentences = [sent.text for sent in doc.sents]
            
            self.preloader.file_handler.logger.log_action("\n-------------------------\nDistributed result was : \n\n")

            for sentence in sentences:
                self.translated_text.append(sentence + '\n')
                self.preloader.file_handler.logger.log_action(sentence + '\n')

        ## mode 3 just assumes gpt formatted it properly
        elif(self.sentence_fragmenter_mode == 3): 
            
            self.translated_text.append(translated_message + '\n\n')
            

        if(self.je_check_mode == 1):
            self.je_check_text.append(translated_message + '\n')
        elif(self.je_check_mode == 2):
            self.je_check_text.append(translated_message)

##-------------------start-of-fix_je()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def fix_je(self) -> typing.List[str]:

        '''

        Fixes the J->E text to be more j-e check friendly\n

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

        Outputs results to several txt files\n

        Parameters:\n
        self (object - Kijiku) : the Kijiku object.\n

        Returns:\n
        None\n

        '''

        self.translation_print_result += "Time Elapsed : " + self.preloader.toolkit.get_elapsed_time(self.time_start, self.time_end)

        self.translation_print_result += "\n\nDebug text have been written to : " + os.path.join(self.preloader.file_handler.output_dir, "debug log.txt")
        self.translation_print_result += "\nJ->E text have been written to : " + os.path.join(self.preloader.file_handler.output_dir, "jeCheck.txt")
        self.translation_print_result += "\nTranslated text has been written to : " + os.path.join(self.preloader.file_handler.output_dir, "translatedText.txt")
        self.translation_print_result += "\nErrors have been written to : " + os.path.join(self.preloader.file_handler.output_dir, "error log.txt") + "\n"

##-------------------start-of-reset()--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def reset(self):
            
        """

        resets the Kijiku object\n

        Parameters:\n
        self (object - Kijiku) : the Kijiku object.\n

        Returns:\n
        None\n

        """

        self.text_to_translate = []
        self.debug_text = []
        self.translated_text = []
        self.je_check_text = []
        self.error_text = []
        self.messages = []
