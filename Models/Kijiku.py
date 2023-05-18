## built in modules
import base64
import json
import shutil
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
from Util import associated_functions


##-------------------start-of-Kijiku--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Kijiku:

    """
    
    Kijiku is a secondary class that is used to interact with the OpenAI API.
    
    """

##-------------------start-of-__init__()--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, config_dir:str, script_dir:str, from_gui:bool) -> None:
        
        ## where the config files are stored
        self.config_dir = config_dir

        ## where the main script is located
        self.script_dir = script_dir

        ## if the program is being run from the gui
        self.from_gui = from_gui

        ## the rules Kijiku will follow when interacting with the OpenAI API
        self.kijiku_rules = dict()

        ## the japanese text that will be translated
        self.japanese_text = []

        ## the debugging text for developers
        self.debug_text = []

        ## the translated text
        self.translated_text = []

        ## the text for j-e checking
        self.je_check_text = []

        ## the text for errors that occur during translation
        self.error_text = []

#-------------------start-of-reset_kijiku_rules()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def reset_kijiku_rules(self) -> None:

        """

        resets the self.kijiku_rules json to default\n

        Parameters:\n
        self.config_dir (string) the path to the config directory\n

        Returns:\n
        None\n

        """
        
        default = {
        "open ai settings": 
        {
            "model":"gpt-3.5-turbo",
            "temp":1,
            "top_p":1,
            "n":1,
            "stream":False,
            "stop":None,
            "max_tokens":9223372036854775807,
            "presence_penalty":0,
            "frequency_penalty":0,
            "logit_bias":None,
            "system_message":"You are a Japanese To English translator. Please remember that you need to translate the narration into English simple past. Try to keep the original formatting and punctuation as well. ",
            "message_mode":1,
            "num_lines":13,
            "sentence_fragmenter_mode":1
        }
        }

        with open(os.path.join(self.config_dir,'Kijiku Rules.json'), 'w+', encoding='utf-8') as file:
            json.dump(default,file)

        associated_functions.clear_console()

#-------------------start-of-change_settings()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def change_settings(self) -> None:

        """

        Allows the user to change the settings of the Kijiku Rules.json file\n

        Parameters:\n
        self (object - Kijiku) : the Kijiku object.\n

        Returns:\n
        None\n

        """
        
        while(True):

            associated_functions.clear_console()

            print("See https://platform.openai.com/docs/api-reference/chat/create for further details\n")

            print("\nmodel : ID of the model to use. As of right now, Kijiku only works with 'chat' models.")
            print("\ntemperature : What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. Lower Values are typically better for translation")
            print("\ntop_p : An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. I generally recommend altering this or temperature but not both.")
            print("\nn : How many chat completion choices to generate for each input message. Do not change this.")
            print("\nstream : If set, partial message deltas will be sent, like in ChatGPT. Tokens will be sent as data-only server-sent events as they become available, with the stream terminated by a data: [DONE] message. See the OpenAI Cookbook for example code. Do not change this.")
            print("\nstop : Up to 4 sequences where the API will stop generating further tokens. Do not change this.")
            print("\nmax_tokens :  The maximum number of tokens to generate in the chat completion. The total length of input tokens and generated tokens is limited by the model's context length. I wouldn't recommend changing this")
            print("\npresence_penalty : Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.")
            print("\nfrequency_penalty : Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.")
            print("\nlogit_bias : Modify the likelihood of specified tokens appearing in the completion. Do not change this.")
            print("\nsystem_message : Instructions to the model. Do not change this unless you know what you're doing.")
            print("\nmessage_mode : 1 or 2. 1 means the system message will actually be treated as a system message. 2 means it'll be treating as a user message. 1 is recommend for gpt-4 otherwise either works.")
            print("\nnum_lines : the number of lines to be built into a prompt at once. Theoretically, more lines would be more cost effective, but other complications may occur with higher lines.")
            print("\nsentence_fragmenter_mode : 1 or 2 or 3 (1 - via regex and other nonsense, 2 - NLP via spacy, 3 - None (Takes formatting and text directly from ai return)) the api can sometimes return a result on a single line, so this determines the way Kijiku fragments the sentences if at all.")
            
            print("\n\nPlease note that while logit_bias and max_tokens can be changed, Kijiku does not currently do anything with them.")

            print("\n\nCurrent settings:\n\n")

            for key,value in self.kijiku_rules["open ai settings"].items(): ## print out the current settings
                print(key + " : " + str(value))

            action = input("\nEnter the name of the setting you want to change, type d to reset to default, or type 'q' to continue: ").lower()

            if(action == "q"): ## if the user wants to continue, do so
                break

            elif(action == "d"): ## if the user wants to reset to default, do so
                self.reset_kijiku_rules()

                with open(os.path.join(self.config_dir,'Kijiku Rules.json'), 'r', encoding='utf-8') as file:
                    self.kijiku_rules = json.load(file) 


            elif(action not in self.kijiku_rules["open ai settings"]):
                print("Invalid setting name. Please try again.")
                time.sleep(1)
                continue

            else:

                new_value = input("\nEnter a new value for " + action + " : ")

                self.kijiku_rules["open ai settings"][action] = new_value

        with open(os.path.join(self.config_dir,'Kijiku Rules.json'), 'w+', encoding='utf-8') as file:
            json.dump(self.kijiku_rules, file)

##-------------------start-of-translate()--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def translate(self,text_to_translate:str) -> None:
        
        self.initialize(text_to_translate)

        self.commence_translation()

#-------------------start-of-initialize_text()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def initialize(self,text_to_translate:str) -> None:

        """

        Set the open api key and create a list full of the sentences we need to translate.\n
        
        Parameters:\n
        text_to_translate (string) a path to the text kijiku will translate\n
        
        Returns:\n
        None\n

        """

        try:
            with open(os.path.join(self.config_dir,'GPTApiKey.txt'), 'r', encoding='utf-8') as file:  ## get saved api key if exists
                api_key = base64.b64decode((file.read()).encode('utf-8')).decode('utf-8')

            openai.api_key = api_key

            print("Used saved api key in " + os.path.join(self.config_dir,'GPTApiKey.txt')) ## if valid save the api key

        except (FileNotFoundError,AuthenticationError): ## else try to get api key manually
                
            if(os.path.isfile("C:\\ProgramData\\Kudasai\\GPTApiKey.txt") == True): ## if the api key is in the old location, delete it
                os.remove("C:\\ProgramData\\Kudasai\\GPTApiKey.txt")
                print("r'C:\\ProgramData\\Kudasai\\GPTApiKey.txt' was deleted due to Kudasai switching to user storage\n")
                
            api_key = input("DO NOT DELETE YOUR COPY OF THE API KEY\n\nPlease enter the openapi key you have : ")

            try: ## if valid save the api key

                openai.api_key = api_key

                if(os.path.isdir(self.config_dir) == False):
                    os.mkdir(self.config_dir, 0o666)
                    print(self.config_dir + " created due to lack of the folder")

                    time.sleep(.1)
                            
                if(os.path.isfile(os.path.join(self.config_dir,'GPTApiKey.txt')) == False):
                    print(os.path.join(self.config_dir,'GPTApiKey.txt') + " was created due to lack of the file")

                    with open(os.path.join(self.config_dir,'GPTApiKey.txt'), 'w+', encoding='utf-8') as key: 
                        key.write(base64.b64encode(api_key.encode('utf-8')).decode('utf-8'))

                    time.sleep(.1)
                
            except AuthenticationError: ## if invalid key exit
                    
                associated_functions.clear_console()
                        
                print("Authorization error with creating translator object, please double check your api key as it appears to be incorrect.\n")
                associated_functions.pause_console()
                        
                exit()

            except Exception as e: ## other error, alert user and raise it

                associated_functions.clear_console()
                        
                print("Unknown error with creating translator object, The error is as follows " + str(e)  + "\nThe exception will now be raised.\n")
                associated_functions.pause_console()

                raise e
                    
        with open(text_to_translate, 'r', encoding='utf-8') as file:  ## strips each line of the text to translate
            self.japanese_text = [line.strip() for line in file.readlines()]

        associated_functions.clear_console()

        try: ## try to load the kijiku rules

            if(os.path.isfile(r'C:\\ProgramData\\Kudasai\\Kijiku Rules.json') == True): ## if the kijiku rules are in the old location, copy them to the new one and delete the old one
                shutil.copyfile(r'C:\\ProgramData\\Kudasai\\Kijiku Rules.json', os.path.join(self.config_dir,'Kijiku Rules.json'))

                os.remove(r'C:\\ProgramData\\Kudasai\\Kijiku Rules.json')
                print("r'C:\\ProgramData\\Kudasai\\Kijiku Rules.json' was deleted due to Kudasai switching to user storage\n\nYour settings have been copied to " + self.config_dir + "\n\n")
                time.sleep(1)
                associated_functions.clear_console()

            with open(os.path.join(self.config_dir,'Kijiku Rules.json'), 'r', encoding='utf-8') as file:
                self.kijiku_rules = json.load(file) 


        except: ## if the kijiku rules don't exist, create them
            
            self.reset_kijiku_rules()

            with open(os.path.join(self.config_dir,'Kijiku Rules.json'), 'r', encoding='utf-8') as file:
                self.kijiku_rules = json.load(file) 

#-------------------start-of-main()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def commence_translation(self) -> None:

        """
            
        Uses all the other functions to translate the text provided by Kudasai\n

        Parameters:\n
        japaneseText (list - string) a list of japanese lines that we need to translate\n
        scriptDir (string) the path of the directory that holds Kudasai.py\n
        self.config_dir (string) the path of the directory that holds Kijiku Rules.json\n
        
        Returns:\n
        None\n

        """
        
        try:
        
            i = 0

            self.debug_text.append("Kijiku Activated\n\nSettings are as follows : \n\n")

            with open(os.path.join(self.config_dir,'Kijiku Rules.json'), 'r', encoding='utf-8') as file:
                self.kijiku_rules = json.load(file) 

            for key,value in self.kijiku_rules["open ai settings"].items():
                self.debug_text.append(key + " : " + str(value) +'\n')
                
            self.MODEL = self.kijiku_rules["open ai settings"]["model"]
            self.system_message = self.kijiku_rules["open ai settings"]["system_message"]
            self.message_mode = int(self.kijiku_rules["open ai settings"]["message_mode"])
            self.prompt_size = int(self.kijiku_rules["open ai settings"]["num_lines"])
            self.sentence_fragmenter_mode = int(self.kijiku_rules["open ai settings"]["sentence_fragmenter_mode"])

            time_start = time.time()

            associated_functions.clear_console()

            self.debug_text.append("\nStarting Prompt Building\n-------------------------\n")

            messages = self.build_messages()

            self.estimate_cost(messages)

            if(self.from_gui == False):
                associated_functions.pause_console("Press any key to continue with translation...")

            self.debug_text.append("\nStarting Translation\n-------------------------")

            while(i+2 <= len(messages)):

                associated_functions.clear_console()

                print("Trying " + str(i+2) + " of " + str(len(messages)))
                self.debug_text.append("\n\n-------------------------\nTrying " + str(i+2) + " of " + str(len(messages)) + "\n-------------------------\n")

                self.translate_message(messages[i],messages[i+1],self.MODEL,self.kijiku_rules)

                self.redistribute()

                i+=2

            associated_functions.output_results(self.script_dir,self.config_dir,self.debug_text,self.je_check_text,self.translated_text,self.error_text,self.from_gui)

            time_end = time.time()

            if(self.from_gui):
                with open(os.path.join(self.config_dir,"guiTempTranslationLog.txt"), "a+", encoding="utf-8") as file: # Write the text to a temporary file
                    file.write("\nTime Elapsed : " + associated_functions.get_elapsed_time(time_start, time_end) + "\n\n")
            
            else:
                print("\nTime Elapsed : " + associated_functions.get_elapsed_time(time_start, time_end))
    
        except Exception as e: 

            print("\nUncaught error has been raised in Kijiku, error is as follows : " + str(e) + "\nOutputting incomplete results\n")

            self.error_text.append("\nUncaught error has been raised in Kijiku, error is as follows : " + str(e) + "\nOutputting incomplete results\n")

            if(self.from_gui):
                with open(os.path.join(self.config_dir,"guiTempTranslationLog.txt"), "a+", encoding="utf-8") as file: # Write the text to a temporary file
                    file.write("\nUncaught error has been raised in Kijiku, error is as follows : " + str(e) + "\nOutputting incomplete results\n")

            associated_functions.output_results(self.script_dir,self.config_dir,self.debug_text,self.je_check_text,self.translated_text,self.error_text,self.from_gui)
