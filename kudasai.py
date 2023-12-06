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

##-------------------start-of-Kudasai---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Kudasai:

    """

    Kudasai class is the main class for the Kudasai program. It handles all the logic for all versions of Kudasai.
    
    """

    connection:bool
    
##-------------------start-of-boot()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def boot() -> None:

        """
        
        Does some logging and sets up the console window, regardless of whether the user is running the CLI, WebGUI, or Console version of Kudasai.

        """

        os.system("title " + "Kudasai")

        Toolkit.clear_console()

        Logger.clear_log_file()

        Logger.log_barrier()
        Logger.log_action("Kudasai started")
        Logger.log_action("Current version: " + Toolkit.CURRENT_VERSION)
        Logger.log_barrier()

        Logger.push_batch()

##-------------------start-of-setup_kairyou_for_cli()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def setup_kairyou_for_cli(input_file:str, replacement_json_path:str) -> None:

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
            
            Kairyou.need_to_run = False
            replacement_json = {}

        ## get name of json file
        ## Example "86 Replacements.json" would return 86
        ## I remember needing this for something but I don't remember what
        name_of_replacement_json = os.path.basename(replacement_json_path)        

        try:

            with open(input_file, 'r', encoding='utf-8') as file: 
                japanese_text = file.read()
            
        except:
                
            Logger.log_action("The first path you provided is either invalid, not a text file, or the text file has an error.", output=True, is_error=True, omit_timestamp=True)

            Toolkit.pause_console()

            exit()
        
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

        Kairyou.write_kairyou_results() 

        Toolkit.pause_console("\nPress any key to continue to Auto-Translation...")

        await Kudasai.determine_autotranslation_module()

        Toolkit.pause_console("\nPress any key to exit...")

##-------------------start-of-run_kudasai_cli()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    async def run_kudasai_cli() -> None:

        """
        
        If the user is running the CLI version of Kudasai, this function is called to run the program.

        """

        Kudasai.handle_update_check_from_cli_or_console()

        Kairyou.preprocess()

        Kairyou.write_kairyou_results()

        Toolkit.pause_console("\nPress any key to continue to Auto-Translation...")

        await Kudasai.determine_autotranslation_module()

##-------------------start-of-handle_update_check_from_cli_or_console()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_update_check_from_cli_or_console() -> None:

        """

        If the user is running the CLI or Console version of Kudasai, this function is called to check for updates.

        """

        Kudasai.connection, update_prompt = Toolkit.check_update()

        if(update_prompt):
            
            print(update_prompt)

            Toolkit.pause_console()
            Toolkit.clear_console()
        

##-------------------start-of-determine_autotranslation_module()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    async def determine_autotranslation_module() -> None:

        """
        
        If the user is running the CLI or Console version of Kudasai, this function is called to determine which autotranslation module to use.

        """

        if(not Kudasai.connection):
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
            Kudasai.run_kaiseki()
        elif(pathing == "2"):
            await Kudasai.run_kijiku()
        else:
            Toolkit.clear_console()
            exit()

##-------------------start-of-run_kaiseki()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def run_kaiseki() -> None:

        """
        
        If the user is running the CLI or Console version of Kudasai, this function is called to run the Kaiseki module.

        """

        Logger.log_action("--------------------")
        Logger.log_action("Kaiseki started")
        Logger.log_action("--------------------")

        Kaiseki.text_to_translate = [line for line in Kairyou.text_to_preprocess.splitlines()]

        Kaiseki.translate()

        Toolkit.clear_console()

        print(Kaiseki.translation_print_result)

        Kaiseki.write_kaiseki_results() 

##-------------------start-of-run_kijiku()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    async def run_kijiku() -> None:

        """
        
        If the user is running the CLI or Console version of Kudasai, this function is called to run the Kijiku module.

        """

        Logger.log_action("--------------------")
        Logger.log_action("Kijiku started")
        Logger.log_action("--------------------")

        Toolkit.clear_console()

        Kijiku.text_to_translate = [line for line in Kairyou.text_to_preprocess.splitlines()]

        await Kijiku.translate()

        Toolkit.clear_console()

        print(Kijiku.translation_print_result)

        Kijiku.write_kijiku_results()

##-------------------start-of-main()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

async def main() -> None:

    """

    The main function of the Kudasai program.

    """

    Kudasai.boot()

    try:

        ## determines if we will run the Kudasai CLI or the Kudasai Console
        if(__name__ == '__main__'):

            Toolkit.clear_console()

            ## if running console version
            if(len(sys.argv) <= 1):
                
                Kudasai.setup_kairyou_for_console()

                await Kudasai.run_kudasai_console()

                Logger.push_batch()

            ## if running cli version
            elif(len(sys.argv) == 3):

                Kudasai.setup_kairyou_for_cli(sys.argv[1], sys.argv[2])

                await Kudasai.run_kudasai_cli()

                Logger.push_batch()

            ## print usage statement
            else:
                    
                print("Usage: python Kudasai.py <input_file> <replacement_json>\n\n")
                print("or run Kudasai.py without any arguments to run the console version.\n\n")

                Logger.log_action("Usage: python Kudasai.py <input_file> <replacement_json>")

                Toolkit.pause_console()

                exit()

    except Exception as e:

        FileEnsurer.handle_critical_exception(e)

##---------------------------------/

asyncio.run(main())
