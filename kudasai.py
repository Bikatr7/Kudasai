## built-in libraries
import os
import sys
import json
import asyncio


## third-party libraries
from kairyou import Kairyou

## custom modules
from models.kaiseki import Kaiseki 
from models.kijiku import Kijiku

from handlers.json_handler import JsonHandler

from modules.common.toolkit import Toolkit
from modules.common.file_ensurer import FileEnsurer
from modules.common.logger import Logger

##-------------------start-of-Kudasai---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Kudasai:

    """

    Kudasai class is the main class for the Kudasai program. It handles all logic for CLI & Console versions of Kudasai.
    
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

        FileEnsurer.setup_needed_files()

        Logger.log_barrier()
        Logger.log_action("Kudasai started")
        Logger.log_action("Current version: " + Toolkit.CURRENT_VERSION)
        Logger.log_barrier()

        Logger.push_batch()

        try:

            with open(FileEnsurer.config_kijiku_rules_path, "r") as kijiku_rules_file:
                JsonHandler.current_kijiku_rules = json.load(kijiku_rules_file)

            JsonHandler.validate_json()

        except:

            print("Invalid kijiku_rules.json file. Please check the file for errors. If you are unsure, delete the file and run Kudasai again. Your kijiku rules file is located at: " + FileEnsurer.config_kijiku_rules_path)

            Toolkit.pause_console()

            raise Exception("Invalid kijiku_rules.json file. Please check the file for errors. If you are unsure, delete the file and run Kudasai again. Your kijiku rules file is located at: " + FileEnsurer.config_kijiku_rules_path)
        
##-------------------start-of-setup_kairyou()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def setup_kairyou(input_file:str | None = None, replacement_json_path:str | None = None, is_cli:bool=False) -> typing.Tuple[dict, str]:

        """
        
        If the user is running the WebGUI version of Kudasai, this function is called to setup the text to be processed and the replacement json file.
        
        Parameters:
        input_file (str | None | default=None) : The path to the input file to be processed.
        replacement_json (str | None | default=None) : The path to the replacement json file.
        is_cli (bool | default=False) : Whether the user is running the CLI version of Kudasai.

        """

        if(not is_cli):
            input_file = input("Please enter the path to the input file to be processed:\n").strip('"')
            Toolkit.clear_console()

            replacement_json_path = input("Please enter the path to the replacement json file:\n").strip('"')
            Toolkit.clear_console()

        ## try to load the replacement json file
        try:

            with open(replacement_json_path, 'r', encoding='utf-8') as file:  ## type: ignore
                replacement_json = json.load(file) 
    
        ## if not just skip preprocessing
        except:
            
            FileEnsurer.need_to_run_kairyou = False
            replacement_json = {}

        try:
            with open(input_file, 'r', encoding='utf-8') as file:  ## type: ignore
                japanese_text = file.read()

        except:

            Logger.log_action("Invalid txt file.", output=True, omit_timestamp=True)

            Toolkit.pause_console()

            raise Exception("Invalid txt file.")
        
        Kairyou.setup(japanese_text, replacement_json)
        
##-------------------start-of-run_kudasai()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
                
    @staticmethod
    async def run_kudasai(is_cli:bool=False) -> None:

        """

        Runs the Kudasai program.

        Parameters:
        is_cli (bool | default=False) : Whether the user is running the CLI version of Kudasai.

        """

        Kudasai.handle_update_check()

        Kairyou.preprocess()

        if(not is_cli):
            print(Kairyou.preprocessing_log) 

        Kairyou.write_kairyou_results() 

        if(not is_cli):
            Toolkit.pause_console("\nPress any key to continue to Auto-Translation...")

        await Kudasai.determine_autotranslation_module()

        if(not is_cli):
            Toolkit.pause_console("\nPress any key to exit...")

##-------------------start-of-handle_update_check()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_update_check() -> None:

        """

        Checks for updates and prompts the user to update if there is an update available.

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

        Toolkit.clear_console()

        ## if running console version
        if(len(sys.argv) <= 1):
            
            Kudasai.setup_kairyou()

            await Kudasai.run_kudasai()

            Logger.push_batch()

        ## if running cli version
        elif(len(sys.argv) == 3):

            Kudasai.setup_kairyou(input_file=sys.argv[1], replacement_json_path=sys.argv[2], is_cli=True)

            await Kudasai.run_kudasai(is_cli=True)

            Logger.push_batch()

        ## if running cli version but skipping preprocessing
        elif(len(sys.argv) == 2):

            Kudasai.setup_kairyou(input_file=sys.argv[1], is_cli=True)

            await Kudasai.run_kudasai(is_cli=True)

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
if(__name__ == '__main__'):
    asyncio.run(main())
