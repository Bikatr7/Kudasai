## built-in libaries
import os
import traceback
import json
import typing

## custom modules
from modules.common.decorators import permission_error_decorator
from modules.common.logger import Logger
from modules.common.toolkit import Toolkit

class FileEnsurer():

    """
    
    FileEnsurer is a class that is used to ensure that the required files and directories exist.
    Also serves as a place to store the paths to the files and directories. Some file related functions are also stored here.
    As well as some variables that are used to store the default kijiku rules and the allowed models across Kudasai.

    """

    ## main dirs
    script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    output_dir = os.path.join(script_dir, "output")
    archive_dir = os.path.join(output_dir, "archive")

    hugging_face_flag = os.path.join(script_dir, "util", "hugging_face_flag.py")

    ## main dirs (config is just under userprofile on windows, and under home on linux); secrets are under appdata on windows, and under .config on linux
    if(os.name == 'nt'):  ## Windows
        config_dir = os.path.join(os.environ['USERPROFILE'],"KudasaiConfig")
        secrets_dir = os.path.join(os.environ['APPDATA'],"KudasaiSecrets")
    else:  ## Linux
        config_dir = os.path.join(os.path.expanduser("~"), "KudasaiConfig")
        secrets_dir = os.path.join(os.path.expanduser("~"), ".config", "KudasaiSecrets")

    Logger.log_file_path = os.path.join(output_dir, "debug_log.txt")

    ##----------------------------------/

    ## sub dirs
    lib_dir = os.path.join(script_dir, "lib")
    gui_lib = os.path.join(lib_dir, "gui")
    jsons_dir = os.path.join(script_dir, "jsons")

    ##----------------------------------/

    ## output files
    preprocessed_text_path = os.path.join(output_dir, "preprocessed_text.txt") ## path for the preprocessed text
    translated_text_path = os.path.join(output_dir, "translated_text.txt") ## path for translated text

    je_check_path = os.path.join(output_dir, "je_check_text.txt") ## path for je check text (text generated by the translation modules to compare against the translated text)

    kairyou_log_path = os.path.join(output_dir, "preprocessing_results.txt")  ## path for kairyou log (the results of preprocessing)
    error_log_path = os.path.join(output_dir, "error_log.txt") ## path for the error log (errors generated by the preprocessing and translation modules)
    debug_log_path = Logger.log_file_path ## path for the debug log (debug info generated by the preprocessing and translation modules)
 
    ## kijiku rules
    external_kijiku_rules_path = os.path.join(script_dir,'kijiku_rules.json')
    config_kijiku_rules_path = os.path.join(config_dir,'kijiku_rules.json')

    ## api keys
    deepl_api_key_path = os.path.join(secrets_dir, "deepl_api_key.txt")
    openai_api_key_path = os.path.join(secrets_dir,'openai_api_key.txt')
    gemini_api_key_path = os.path.join(secrets_dir,'gemini_api_key.txt')

    ## favicon
    favicon_path = os.path.join(gui_lib, "Kudasai_Logo.png")

    DEFAULT_KIJIKU_RULES = {
    "base kijiku settings": {
        "prompt_assembly_mode": 1,
        "number_of_lines_per_batch": 36,
        "sentence_fragmenter_mode": 2,
        "je_check_mode": 2,
        "number_of_malformed_batch_retries": 1,
        "batch_retry_timeout": 300,
        "number_of_concurrent_batches": 5
    },

    "openai settings": {
        "openai_model": "gpt-4",
        "openai_system_message": "As a Japanese to English translator, translate narration into English simple past, everything else should remain in its original tense. Maintain original formatting, punctuation, and paragraph structure. Keep pre-translated terms and anticipate names not replaced. Preserve terms and markers marked with >>><<< and match the output's line count to the input's. Note: 〇 indicates chapter changes.",
        "openai_temperature": 0.3,
        "openai_top_p": 1.0,
        "openai_n": 1,
        "openai_stream": False,
        "openai_stop": None,
        "openai_logit_bias": None,
        "openai_max_tokens": None,
        "openai_presence_penalty": 0.0,
        "openai_frequency_penalty": 0.0
    },

    "gemini settings": {
        "gemini_model": "gemini-pro",
        "gemini_prompt": "As a Japanese to English translator, translate narration into English simple past, everything else should remain in its original tense. Maintain original formatting, punctuation, and paragraph structure. Keep pre-translated terms and anticipate names not replaced. Preserve terms and markers marked with >>><<< and match the output's line count to the input's. Note: 〇 indicates chapter changes.",
        "gemini_temperature": 0.3,
        "gemini_top_p": None,
        "gemini_top_k": None,
        "gemini_candidate_count": 1,
        "gemini_stream": False,
        "gemini_stop_sequences": None,
        "gemini_max_output_tokens": None
    }
}


    ALLOWED_OPENAI_MODELS  = [
        "gpt-3.5-turbo",
        "gpt-4",
        "gpt-4-turbo-preview",
        "gpt-3.5-turbo-0301",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-0125",
        "gpt-3.5-turbo-16k-0613",
        "gpt-3.5-turbo-1106",
        "gpt-4-0613",
        "gpt-4-32k-0613",
        "gpt-4-1106-preview",
        "gpt-4-0125-preview"
    ]

    ALLOWED_GEMINI_MODELS = [
        "gemini-1.0-pro-001",
        "gemini-1.0-pro-vision-001",
        "gemini-1.0-pro",
        "gemini-1.0-pro-vision",
        "gemini-pro",
        "gemini-pro-vision"
    ]

    INVALID_KIJIKU_RULES_PLACEHOLDER = {
    "INVALID JSON": 
    {
        "INVALID JSON":"INVALID JSON"
    }
    }

    ## rules
    blank_rules_path = os.path.join(jsons_dir, "blank_replacements.json")

    do_interrupt = False
    need_to_run_kairyou = True

##-------------------start-of-check_if_hugging_space()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def check_if_hugging_space() -> bool:
    
        """
        
        Determines if Kudasai is running on a Hugging Face server.

        """

        return os.path.exists(FileEnsurer.hugging_face_flag)

##--------------------start-of-exit_kudasai()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def exit_kudasai():

        """
        
        Pushes the log batch to the log and exits.

        """

        print("Cleaning up and exiting...")

        Logger.push_batch()

        exit()

##-------------------start-of-setup_needed_files()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    @permission_error_decorator()
    def setup_needed_files() -> None:

        """

        Ensures that the required files and directories exist.

        """

        ## creates the output directory and config directory if they don't exist
        FileEnsurer.standard_create_directory(FileEnsurer.config_dir)
        FileEnsurer.standard_create_directory(FileEnsurer.output_dir)
        FileEnsurer.standard_create_directory(FileEnsurer.secrets_dir)

        ## creates and clears the log file
        Logger.clear_log_file()

        ## creates the 5 output files
        FileEnsurer.standard_create_file(FileEnsurer.preprocessed_text_path)
        FileEnsurer.standard_create_file(FileEnsurer.translated_text_path)
        FileEnsurer.standard_create_file(FileEnsurer.je_check_path)
        FileEnsurer.standard_create_file(FileEnsurer.kairyou_log_path)
        FileEnsurer.standard_create_file(FileEnsurer.error_log_path)

        ## creates the kijiku rules file if it doesn't exist
        if(os.path.exists(FileEnsurer.config_kijiku_rules_path) == False):
            with open(FileEnsurer.config_kijiku_rules_path, 'w+', encoding='utf-8') as file:
                json.dump(FileEnsurer.DEFAULT_KIJIKU_RULES, file)

##--------------------start-of-standard_create_directory()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    @permission_error_decorator()
    def standard_create_directory(directory_path:str) -> None:

        """

        Creates a directory if it doesn't exist, as well as logs what was created.

        Parameters:
        directory_path (str) : path to the directory to be created.

        """

        if(os.path.isdir(directory_path) == False):
            os.mkdir(directory_path)
            Logger.log_action(directory_path + " created due to lack of the folder")

##--------------------start-of-standard_create_file()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    @permission_error_decorator()
    def standard_create_file(file_path:str) -> None:

        """

        Creates a file if it doesn't exist, truncates it,  as well as logs what was created.

        Parameters:
        file_path (str) : path to the file to be created.

        """

        if(os.path.exists(file_path) == False):
            Logger.log_action(file_path + " was created due to lack of the file")
            with open(file_path, "w+", encoding="utf-8") as file:
                file.truncate()

##--------------------start-of-modified_create_file()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    @permission_error_decorator()
    def modified_create_file(file_path:str, content_to_write:str) -> bool:

        """

        Creates a path if it doesn't exist or if it is blank or empty, writes to it, as well as logs what was created.

        Parameters:
        file_path (str) : path to the file to be created.
        content to write (str) : content to be written to the file.

        Returns:
        bool : whether or not the file was overwritten.

        """

        did_overwrite = False

        if(os.path.exists(file_path) == False or os.path.getsize(file_path) == 0):
            Logger.log_action(file_path + " was created due to lack of the file or because it is blank")
            with open(file_path, "w+", encoding="utf-8") as file:
                file.write(content_to_write)

            did_overwrite = True

        return did_overwrite

##--------------------start-of-standard_overwrite_file()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    @permission_error_decorator()
    def standard_overwrite_file(file_path:str, content_to_write:str, omit:bool = True) -> None:

        """

        Writes to a file, creates it if it doesn't exist, overwrites it if it does, as well as logs what occurred.

        Parameters:
        file_path (str) : path to the file to be overwritten.
        content to write (str) : content to be written to the file.
        omit (bool | optional) : whether or not to omit the content from the log.

        """

        with open(file_path, "w+", encoding="utf-8") as file:
            file.write(content_to_write)

        if(omit):
            content_to_write = "(Content was omitted)"
        
        Logger.log_action(file_path + " was overwritten with the following content: " + content_to_write)

##--------------------start-of-clear_file()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    @permission_error_decorator()
    def clear_file(file_path:str) -> None:

        """

        Clears a file, as well as logs what occurred.

        Parameters:
        file_path (str) : path to the file to be cleared.

        """

        with open(file_path, "w+", encoding="utf-8") as file:
            file.truncate()

        Logger.log_action(file_path + " was cleared")

##--------------------start-of-standard_read_file()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    @permission_error_decorator()
    def standard_read_file(file_path:str) -> str:

        """

        Reads a file.

        Parameters:
        file_path (str) : path to the file to be read.

        Returns:
        content (str) : the content of the file.

        """

        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        return content

##-------------------start-of-handle_critical_exception()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_critical_exception(critical_exception:Exception) -> None:

        """

        Handles a critical exception by logging it, pausing the console so the user can see the error, and then re-raising it.

        Parameters:
        critical_exception (object - Exception) : the exception to be handled.

        """

        Logger.log_barrier()
        Logger.log_action("Kudasai has crashed", output=True)
        Logger.log_action("Please send the following to the developer on github at https://github.com/Bikatr7/Kudasai/issues :", output=True, omit_timestamp=True)

        traceback_msg = traceback.format_exc()

        Logger.log_action(traceback_msg ,output=True, omit_timestamp=True)

        Logger.push_batch()

        Toolkit.pause_console()

        raise critical_exception
    
##-------------------start-of-archive_results()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------


    @staticmethod
    @permission_error_decorator()
    def archive_results(list_of_result_tuples:typing.List[typing.Tuple[str,str]], module:str, timestamp:str) -> None:

        """

        Creates a directory in the archive folder and writes the results to files in that directory.

        Parameters:
        list_of_result_tuples (list - tuple - str, str) : list of tuples containing the filename and content of the results to be archived.
        module (str) : name of the module that generated the results.
        timestamp (str) : timestamp of when the results were generated.

        """

        archival_path = os.path.join(FileEnsurer.archive_dir, f'{module}_run_{timestamp}')
        FileEnsurer.standard_create_directory(archival_path)

        for result in list_of_result_tuples:
            (filename, content) = result
            result_file_path = os.path.join(archival_path, f'{filename}_{timestamp}.txt')

            with open(result_file_path, "w", encoding="utf-8") as file:
                file.writelines(content)

##-------------------start-of-standard_read_json()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    @permission_error_decorator()
    def standard_read_json(file_path:str) -> dict:

        """

        Reads a json file and returns the json object.

        Parameters:
        file_path (str) : path to the json file to be read.

        Returns:
        json_object (dict) : the json object.

        """

        with open(file_path, "r", encoding="utf-8") as file:
            json_object = json.load(file)

        return json_object

##-------------------start-of-write_kairyou_results()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    @permission_error_decorator()
    def write_kairyou_results(text_to_preprocess:str, preprocessing_log:str, error_log:str, timestamp:str) -> None:

        """
        
        This function is called to write the results to the output directory.

        Parameters:
        text_to_preprocess (str) : the text that was preprocessed.
        preprocessing_log (str) : the log of the preprocessing results.
        error_log (str) : the log of any errors that occurred during preprocessing.
        timestamp (str) : the timestamp of when the results were generated (Can be obtained from Toolkit.get_timestamp(is_archival=True))

        """

        ## ensures the output directory exists, cause it could get moved or fucked with.
        FileEnsurer.standard_create_directory(FileEnsurer.output_dir)

        with(open(FileEnsurer.preprocessed_text_path, 'w', encoding='utf-8')) as file:
            file.write(text_to_preprocess) 

        with open(FileEnsurer.kairyou_log_path, 'w', encoding='utf-8') as file:
            file.write(preprocessing_log)

        with open(FileEnsurer.error_log_path, 'w', encoding='utf-8') as file:
            file.write(error_log)

        with open(FileEnsurer.je_check_path, 'w', encoding='utf-8') as file:
            file.truncate()

        with open(FileEnsurer.translated_text_path, 'w', encoding='utf-8') as file:
            file.truncate()

        ## Instructions to create a copy of the output for archival
        FileEnsurer.standard_create_directory(FileEnsurer.archive_dir)

        Logger.push_batch()
        Logger.clear_batch()

        list_of_result_tuples = [('kairyou_preprocessed_text', text_to_preprocess),
                                 ('kairyou_preprocessing_log', preprocessing_log),
                                 ('kairyou_error_log', error_log),
                                 ('debug_log', FileEnsurer.standard_read_file(Logger.log_file_path))]

        FileEnsurer.archive_results(list_of_result_tuples,
                                    module='kairyou', timestamp=timestamp)

