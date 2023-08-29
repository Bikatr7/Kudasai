## built in modules
import os
import sys
import asyncio

## third party modules

import json

## custom modules
from models.Kaiseki import Kaiseki 
from models.Kijiku import Kijiku
from models.Kairyou import Kairyou

from modules.preloader import preloader


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
        None.\n

        """

        os.system("title " + "Kudasai CLI")

        self.preloader = preloader()

        self.preloader.toolkit.clear_console()

        self.preloader.file_handler.logger.log_action("--------------------")
        self.preloader.file_handler.logger.log_action("Initialized Kudasai")
        self.preloader.file_handler.logger.log_action("--------------------\n")

        self.preloader.file_handler.logger.log_action("--------------------")
        self.preloader.file_handler.logger.log_action("Kudasai started")
        self.preloader.file_handler.logger.log_action("--------------------\n")
    
        self.preloader.file_handler.logger.log_action("--------------------")
        self.preloader.file_handler.logger.log_action("Current version: " + self.preloader.toolkit.CURRENT_VERSION)
        self.preloader.file_handler.logger.log_action("-------------------\n")

        self.kairyou_client = None

        self.kaiseki_client = None

        self.kijiku_client = None

        self.connection = None

##-------------------start-of-setup_kairyou_for_cli()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    def setup_kairyou_for_cli(self, input_file, replacement_json) -> None:

        """
        
        If the user is running the CLI version of Kudasai, this function is called to setup the text to be processed and the replacement json file.\n
        
        Parameters:\n
        self (object - Kudasai) : the Kudasai object.\n
        input_file (str) : The path to the input file to be processed.\n
        replacement_json (str) : The path to the replacement json file.\n

        Returns:\n
        None.\n

        """

        try:

            with open(replacement_json, 'r', encoding='utf-8') as file: 
                replacement_json = json.load(file) 
    
        except:

            print("The second path you provided is either invalid, not a JSON file, or the JSON file has an error.\n")
            self.preloader.file_handler.logger.log_action("The second path you provided is either invalid, not a JSON file, or the JSON file has an error.\n")

            self.preloader.toolkit.pause_console()

            exit()


        with open(input_file, 'r', encoding='utf-8') as file: 
            japanese_text = file.read()
        
        self.kairyou_client = Kairyou(replacement_json, japanese_text, self.preloader)

##-------------------start-of-setup_kairyou_for_console()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def setup_kairyou_for_console(self) -> None:

        """
        
        If the user is running the Console version of Kudasai, this function is called to setup the text to be processed and the replacement json file.\n

        Parameters:\n
        self (object - Kudasai) : the Kudasai object.\n

        Returns:\n
        None.\n

        """

        os.system("title " + "Kudasai Console")

        replacement_json = input("Please enter the path to the replacement json file:\n").strip('"')

        self.preloader.toolkit.clear_console()

        input_file = input("Please enter the path to the input file to be processed:\n").strip('"')

        self.preloader.toolkit.clear_console()

        try:

            with open(replacement_json, 'r', encoding='utf-8') as file: 
                replacement_json = json.load(file) 
    
        except:

            print("The second path you provided is either invalid, not a JSON file, or the JSON file has an error.\n")
            self.preloader.file_handler.logger.log_action("The second path you provided is either invalid, not a JSON file, or the JSON file has an error.\n")

            self.preloader.toolkit.pause_console()

            exit()


        with open(input_file, 'r', encoding='utf-8') as file: 
            japanese_text = file.read()
        
        self.kairyou_client = Kairyou(replacement_json, japanese_text, self.preloader)

##-------------------start-of-run_kudasai_console()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    async def run_kudasai_console(self) -> None:

        """
        
        If the user is running the Console version of Kudasai, this function is called to run the program.\n
        
        Parameters:\n
        self (object - Kudasai) : the Kudasai object.\n

        Returns:\n
        None.\n

        """

        self.handle_update_check_from_cli_or_console()

        self.kairyou_client.preprocess() ## type: ignore (we know it's not None)

        print(self.kairyou_client.preprocessing_log) ## type: ignore (we know it's not None)

        self.preloader.write_kairyou_results(self.kairyou_client) ## type: ignore (we know it's not None)

        self.preloader.toolkit.pause_console("\nPress any key to continue to Auto-Translation...")

        await self.determine_autotranslation_module()

        self.preloader.toolkit.pause_console("\nPress any key to exit...")

##-------------------start-of-run_kudasai_cli()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    async def run_kudasai_cli(self) -> None:

        """
        
        If the user is running the CLI version of Kudasai, this function is called to run the program.\n
        
        Parameters:\n
        self (object - Kudasai) : the Kudasai object.\n

        Returns:\n
        None.\n

        """

        self.handle_update_check_from_cli_or_console()

        self.kairyou_client.preprocess() ## type: ignore (we know it's not None)

        print(self.kairyou_client.preprocessing_log) ## type: ignore (we know it's not None)

        self.preloader.write_kairyou_results(self.kairyou_client) ## type: ignore (we know it's not None)

        self.preloader.toolkit.pause_console("\nPress any key to continue to Auto-Translation...")

        await self.determine_autotranslation_module()

##-------------------start-of-handle_update_check_from_cli_or_console()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def handle_update_check_from_cli_or_console(self) -> None:

        """

        If the user is running the CLI or Console version of Kudasai, this function is called to check for updates.\n

        Parameters:\n
        self (object - Kudasai) : the Kudasai object.\n

        Returns:\n
        None.\n

        """

        self.connection, update_prompt = self.preloader.toolkit.check_update() # type: ignore

        if(update_prompt):
            
            print(update_prompt)

            self.preloader.toolkit.pause_console()
            self.preloader.toolkit.clear_console()
        

##-------------------start-of-determine_autotranslation_module()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    async def determine_autotranslation_module(self) -> None:

        """
        
        If the user is running the CLI or Console version of Kudasai, this function is called to determine which autotranslation module to use.\n

        Parameters:\n
        self (object - Kudasai) : the Kudasai object.\n

        Returns:\n
        None.\n

        """

        if(not self.connection):
            self.preloader.toolkit.clear_console()

            print("You are not connected to the internet. Please connect to the internet to use the autotranslation feature.\n")
            self.preloader.toolkit.pause_console()

            exit()

        self.preloader.toolkit.clear_console()

        pathing = ""

        pathing_msg = "Please select an auto-translation module:\n\n1.Kaiseki\n2.Kijiku\n3.Exit\n\n"

        pathing = input(pathing_msg)

        self.preloader.toolkit.clear_console()

        if(pathing == "1"):
            self.run_kaiseki()
        elif(pathing == "2"):
            await self.run_kijiku()
        else:
            self.preloader.toolkit.clear_console()

##-------------------start-of-run_kaiseki()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def run_kaiseki(self) -> None:

        """
        
        If the user is running the CLI or Console version of Kudasai, this function is called to run the Kaiseki module.\n

        Parameters:\n
        self (object - Kudasai) : the Kudasai object.\n

        Returns:\n
        None.\n

        """

        self.preloader.file_handler.logger.log_action("--------------------")
        self.preloader.file_handler.logger.log_action("Kaiseki started")
        self.preloader.file_handler.logger.log_action("--------------------\n")

        self.kaiseki_client = Kaiseki(self.kairyou_client.text_to_preprocess,self.preloader) ## type: ignore (we know it's not None)

        self.kaiseki_client.translate()

        self.preloader.toolkit.clear_console()

        print(self.kaiseki_client.translation_print_result)

        self.preloader.write_kaiseki_results(self.kaiseki_client) ## type: ignore (we know it's not None)

##-------------------start-of-run_kijiku()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    async def run_kijiku(self) -> None:

        """
        
        If the user is running the CLI or Console version of Kudasai, this function is called to run the Kijiku module.\n

        Parameters:\n
        self (object - Kudasai) : the Kudasai object.\n

        Returns:\n
        None.\n

        """

        self.preloader.file_handler.logger.log_action("--------------------")
        self.preloader.file_handler.logger.log_action("Kijiku started")
        self.preloader.file_handler.logger.log_action("--------------------\n")

        self.preloader.toolkit.clear_console()

        self.kijiku_client = Kijiku(self.kairyou_client.text_to_preprocess,self.preloader) ## type: ignore (we know it's not None)

        await self.kijiku_client.translate()

        self.preloader.toolkit.clear_console()

        print(self.kijiku_client.translation_print_result)

        self.preloader.write_kijiku_results(self.kijiku_client) ## type: ignore (we know it's not None)

##-------------------start-of-main()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

async def main():

    client = Kudasai()

    try:

        ## determines if we will run the Kudasai CLI or the Kudasai Console
        if(__name__ == '__main__'):

            ## to be implemented later, for now we will just run the CLI version
            if(len(sys.argv) < 3):
                
                client.setup_kairyou_for_console()

                await client.run_kudasai_console()

                client.preloader.file_handler.logger.push_batch()

            else:

                client.setup_kairyou_for_cli(sys.argv[1], sys.argv[2])

                await client.run_kudasai_cli()

                client.preloader.file_handler.logger.push_batch()

    except Exception as e:

        client.preloader.file_handler.handle_critical_exception(e)

asyncio.run(main())