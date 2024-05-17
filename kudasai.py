## built-in libraries
import os
import sys
import json
import asyncio
import re
import typing
import logging
import argparse

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
    knowledge_base:str

    need_to_run_kairyou:bool = True
    need_to_run_indexer:bool = True

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
        
        Does some logging and sets up the console window, and translator settings, regardless of whether the user is running the CLI, WebGUI, or Console version of Kudasai.

        """

        os.system("title " + "Kudasai")

        Toolkit.clear_console()

        ## Need to create the output dir FIRST as logging files are located in the output folder
        FileEnsurer.standard_create_directory(FileEnsurer.output_dir)

        Kudasai.setup_logging()

        FileEnsurer.setup_needed_files()

        logging.debug(f"Kudasai started; Current version : {Toolkit.CURRENT_VERSION}")

        try:

            with open(FileEnsurer.config_translation_settings_path, "r") as translation_settings:
                JsonHandler.current_translation_settings = json.load(translation_settings)

            JsonHandler.validate_json()

            assert JsonHandler.current_translation_settings != FileEnsurer.INVALID_TRANSLATION_SETTINGS_PLACEHOLDER

        except:

            print("Invalid translation_settings.json file. Please check the file for errors or mistakes. If you are unsure, delete the file and run Kudasai again. Your file is located at: " + FileEnsurer.config_translation_settings_path)

            Toolkit.pause_console()

            raise Exception("Invalid translation_settings.json file. Please check the file for errors or mistakes. If you are unsure, delete the file and run Kudasai again. Your file is located at: " + FileEnsurer.config_translation_settings_path)
        
##-------------------start-of-run_kairyou_indexer()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def run_kairyou_indexer(text_to_index:str, replacement_json:typing.Union[dict,str], knowledge_base:str) -> typing.Tuple[str, str]:

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

            if(Kudasai.replacement_json not in ["", 
                                                FileEnsurer.blank_rules_path, 
                                                FileEnsurer.standard_read_json(FileEnsurer.blank_rules_path)] 

               and Kudasai.need_to_run_indexer
               and Kudasai.knowledge_base != ""):
                Kudasai.text_to_preprocess, indexing_log = Kudasai.run_kairyou_indexer(Kudasai.text_to_preprocess, Kudasai.replacement_json, Kudasai.knowledge_base)

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
    async def run_translator(is_cli:bool=False) -> None:

        """
        
        If the user is running the CLI or Console version of Kudasai, this function is called to run the Translator module.

        """

        Translator.is_cli = is_cli

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
        
        elif(len(sys.argv) in [2, 3, 4, 5, 6]):
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

        if(path_to_replacement_json != ""):
            Kudasai.knowledge_base = input("Please enter the path to the knowledge base you would like to use for the name indexer (can be text, a path to a txt file, or a path to a directory of txt files (Press enter if skipping name indexing):\n").strip('"')
            Toolkit.clear_console()

    except Exception as e:
        print_usage_statement()

        raise e
    
    print("In progress...")

    await Kudasai.run_kudasai()

##-------------------start-of-run_cli_version()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

async def run_cli_version():

    """

    Runs the CLI version of Kudasai.

    """

    def determine_argument_type(arg:str) -> str:

        """

        Determines the third argument for the CLI version of Kudasai.

        """

        conditions = [
            (lambda arg: arg in ["deepl", "openai", "gemini"], "translation_method"),
            (lambda arg: os.path.exists(arg) and not ".json" in arg, "text_to_translate"),
            (lambda arg: len(arg) > 10 and not os.path.exists(arg), "api_key"),
            (lambda arg: arg == "translate", "identifier"),
            (lambda arg: os.path.exists(arg) and ".json" in arg, "translation_settings_json")
        ]

        for condition, result in conditions:
            if(condition(arg)):
                print(result)
                return result

        raise Exception("Invalid argument. Please use 'deepl', 'openai', or 'gemini'.")
        
    mode = ""

    try:

        indices = {
            "preprocess": {"text_to_preprocess_index": 2, "replacement_json_index": 3, "knowledge_base_index": 4},
            "translate": {"text_to_translate_index": 2},
            "--help": {}
        }

        try:
            arg_indices = indices[sys.argv[1]]
            mode = sys.argv[1]

        except KeyError:
            print_usage_statement()
            raise Exception("Invalid mode. Please use 'preprocess' or 'translate'. Please use --help for more information.")
        
        if(mode == "preprocess"):
    
            Kudasai.text_to_preprocess = FileEnsurer.standard_read_file(sys.argv[arg_indices['text_to_preprocess_index']].strip('"'))
            Kudasai.replacement_json = FileEnsurer.standard_read_json(sys.argv[arg_indices['replacement_json_index']].strip('"')) if len(sys.argv) >= arg_indices['replacement_json_index'] + 1 else FileEnsurer.standard_read_json(FileEnsurer.blank_rules_path)
            Kudasai.knowledge_base = sys.argv[arg_indices['knowledge_base_index']].strip('"') if len(sys.argv) == arg_indices['knowledge_base_index'] + 1 else ""

            if(len(sys.argv) == 2):
                Kudasai.need_to_run_kairyou = False
            elif(len(sys.argv) == 3):
                Kudasai.need_to_run_indexer = False
        
            await Kudasai.run_kudasai()

        elif(mode == "translate"):

            method_to_translation_mode = {
                "openai": "1",
                "gemini": "2",
                "deepl": "3"
            }

            Kudasai.text_to_preprocess = FileEnsurer.standard_read_file(sys.argv[arg_indices['text_to_translate_index']].strip('"'))
            
            sys.argv.pop(0)

            arg_dict = {arg.strip('"'): determine_argument_type(arg.strip('"')) for arg in sys.argv}

            assert len(arg_dict) == len(set(arg_dict)), "Invalid arguments. Please use --help for more information."

            arg_type_action_map = {
                "translation_method": lambda arg: setattr(Translator, 'TRANSLATION_METHOD', method_to_translation_mode[arg]),
                "translation_settings_json": lambda arg: setattr(JsonHandler, 'current_translation_settings', FileEnsurer.standard_read_json(arg)),
                "api_key": lambda arg: setattr(Translator, 'pre_provided_api_key', arg),
                "identifier": lambda arg: None,
                "text_to_translate": lambda arg: setattr(Kudasai, 'text_to_preprocess', FileEnsurer.standard_read_file(arg))
            }

            for arg, arg_type in arg_dict.items():
                if(arg_type in arg_type_action_map):
                    arg_type_action_map[arg_type](arg)
                else:
                    raise Exception("Invalid argument type. Please use --help for more information.")

            await Kudasai.run_translator(is_cli=True)

        else:
            print_usage_statement() 

    except Exception as e:
        print_usage_statement()
        raise e
    
##-------------------start-of-print_usage_statement()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def print_usage_statement():

    """

    Prints the usage statement for the CLI version of Kudasai.

    """
    python_command = "python" if Toolkit.is_windows() else "python3"

    print(f"""
Usage: {python_command} Kudasai.py <mode> <required_arguments> [optional_arguments]

Modes:
  preprocess
    Preprocesses the text file using the provided replacement JSON.

    Required arguments:
      <input_file>              Path to the text file to preprocess. This a path to a text file
      <replacement_json>        Path to the replacement JSON file. This is a path to a json file.

    Optional arguments:
      <knowledge_base>          Path to the knowledge base file. This can be either a directory, file, or even text.

    Example:
      {python_command} Kudasai.py preprocess "C:\\path\\to\\input_file.txt" "C:\\path\\to\\replacement_json.json" "C:\\path\\to\\knowledge_base"

  translate
    Translates the text file using the specified translation method.

    Required arguments:
      <input_file>              Path to the text file to translate. This is a txt file.

    Optional arguments:
      <translation_method>      Translation method to use ('deepl', 'openai', or 'gemini'). This defaults to deepl
      <translation_settings_json> Path to the translation settings JSON file. This will override the current loaded settings.
      <api_key>                  API key for the translation service. If not provided, it will use the one on file, otherwise it will ask if not provided

    Example:
      {python_command} Kudasai.py translate "C:\\path\\to\\input_file.txt" gemini "C:\\path\\to\\translation_settings.json" "YOUR API KEY"

Additional Notes:
- All arguments should be enclosed in double quotes if they contain spaces. But double quotes are optional and will be striped. Single quotes are not allowed
- For more information, refer to the documentation at README.md
""")


##-------------------start-of-submain()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------


if(__name__ == "__main__"):
    asyncio.run(main())