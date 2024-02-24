## built-in libraries
import os
import sys
import json
import asyncio
import re
import typing
import traceback

## third-party libraries
from kairyou import Kairyou
from kairyou import Indexer
from kairyou.types import NameAndOccurrence

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
    
    text_to_preprocess:str
    replacement_json:dict

    need_to_run_kairyou:bool = True

##-------------------start-of-boot()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def boot() -> None:

        """
        
        Does some logging and sets up the console window, regardless of whether the user is running the CLI, WebGUI, or Console version of Kudasai.

        """

        os.system("title " + "Kudasai")

        Toolkit.clear_console()

        FileEnsurer.setup_needed_files()

        Logger.clear_log_file()

        Logger.log_barrier()
        Logger.log_action("Kudasai started")
        Logger.log_action("Current version: " + Toolkit.CURRENT_VERSION)
        Logger.log_barrier()

        Logger.push_batch()
        Logger.clear_batch()

        try:

            with open(FileEnsurer.config_kijiku_rules_path, "r") as kijiku_rules_file:
                JsonHandler.current_kijiku_rules = json.load(kijiku_rules_file)

            JsonHandler.validate_json()

        except:

            print("Invalid kijiku_rules.json file. Please check the file for errors. If you are unsure, delete the file and run Kudasai again. Your kijiku rules file is located at: " + FileEnsurer.config_kijiku_rules_path)

            Toolkit.pause_console()

            raise Exception("Invalid kijiku_rules.json file. Please check the file for errors. If you are unsure, delete the file and run Kudasai again. Your kijiku rules file is located at: " + FileEnsurer.config_kijiku_rules_path)
        
##-------------------start-of-run_kairyou_indexer()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def run_kairyou_indexer(text_to_index:str, replacement_json:typing.Union[dict,str]) -> typing.Tuple[str, str]:

        """

        Runs the Kairyou Indexer.

        Parameters:
        text_to_index (str): The text to index.
        replacement_json (dict): The replacement json.

        Returns:

        
        """

        Toolkit.clear_console()

        knowledge_base = input("Please enter the path to the knowledge base you would like to use for the indexer (can be text, a path to a txt file, or a path to a directory of txt files):\n").strip('"')

        ## unique names is a list of named tuples, with the fields name and occurrence
        unique_names, indexing_log = Indexer.index(text_to_index, knowledge_base, replacement_json)

        ## for each name in unique_names, we need to replace that name in the text_to_process with >>>name<<<
        ## but since it returns the occurrence of the name, we only need to replace that occurrence of the name in the text_to_process
        ## So if a name has 42 occurrences, but only the 3rd and 4th occurrence were flagged, we only need to replace the 3rd and 4th occurrence of the name in the text_to_process

        text_to_index = Kudasai.mark_indexed_names(text_to_index, unique_names)

        return text_to_index, indexing_log
    
##-------------------start-of-mark_indexed_names()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def mark_indexed_names(text:str, unique_names:typing.List[NameAndOccurrence]) -> str:

        """

        Marks indexed names in the text.

        Parameters:
        text (str): The text to mark.
        unique_names (list - NameAndOccurrence): The list of unique names.

        Returns:
        str: The marked text.

        """

        for name_tuple in unique_names:
            name = name_tuple.name
            pattern = re.compile(re.escape(name)) ## Prepare regex pattern, escaping the name to handle special characters

            current_pos = 0
            new_text = ""
            last_end = 0

            for match in pattern.finditer(text):
                current_pos += 1
                if(current_pos == name_tuple.occurrence):  
                    new_text += text[last_end:match.start()] + f">>>{name}<<<"
                    last_end = match.end()

            new_text += text[last_end:]  # Append the rest of the text
            text = new_text

        return text

##-------------------start-of-run_kudasai()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
                
    @staticmethod
    async def run_kudasai() -> None:

        """

        Runs the Kudasai program. Used for CLI and Console versions of Kudasai. Not used for the WebGUI version of Kudasai.

        """

        Kudasai.handle_update_check()

        if(Kudasai.need_to_run_kairyou):

            indexing_log = ""

            if(Kudasai.replacement_json not in ["", FileEnsurer.blank_rules_path, FileEnsurer.standard_read_json(FileEnsurer.blank_rules_path)] and input("Would you like to use Kairyou's Indexer to index the preprocessed text? (1 for yes, 2 for no)\n") == "1"):
                Kudasai.text_to_preprocess, indexing_log = Kudasai.run_kairyou_indexer(Kudasai.text_to_preprocess, Kudasai.replacement_json)

            preprocessed_text, preprocessing_log, error_log = Kairyou.preprocess(Kudasai.text_to_preprocess, Kudasai.replacement_json)

            ## Need to set this so auto-translation can use the preprocessed text
            Kudasai.text_to_preprocess = preprocessed_text

            ## add index log to preprocessing log
            if(indexing_log != ""):
                preprocessing_log = indexing_log + "\n\n" + preprocessing_log

            print(preprocessing_log) 

            timestamp = Toolkit.get_timestamp(is_archival=True)

            FileEnsurer.write_kairyou_results(preprocessed_text, preprocessing_log, error_log, timestamp)
            
            Toolkit.pause_console("\nPress any key to continue to Auto-Translation...")
            Toolkit.clear_console()

        else:
            print("(Preprocessing skipped)")

        await Kudasai.determine_autotranslation_module()

        Toolkit.pause_console("\nPress any key to exit...")

##-------------------start-of-handle_update_check()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_update_check() -> None:

        """

        Checks for updates and prompts the user to update if there is an update available.

        """

        Kudasai.connection, update_prompt = Toolkit.check_update()

        if(update_prompt != ""):
            
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

        Kaiseki.text_to_translate = [line for line in Kudasai.text_to_preprocess.splitlines()]

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

        Kijiku.text_to_translate = [line for line in Kudasai.text_to_preprocess.splitlines()]

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
    Toolkit.clear_console()

    try:

        if(len(sys.argv) <= 1):
            await run_console_version()
        
        elif(len(sys.argv) in [2, 3]):
            await run_cli_version()

        else:
            print_usage_statement()

    except Exception as e:
        FileEnsurer.handle_critical_exception(e)

##-------------------start-of-run_console_version()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

async def run_console_version():

    """
    
    Runs the console version of Kudasai.

    """

    try:

        path_to_text_to_preprocess = input("Please enter the path to the input file to be processed:\n").strip('"')
        Kudasai.text_to_preprocess = FileEnsurer.standard_read_file(path_to_text_to_preprocess)
        Toolkit.clear_console()

        path_to_replacement_json = input("Please enter the path to the replacement json file:\n").strip('"')
        Kudasai.replacement_json = FileEnsurer.standard_read_json(path_to_replacement_json if path_to_replacement_json else FileEnsurer.blank_rules_path)
        Toolkit.clear_console()

    except Exception as e:
        print_usage_statement()

        print(traceback.format_exc())

        Toolkit.pause_console()

        raise e

    await Kudasai.run_kudasai()
    Logger.push_batch()

##-------------------start-of-run_cli_version()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

async def run_cli_version():

    """

    Runs the CLI version of Kudasai.

    """

    try:

        Kudasai.text_to_preprocess = FileEnsurer.standard_read_file(sys.argv[1].strip('"'))
        Kudasai.replacement_json = FileEnsurer.standard_read_json(sys.argv[2].strip('"') if(len(sys.argv) == 3) else FileEnsurer.blank_rules_path)

    except Exception as e:
        print_usage_statement()

        print(traceback.format_exc())

        Toolkit.pause_console()

        raise e

    if(len(sys.argv) == 2):
        Kudasai.need_to_run_kairyou = False

    await Kudasai.run_kudasai()
    Logger.push_batch()

##-------------------start-of-print_usage_statement()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def print_usage_statement():

    """

    Prints the usage statement for the CLI version of Kudasai.

    """

    print("Usage: python Kudasai.py <input_file> <replacement_json>\n\n")
    print("or run Kudasai.py without any arguments to run the console version.\n\n")
    Logger.log_action("Usage: python Kudasai.py <input_file> <replacement_json>")
    Toolkit.pause_console()
    exit()

if(__name__ == '__main__'):
    asyncio.run(main())