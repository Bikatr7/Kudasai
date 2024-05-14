## built-in libraries
import os
import sys
import json
import asyncio
import re
import typing
import logging

## third-party libraries
from kairyou import Kairyou
from kairyou import Indexer
from kairyou.types import NameAndOccurrence

## custom modules
from modules.common.translator import Translator

from handlers.json_handler import JsonHandler

from modules.common.toolkit import Toolkit
from modules.common.file_ensurer import FileEnsurer

##-------------------start-of-Kudasai---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Kudasai:

    """

    Kudasai class is the main class for the Kudasai program. It handles all logic for CLI & Console versions of Kudasai.
    
    """

    connection:bool
    
    text_to_preprocess:str
    replacement_json:dict

    need_to_run_kairyou:bool = True

##-------------------start-of-setup_logging()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def setup_logging() -> None:

        """

        Sets up logging for the Kudasai program.

        """

        ## Debug log setup
        debug_log_handler = logging.FileHandler(FileEnsurer.debug_log_path, mode='w+', encoding='utf-8')
        debug_log_handler.setLevel(logging.DEBUG)
        debug_formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(filename)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        debug_log_handler.setFormatter(debug_formatter)

        ## Error log setup
        error_log_handler = logging.FileHandler(FileEnsurer.error_log_path, mode='w+', encoding='utf-8')
        error_log_handler.setLevel(logging.WARNING)
        error_formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(filename)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        error_log_handler.setFormatter(error_formatter)

        ## Console handler setup
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console_formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(filename)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        console.setFormatter(console_formatter)

        ## Add handlers to the logger
        logger = logging.getLogger('')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(debug_log_handler)
        logger.addHandler(error_log_handler)
        logger.addHandler(console)

        ## Ensure only INFO level and above messages are sent to the console
        console.setLevel(logging.INFO)

##-------------------start-of-boot()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def boot() -> None:

        """
        
        Does some logging and sets up the console window, regardless of whether the user is running the CLI, WebGUI, or Console version of Kudasai.

        """

        os.system("title " + "Kudasai")

        Toolkit.clear_console()

        ## Need to create the output dir FIRST as logging files are located in the output folder
        FileEnsurer.standard_create_directory(FileEnsurer.output_dir)

        Kudasai.setup_logging()

        FileEnsurer.setup_needed_files()

        logging.debug(f"Kudasai started; Current version : {Toolkit.CURRENT_VERSION}")

        try:

            with open(FileEnsurer.config_translation_settings_path, "r") as kijiku_rules_file:
                JsonHandler.current_translation_settings = json.load(kijiku_rules_file)

            JsonHandler.validate_json()

            assert JsonHandler.current_translation_settings != FileEnsurer.INVALID_TRANSLATION_SETTINGS_PLACEHOLDER

        except:

            print("Invalid translation_settings.json file. Please check the file for errors or mistakes. If you are unsure, delete the file and run Kudasai again. Your file is located at: " + FileEnsurer.config_translation_settings_path)

            Toolkit.pause_console()

            raise Exception("Invalid translation_settings.json file. Please check the file for errors or mistakes. If you are unsure, delete the file and run Kudasai again. Your file is located at: " + FileEnsurer.config_translation_settings_path)
        
##-------------------start-of-run_kairyou_indexer()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def run_kairyou_indexer(text_to_index:str, replacement_json:typing.Union[dict,str]) -> typing.Tuple[str, str]:

        """

        Runs the Kairyou Indexer.

        Parameters:
        text_to_index (str): The text to index.
        replacement_json (dict): The replacement json.

        Returns:
        text_to_index (str): The indexed text.
        indexing_log (str): The log of the indexing process.
        
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
        This does not mark all names, but rather the specific occurrences of the names that were flagged by the indexer.

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

            new_text += text[last_end:]  ## Append the rest of the text
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

            if(preprocessing_log == "Skipped"):
                preprocessing_log = "Preprocessing skipped."

            print(preprocessing_log) 

            timestamp = Toolkit.get_timestamp(is_archival=True)

            FileEnsurer.write_kairyou_results(preprocessed_text, preprocessing_log, error_log, timestamp)
            
            Toolkit.pause_console("\nPress any key to continue to Auto-Translation...")
            Toolkit.clear_console()

        else:
            print("(Preprocessing skipped)")

        await Kudasai.run_translator()

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
    
##-------------------start-of-run_translator()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    async def run_translator() -> None:

        """
        
        If the user is running the CLI or Console version of Kudasai, this function is called to run the Translator module.

        """

        logging.info("Translator started")

        Toolkit.clear_console()

        Translator.text_to_translate = [line for line in Kudasai.text_to_preprocess.splitlines()]

        await Translator.translate()

        Toolkit.clear_console()

        print(Translator.translation_print_result)

        Translator.write_translator_results()

##-------------------start-of-main()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

async def main() -> None:

    """

    The main function of the Kudasai program.

    """

    try:

        Kudasai.boot()
        Toolkit.clear_console()

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

        path_to_text_to_preprocess = input("Please enter the path to the input file to be preprocessed/translated:\n").strip('"')
        Kudasai.text_to_preprocess = FileEnsurer.standard_read_file(path_to_text_to_preprocess)
        Toolkit.clear_console()

        path_to_replacement_json = input("Please enter the path to the replacement json file (Press enter if skipping to translation):\n").strip('"')
        Kudasai.replacement_json = FileEnsurer.standard_read_json(path_to_replacement_json if path_to_replacement_json else FileEnsurer.blank_rules_path)
        Toolkit.clear_console()

    except Exception as e:
        print_usage_statement()

        raise e

    await Kudasai.run_kudasai()

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

        raise e

    if(len(sys.argv) == 2):
        Kudasai.need_to_run_kairyou = False

    await Kudasai.run_kudasai()

##-------------------start-of-print_usage_statement()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def print_usage_statement():

    """

    Prints the usage statement for the CLI version of Kudasai.

    """

    python_command = "python" if Toolkit.is_windows() else "python3"

    print(f"Usage: {python_command} Kudasai.py <input_file> <replacement_json>"
          f"or run Kudasai.py without any arguments to run the console version.\n")

##-------------------start-of-submain()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------


if(__name__ == "__main__"):
    asyncio.run(main())