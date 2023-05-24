## built in modules
import string
import os
import time
import re
import base64
import time
import typing

## third party modules
import deepl

## custom modules
from Util import associated_functions

##-------------------start-of-Kansei--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Kansei:

    """
    
    Kansei is a secondary class that is used to interact with the deepL API, it translates sentences in batches.

    """

##-------------------start-of-__init__()--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, config_dir:str, script_dir:str, from_gui:bool) -> None:

        """

        The constructor for the Kansei class. Takes in the path to the config directory and the path to the main script directory as well as a boolean indicating if the translation request is from the gui or not.\n

        Parameters:\n
        self (object - Kansei) : The Kansei object.\n
        config_dir (str) : The path to the config directory.\n
        script_dir (str) : The path to the main script directory.\n
        from_gui (bool) : A boolean indicating if the translation request is from the gui or not.\n

        Returns:\n
        None\n

        """

        ## the path to the config directory
        self.config_dir = config_dir

        ## the path to the main script directory
        self.script_dir = script_dir

        ## if the translation request is from the gui or not
        self.from_gui = from_gui

        ## the text to translate
        self.japanese_text = []

        ## the text for logging errors
        self.error_text = []

        ## the text for the j-e checkers
        self.je_check_text = []

        ## the translated text
        self.translated_text = []

        ## the debug text
        self.debug_text = []

        ## the text to given to the deepL api to translate
        self.messages = []

        ## number of lines to translate at once
        self.prompt_size = 32
        
##-------------------start-of-reset()--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    def reset(self) -> None:

        """

        Resets the Kansei object.\n

        Parameters:\n
        self (object - Kansei) : The Kansei object.\n

        Returns:\n
        None\n

        """

        self.error_text = []
        self.je_check_text = []
        self.translated_text = []
        self.debug_text = []
        self.messages = []
        
##-------------------start-of-translate()--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def translate(self, text_to_translate:str):

        """

        Translates the text file

        Parameters:\n
        self (object - Kansei) : The Kansei object.\n
        text_to_translate (str) : the path to the text file to translate.\n

        Returns:\n
        None\n

        """

        self.reset()

        self.initialize(text_to_translate) ## initialize the Kaiseki object

        self.commence_translation() ## commence the translation

##-------------------start-of-initialize()--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def initialize(self, text_to_translate:str) -> None:
        
        """

        Initializes the Kansei class by getting the api key and creating the translator object.\n

        Parameters:\n
        self (object - Kansei) : The Kansei object.\n
        text_to_translate (str) : the path to the text file to translate.\n

        
        """
        
        try:
            with open(os.path.join(self.config_dir,'DeeplApiKey.txt'), 'r', encoding='utf-8') as file:  ## get saved api key if exists
                api_key = base64.b64decode((file.read()).encode('utf-8')).decode('utf-8')

            self.translator = deepl.Translator(api_key)

            print("Used saved api key in " + os.path.join(self.config_dir,'DeeplApiKey.txt'))

        except Exception as e: ## else try to get api key manually

            if(os.path.isfile("C:\\ProgramData\\Kudasai\\DeeplApiKey.txt") == True):
                os.remove("C:\\ProgramData\\Kudasai\\DeeplApiKey.txt")
                print("r'C:\\ProgramData\\Kudasai\\DeeplApiKey.txt' was deleted due to Kudasai switching to user storage\n")

            api_key = input("DO NOT DELETE YOUR COPY OF THE API KEY\n\nPlease enter the deepL api key you have : ")

            try: ## if valid save the api key

                self.translator = deepl.Translator(api_key)

                if(os.path.isdir(self.config_dir) == False):
                    os.mkdir(self.config_dir, 0o666)
                    print(self.config_dir + " was created due to lack of the folder")

                time.sleep(.1)
                    
                if(os.path.exists(os.path.join(self.config_dir,'DeeplApiKey.txt')) == False):
                    print(os.path.join(self.config_dir,'DeeplApiKey.txt') + " was created due to lack of the file")

                    with open(os.path.join(self.config_dir,'DeeplApiKey.txt'), 'w+', encoding='utf-8') as key: 
                        key.write(base64.b64encode(api_key.encode('utf-8')).decode('utf-8'))

                time.sleep(.1)
                
            except deepl.exceptions.AuthorizationException: ## if invalid key exit
                    
                associated_functions.clear_console()
                    
                print("Authorization error with creating translator object, please double check your api key as it appears to be incorrect.\nKudasai will now exit.\n")
                associated_functions.pause_console()
                    
                exit()

            except Exception as e: ## other error, alert user and raise it
                
                associated_functions.clear_console()
                    
                print("Unknown error with creating translator object, The error is as follows " + str(e)  + "\nKudasai will now exit.\n")
                associated_functions.pause_console()

                exit()

        with open(text_to_translate, 'r', encoding='utf-8') as file:  ## strips each line of the text to translate_sentence
            self.japanese_text = [line.strip() for line in file.readlines()]

##-------------------start-of-commence_translation()--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def commence_translation(self):
        
        """
        
        Commences the translation of the text file.\n
        
        Parameters:\n
        self (object - Kansei) : The Kansei object.\n

        Returns:\n
        None\n

        """

##-------------------start-of-generate_prompt()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def generate_prompt(self, index:int) -> tuple[typing.List[str],int]:

        '''

        generates prompts for the messages meant for the ai\n

        Parameters:\n
        self (object - Kansei) : the Kansei object.\n
        index (int) an int representing where we currently are in the text file\n

        Returns:\n
        prompt (list - string) a list of japanese lines that will be assembled into messages\n
        index (int) an updated int representing where we currently are in the text file\n

        '''

        prompt = []

        while(index < len(self.japanese_text)):
            sentence = self.japanese_text[index]

            if(len(prompt) < self.prompt_size):

                if(any(char in sentence for char in ["▼", "△", "◇"])):
                    prompt.append(sentence + '\n')
                    self.debug_text.append("\n-----------------------------------------------\nSentence : " + sentence + "\nSentence is a pov change... leaving intact\n-----------------------------------------------\n")

                elif("part" in sentence.lower() or all(char in ["１","２","３","４","５","６","７","８","９", " "] for char in sentence) and not all(char in [" "] for char in sentence)):
                    prompt.append(sentence + '\n') 
                    self.debug_text.append("\n-----------------------------------------------\nSentence : " + sentence + "\nSentence is part marker... leaving intact\n-----------------------------------------------\n")
            
                elif(bool(re.match(r'^[\W_\s\n-]+$', sentence)) and not any(char in sentence for char in ["」", "「", "«", "»"])):
                    self.debug_text.append("\n-----------------------------------------------\nSentence : " + sentence + "\nSentence is punctuation... skipping\n-----------------------------------------------\n")
            
                elif(bool(re.match(r'^[A-Za-z0-9\s\.,\'\?!]+\n*$', sentence) and "part" not in sentence.lower())):
                    self.debug_text.append("\n-----------------------------------------------\nSentence : " + sentence + "\nSentence is english... skipping\n-----------------------------------------------\n")

                else:
                    prompt.append(sentence + "\n")
    
            else:
                return prompt, index
            
            index += 1

        return prompt, index
    
##-------------------start-of-build_messages()--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def build_messages(self) -> None:

        '''

        builds messages dict for ai\n
        
        Parameters:\n
        self (object - Kansei) : the Kansei object.\n

        Returns:\n
        None\n

        '''

        i = 0

        while i < len(self.japanese_text):
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

        self.debug_text.append("\nMessages\n-------------------------\n\n")

        i = 0

        for message in self.messages:

            self.debug_text.append(str(message) + "\n\n")
        
