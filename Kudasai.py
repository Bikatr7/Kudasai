## built in modules
import os
import traceback
import sys

## third party modules

import json

## custom modules
from Models.Kaiseki import Kaiseki 
from Models.Kijiku import Kijiku
from Models.Kairyou import Kairyou

from Modules.preloader import preloader


##-------------------start-of-Kudasai---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Kudasai:

    """

    Kudasai class is the main class for the Kudasai program. It handles all the stuff except for the gui.\n
    
    """
##-------------------start-of-__init__()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self) -> None: 

        """
        
        Constructor for Kudasai class.

        Parameters:\n
        self (object - Kudasai) : the Kudasai object.\n

        Returns:\n
        None\n

        """

        os.system("title " + "Kudasai")

        self.preloader = preloader()

        self.preloader.toolkit.clear_console()

        self.kairyou_client = None

        self.kaiseki_client = None

        self.kijiku_client = None

        self.connection = None

##-------------------start-of-setup()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    def setup_kairyou(self, input_file, replacement_json) -> None:

        """
        
        If the user is running the CLI version of Kudasai, this function is called to setup the text to be processed and the replacement json file.\n
        
        Parameters:\n
        self (object - Kudasai) : the Kudasai object.\n
        input_file (str) : The path to the input file to be processed.\n
        replacement_json (str) : The path to the replacement json file.\n

        Returns:\n
        None\n

        """

        try:

            with open(replacement_json, 'r', encoding='utf-8') as file: 
                replacement_json = json.load(file) 
    
        except:

            print("The second path you provided is either invalid, not a JSON file, or the JSON file has an error.\n")
            self.preloader.toolkit.pause_console()

            exit()


        with open(input_file, 'r', encoding='utf-8') as file: 
            japanese_text = file.read()
        
        self.kairyou_client = Kairyou(replacement_json, japanese_text, self.preloader)

##-------------------start-of-run_kudasai_cli()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def run_kudasai_cli(self) -> None:

        """
        
        If the user is running the CLI version of Kudasai, this function is called to run the program.\n
        
        Parameters:\n
        self (object - Kudasai) : the Kudasai object.\n

        Returns:\n
        None\n

        """

        self.handle_update_check_from_cli_or_console()

        self.kairyou_client.preprocess() ## type: ignore (we know it's not None)

        self.write_kairyou_results()

        self.preloader.toolkit.pause_console("Press any key to continue to Auto-Translation...")

        self.determine_autotranslation_module()

##-------------------start-of-handle_update_check_from_cli_or_console()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def handle_update_check_from_cli_or_console(self) -> None:

        self.connection, update_prompt = self.preloader.toolkit.check_update()

        if(update_prompt):
            
            print(update_prompt)

            self.preloader.toolkit.pause_console()
            self.preloader.toolkit.clear_console()
        

##-------------------start-of-write_kairyou_results()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def write_kairyou_results(self) -> None:

        """
        
        If the user is running the CLI or Console version of Kudasai, this function is called to write the results of the preprocessing to a directory.\n

        Parameters:\n
        self (object - Kudasai) : the Kudasai object.\n

        Returns:\n
        None\n

        """

        with(open(self.preloader.preprocessed_text_path, 'w', encoding='utf-8')) as file:
            file.write(self.kairyou_client.text_to_preprocess) ## type: ignore (we know it's not None)

        with open(self.preloader.kairyou_log_path, 'w', encoding='utf-8') as file:
            file.write(self.kairyou_client.preprocessing_log) ## type: ignore (we know it's not None)

        with open(self.preloader.error_log_path, 'w', encoding='utf-8') as file:
            file.write(self.kairyou_client.error_log) ## type: ignore (we know it's not None)

        with open(self.preloader.je_check_path, 'w', encoding='utf-8') as file:
            file.truncate()

        with open(self.preloader.translated_text_path, 'w', encoding='utf-8') as file:
            file.truncate()

##-------------------start-of-determine_autotranslation_module()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def determine_autotranslation_module(self) -> None:

        """
        
        If the user is running the CLI or Console version of Kudasai, this function is called to determine which autotranslation module to use.\n

        Parameters:\n
        self (object - Kudasai) : the Kudasai object.\n

        Returns:\n
        None\n

        """

        self.preloader.toolkit.clear_console()

        pathing = 0

        pathing_msg = "Please select an auto-translation module:\n\n1. Kaiseki\n2. Kijiku\n3.Skip\n\n"

        pathing = input(pathing_msg)

        if(pathing == "1"):
            self.run_kaiseki()
        elif(pathing == "2"):
            pass
        else:
            pass


##-------------------start-of-run_kaiseki()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def run_kaiseki(self) -> None:

        """
        
        If the user is running the CLI or Console version of Kudasai, this function is called to run the Kaiseki module.\n

        Parameters:\n
        self (object - Kudasai) : the Kudasai object.\n

        Returns:\n
        None\n

        """

        self.kaiseki_client = Kaiseki(self.kairyou_client.text_to_preprocess,self.preloader) ## type: ignore (we know it's not None)

        self.kaiseki_client.translate()
            
##-------------------start-of-main()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

client = Kudasai()

try:

    ## determines if we will run the Kudasai CLI or the Kudasai Console
    if(__name__ == '__main__'):

        ## to be implemented later, for now we will just run the CLI version
        if(len(sys.argv) < 3):
            pass

        else:

            client.setup_kairyou(sys.argv[1], sys.argv[2])

            client.run_kudasai_cli()

except Exception as e:

    ## if crash, catch and log, then throw
    client.preloader.file_handler.logger.log_action("--------------------------------------------------------------")
    client.preloader.file_handler.logger.log_action("Kudasai has crashed")

    traceback_str = traceback.format_exc()
    
    client.preloader.file_handler.logger.log_action(traceback_str)

    client.preloader.file_handler.logger.push_batch()

    raise e