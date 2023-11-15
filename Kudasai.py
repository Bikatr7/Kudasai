## built-in libraries
import os
import sys
import asyncio
import json

## custom modules
from models.kaiseki import Kaiseki 
from models.kijiku import Kijiku
from models.kairyou import Kairyou

from modules.toolkit import Toolkit
from modules.file_ensurer import FileEnsurer
from modules.logger import Logger
from modules.results_assembler import ResultsAssembler

##-------------------start-of-Kudasai---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Kudasai:

    """

    Kudasai class is the main class for the Kudasai program. It handles all the logic for the CLI and Console versions of Kudasai.
    
    """

    connection:bool
    
##-------------------start-of-boot()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def boot(self) -> None:

        """
        
        If the user is running the CLI or Console version of Kudasai, this function is called to boot the program.\n


        """

        os.system("title " + "Kudasai CLI")

        Toolkit.clear_console()

        Logger.log_action("--------------------")
        Logger.log_action("Initialized Kudasai")
        Logger.log_action("--------------------\n")

        Logger.log_action("--------------------")
        Logger.log_action("Kudasai started")
        Logger.log_action("--------------------\n")
    
        Logger.log_action("--------------------")
        Logger.log_action("Current version: " + Toolkit.CURRENT_VERSION)
        Logger.log_action("-------------------\n")

##-------------------start-of-setup_kairyou_for_cli()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def setup_kairyou_for_cli(input_file, replacement_json_path) -> None:

        """
        
        If the user is running the CLI version of Kudasai, this function is called to setup the text to be processed and the replacement json file.
        
        Parameters:
        input_file (str) : The path to the input file to be processed.
        replacement_json (str) : The path to the replacement json file.

        """

        try:

            with open(replacement_json_path, 'r', encoding='utf-8') as file: 
                replacement_json = json.load(file) 
    
        except:

            print("The second path you provided is either invalid, not a JSON file, or the JSON file has an error.\n")
            Logger.log_action("The second path you provided is either invalid, not a JSON file, or the JSON file has an error.\n")

            Toolkit.pause_console()

            exit()

        ## get name of json file
        ## Example "86 Replacements.json" would return 86
        ## I remember needing this for something but I don't remember what
        name_of_replacement_json = os.path.basename(replacement_json_path)        

        with open(input_file, 'r', encoding='utf-8') as file: 
            japanese_text = file.read()
        
        Kairyou.replacement_json = replacement_json 
        Kairyou.text_to_preprocess = japanese_text

##-------------------start-of-setup_kairyou_for_console()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def setup_kairyou_for_console() -> None:

        """
        
        If the user is running the Console version of Kudasai, this function is called to setup the text to be processed and the replacement json file.

        """

        input_file = input("Please enter the path to the input file to be processed:\n").strip('"')

        Toolkit.clear_console()

        replacement_json_path = input("Please enter the path to the replacement json file:\n").strip('"')

        Toolkit.clear_console()

        try:

            with open(replacement_json_path, 'r', encoding='utf-8') as file: 
                replacement_json = json.load(file) 
    
        except:

            print("The second path you provided is either invalid, not a JSON file, or the JSON file has an error.\n")
            Logger.log_action("The second path you provided is either invalid, not a JSON file, or the JSON file has an error.\n")

            Toolkit.pause_console()

            exit()


        ## get name of json file
        ## Example "86 Replacements.json" would return 86
        ## I remember needing this for something but I don't remember what
        name_of_replacement_json = os.path.basename(replacement_json_path)        

        with open(input_file, 'r', encoding='utf-8') as file: 
            japanese_text = file.read()
        
        Kairyou.replacement_json = replacement_json 
        Kairyou.text_to_preprocess = japanese_text

##-------------------start-of-run_kudasai_console()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    async def run_kudasai_console() -> None:

        """
        
        If the user is running the Console version of Kudasai, this function is called to run the program.
        
        """

        Kudasai.handle_update_check_from_cli_or_console()

        Kairyou.preprocess()

        print(Kairyou.preprocessing_log) 

        ResultsAssembler.write_kairyou_results() ## type: ignore (we know it's not None)

        Toolkit.pause_console("\nPress any key to continue to Auto-Translation...")

        await Kudasai.determine_autotranslation_module()

        Toolkit.pause_console("\nPress any key to exit...")

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

        Toolkit.pause_console("\nPress any key to continue to Auto-Translation...")

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

        self.connection, update_prompt = Toolkit.check_update() # type: ignore

        if(update_prompt):
            
            print(update_prompt)

            Toolkit.pause_console()
            Toolkit.clear_console()
        

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
            Toolkit.clear_console()

            print("You are not connected to the internet. Please connect to the internet to use the autotranslation feature.\n")
            Toolkit.pause_console()

            exit()

        Toolkit.clear_console()

        pathing = ""

        pathing_msg = "Please select an auto-translation module:\n\n1.Kaiseki (deepL)\n2.Kijiku (GPT)\n3.Exit\n\n"

        pathing = input(pathing_msg)

        Toolkit.clear_console()

        if(pathing == "1"):
            self.run_kaiseki()
        elif(pathing == "2"):
            await self.run_kijiku()
        else:
            Toolkit.clear_console()
            exit()

##-------------------start-of-run_kaiseki()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def run_kaiseki(self) -> None:

        """
        
        If the user is running the CLI or Console version of Kudasai, this function is called to run the Kaiseki module.\n

        Parameters:\n
        self (object - Kudasai) : the Kudasai object.\n

        Returns:\n
        None.\n

        """

        Logger.log_action("--------------------")
        Logger.log_action("Kaiseki started")
        Logger.log_action("--------------------\n")

        self.kaiseki_client = Kaiseki(self.kairyou_client.text_to_preprocess,self.preloader) ## type: ignore (we know it's not None)

        self.kaiseki_client.translate()

        Toolkit.clear_console()

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

        Logger.log_action("--------------------")
        Logger.log_action("Kijiku started")
        Logger.log_action("--------------------\n")

        Toolkit.clear_console()

        self.kijiku_client = Kijiku(self.kairyou_client.text_to_preprocess,self.preloader) ## type: ignore (we know it's not None)

        await self.kijiku_client.translate()

        Toolkit.clear_console()

        print(self.kijiku_client.translation_print_result)

        self.preloader.write_kijiku_results(self.kijiku_client) ## type: ignore (we know it's not None)

##-------------------start-of-main()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

async def main() -> None:

    client = Kudasai()

    try:

        ## determines if we will run the Kudasai CLI or the Kudasai Console
        if(__name__ == '__main__'):

            ## if running console version
            if(len(sys.argv) <= 1):
                
                client.setup_kairyou_for_console()

                await client.run_kudasai_console()

                client.preloader.file_handler.logger.push_batch()

            ## if running cli version
            elif(len(sys.argv) == 3):

                client.setup_kairyou_for_cli(sys.argv[1], sys.argv[2])

                await client.run_kudasai_cli()

                client.preloader.file_handler.logger.push_batch()

            ## print usage statement
            else:
                    
                    print("Usage: python Kudasai.py <input_file> <replacement_json>\n\n")
                    print("or run Kudasai.py without any arguments to run the console version.\n\n")
    
                    client.preloader.file_handler.logger.log_action("Usage: python Kudasai.py <input_file> <replacement_json>")
    
                    client.preloader.toolkit.pause_console()
    
                    exit()

    except Exception as e:

        client.preloader.file_handler.handle_critical_exception(e)

##---------------------------------/

asyncio.run(main())