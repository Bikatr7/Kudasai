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

#-------------------start-of-Kaiseki--------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class Kaiseki:

    """

    Kaiseki is a secondary class that is used to interact with the deepl API.
    
    """


#-------------------start-of-__init__()--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, text_to_translate:str, config_dir:str) -> None:
        
        self.translator = object

        self.japanese_text = str

        self.config_dir = config_dir

        self.translate(text_to_translate)

#-------------------start-of-translate()--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def translate(self, text_to_translate:str):

        self.initialize(text_to_translate)


#-------------------start-of-initialize()--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def initialize(self, text_to_translate:str) -> None:
        
        """

        Initializes the Kaiseki class by getting the api key and creating the translator object.\n

        Parameters:\n
        self (object - Kaiseki) : the Kaiseki object.\n
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
                print("r'C:\\ProgramData\\Kudasai\\DeeplApiKey.txt' was deleted due to Kudasai switching to user storage\n\n")

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

        with open(text_to_translate, 'r', encoding='utf-8') as file:  ## strips each line of the text to translate
            self.japanese_text = [line.strip() for line in file.readlines()]
