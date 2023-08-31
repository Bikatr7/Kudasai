## built-in libraries
from __future__ import annotations ## used for cheating the circular import issue that occurs when i need to type check some things

import os
import ctypes
import json
import typing
import time

## custom modules
if(typing.TYPE_CHECKING): ## used for cheating the circular import issue that occurs when i need to type check some things
    from modules.preloader import preloader

class jsonHandler:

    '''
    
    This class is used to handle the Kijiku Rules json file.\n

    '''

##--------------------start-of-__init__()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, inc_preloader:preloader):

        """
        
        Constructor for the jsonHandler class.\n

        Parameters:\n
        inc_preloader (preloader): The preloader object.\n

        Returns:\n
        None.\n

        """

        ## the preloader object
        self.preloader = inc_preloader

        ## path to the external kijiku rules json file
        self.external_kijiku_rules_path = os.path.join(self.preloader.file_handler.script_dir,'Kijiku Rules.json')

        ## the path to the kijiku rules json file
        self.kijiku_rules_path = os.path.join(self.preloader.file_handler.config_dir,'Kijiku Rules.json')

        ## the rules Kijiku will follow when interacting with the OpenAI API
        self.kijiku_rules = dict()

        ## the default settings for the Kijiku Rules.json file
        self.default = {
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
            "sentence_fragmenter_mode":1,
            "je_check_mode":1
        }
        }

##-------------------start-of-validate_json()--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def validate_json(self):

        """

        Validates the Kijiku Rules.json file.\n

        Parameters:\n
        self (object - jsonHandler) : the jsonHandler object.\n

        Returns:\n
        None.\n

        """

        keys_list = [
        "model",
        "temp",
        "top_p",
        "n",
        "stream",
        "stop",
        "max_tokens",
        "presence_penalty",
        "frequency_penalty",
        "logit_bias",
        "system_message",
        "message_mode",
        "num_lines",
        "sentence_fragmenter_mode",
        "je_check_mode"
         ]
        

        if("open ai settings" not in self.kijiku_rules):
            self.reset_kijiku_rules_to_default()

        if(all(key in self.kijiku_rules["open ai settings"] for key in keys_list)):
            self.preloader.file_handler.logger.log_action("Kijiku Rules.json is valid")
        
        else:
            self.reset_kijiku_rules_to_default()

##-------------------start-of-reset_kijiku_rules_to_default()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def reset_kijiku_rules_to_default(self) -> None:

        """

        Resets the kijiku_rules json to default.\n

        Parameters:\n
        self (object - jsonHandler) : the jsonHandler object.\n
        
        Returns:\n
        None.\n

        """

        self.kijiku_rules = self.default
        
        ## updates json file
        self.dump_kijiku_rules()

        ## loads json file
        self.load_kijiku_rules()

##-------------------start-of-dump_kijiku_rules()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def dump_kijiku_rules(self) -> None:

        """

        Dumps the Kijiku Rules.json file.\n

        Parameters:\n
        self (object - jsonHandler) : the jsonHandler object.\n

        Returns:\n
        None.\n

        """

        ## updates json file
        with open(self.kijiku_rules_path, 'w+', encoding='utf-8') as file:
            json.dump(self.kijiku_rules, file)

##-------------------start-of-load_kijiku_rules()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def load_kijiku_rules(self) -> None:

        """

        Loads the Kijiku Rules.json file.\n

        Parameters:\n
        self (object - jsonHandler) : the jsonHandler object.\n

        Returns:\n
        None.\n

        """

        ## loads the json file
        with open(self.kijiku_rules_path, 'r', encoding='utf-8') as file:
            self.kijiku_rules = json.load(file)


#-------------------start-of-change_kijiku_settings()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def change_kijiku_settings(self) -> None:

        """

        Allows the user to change the settings of the Kijiku Rules.json file\n

        Parameters:\n
        self (object - jsonHandler) : the json object.\n

        Returns:\n
        None.\n

        """
        
        ## maximize console window
        hwnd = ctypes.windll.kernel32.GetConsoleWindow() 
        ctypes.windll.user32.ShowWindow(hwnd, 3)
        
        while(True):

            self.preloader.toolkit.clear_console()

            settings_print_message = "See https://platform.openai.com/docs/api-reference/chat/create for further details\n"

            settings_print_message += "\n\nmodel : ID of the model to use. As of right now, Kijiku only works with 'chat' models."
            settings_print_message += "\n\ntemperature : What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. Lower Values are typically better for translation"
            settings_print_message += "\n\ntop_p : An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. I generally recommend altering this or temperature but not both."
            settings_print_message += "\n\nn : How many chat completion choices to generate for each input message. Do not change this."
            settings_print_message += "\n\nstream : If set, partial message deltas will be sent, like in ChatGPT. Tokens will be sent as data-only server-sent events as they become available, with the stream terminated by a data: [DONE] message. See the OpenAI Cookbook for example code. Do not change this."
            settings_print_message += "\n\nstop : Up to 4 sequences where the API will stop generating further tokens. Do not change this."
            settings_print_message += "\n\nmax_tokens :  The maximum number of tokens to generate in the chat completion. The total length of input tokens and generated tokens is limited by the model's context length. I wouldn't recommend changing this"
            settings_print_message += "\n\npresence_penalty : Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics."
            settings_print_message += "\n\nfrequency_penalty : Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim."
            settings_print_message += "\n\nlogit_bias : Modify the likelihood of specified tokens appearing in the completion. Do not change this."
            settings_print_message += "\n\nsystem_message : Instructions to the model. Do not change this unless you know what you're doing."
            settings_print_message += "\n\nmessage_mode : 1 or 2. 1 means the system message will actually be treated as a system message. 2 means it'll be treating as a user message. 1 is recommend for gpt-4 otherwise either works."
            settings_print_message += "\n\nnum_lines : the number of lines to be built into a prompt at once. Theoretically, more lines would be more cost effective, but other complications may occur with higher lines."
            settings_print_message += "\n\nsentence_fragmenter_mode : 1 or 2 or 3 (1 - via regex and other nonsense, 2 - NLP via spacy, 3 - None (Takes formatting and text directly from ai return)) the api can sometimes return a result on a single line, so this determines the way Kijiku fragments the sentences if at all."
            settings_print_message += "\n\nje_check_mode : 1 or 2, 1 will print out the 'num_lines' amount of jap then the english below separated by ---, 2 will attempt to pair the english and jap sentences, placing the jap above the eng. If it cannot, it will do 1."

            settings_print_message += "\n\nPlease note that while logit_bias and max_tokens can be changed, Kijiku does not currently do anything with them."

            settings_print_message += "\n\nCurrent settings:\n\n----------------------------------------------------------------\n\n"

            ## print out the current settings
            for key,value in self.kijiku_rules["open ai settings"].items(): 
                settings_print_message += key + " : " + str(value) + '\n'

            settings_print_message += "\n\nEnter the name of the setting you want to change, type d to reset to default, type c to load an external/custom json directly, or type 'q' to quit settings change : "

            action = input(settings_print_message).lower()

            ## if the user wants to continue, do so
            if(action == "q"): 
                break

            ## loads a custom json directly
            if(action == "c"):
                self.preloader.toolkit.clear_console()

                ## saves old rules in case on invalid json
                old_kijiku_rules = self.kijiku_rules

                try:

                    ## loads the custom json file
                    with open(self.external_kijiku_rules_path, 'r', encoding='utf-8') as file:
                        self.kijiku_rules = json.load(file) 

                    self.validate_json()

                    assert self.kijiku_rules != self.default ## validate_json() sets a dict to default if it's invalid, so if it's still default, it's invalid
                    
                    self.dump_kijiku_rules()
                
                except AssertionError:
                    print("Invalid JSON file. Please try again. ")

                except FileNotFoundError:
                    print("Missing JSON file. Please try again.")

                finally:
                    ## resets the kijiku rules to the old rules
                    self.kijiku_rules = old_kijiku_rules

                    continue
            
            ## if the user wants to reset to default, do so
            elif(action == "d"): 
                self.reset_kijiku_rules_to_default()

            elif(action not in self.kijiku_rules["open ai settings"]):
                print("Invalid setting name. Please try again.")
                time.sleep(1)
                continue

            else:

                new_value = input("\nEnter a new value for " + action + " : ")

                self.kijiku_rules["open ai settings"][action] = new_value


        self.dump_kijiku_rules()

        ## minimize console window
        hwnd = ctypes.windll.kernel32.GetConsoleWindow() 
        ctypes.windll.user32.ShowWindow(hwnd, 9)
