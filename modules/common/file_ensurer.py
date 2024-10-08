## built-in libaries
import os
import traceback
import json
import typing
import shutil
import logging

## custom modules
from modules.common.decorators import permission_error_decorator
from modules.common.toolkit import Toolkit

class FileEnsurer():

    """
    
    FileEnsurer is a class that is used to ensure that the required files and directories exist.
    Also serves as a place to store the paths to the files and directories. Some file related functions are also stored here.
    As well as some variables that are used to store the default translation settings and the allowed models across Kudasai.

    """

    ## main dirs
    script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    output_dir = os.path.join(script_dir, "output")
    archive_dir = os.path.join(output_dir, "archive")

    hugging_face_flag = os.path.join(script_dir, "util", "hugging_face_flag.py")

    ## main dirs (config is just under userprofile on windows, and under home on linux); secrets are under appdata on windows, and under .config on linux
    if(Toolkit.is_windows()):  ## Windows
        config_dir = os.path.join(os.environ['USERPROFILE'],"KudasaiConfig")
        secrets_dir = os.path.join(os.environ['APPDATA'],"KudasaiSecrets")
    else:  ## Linux
        config_dir = os.path.join(os.path.expanduser("~"), "KudasaiConfig")
        secrets_dir = os.path.join(os.path.expanduser("~"), ".config", "KudasaiSecrets")

    ##----------------------------------/

    ## sub dirs
    lib_dir = os.path.join(script_dir, "lib")
    common_lib = os.path.join(lib_dir, "common")
    gui_lib = os.path.join(lib_dir, "gui")
    jsons_dir = os.path.join(script_dir, "jsons")

    ##----------------------------------/

    ## output files
    preprocessed_text_path = os.path.join(output_dir, "preprocessed_text.txt") 
    translated_text_path = os.path.join(output_dir, "translated_text.txt")

    je_check_path = os.path.join(output_dir, "je_check_text.txt") 

    kairyou_log_path = os.path.join(output_dir, "preprocessing_results.txt")  
    error_log_path = os.path.join(output_dir, "error_log.txt") 
    debug_log_path = os.path.join(output_dir, "debug_log.txt") 
 
    ## translation settings
    external_translation_settings_path = os.path.join(script_dir,'translation_settings.json')
    config_translation_settings_path = os.path.join(config_dir,'translation_settings.json')
    
    external_translation_genders_path = os.path.join(script_dir,'genders.json')
    config_translation_genders_path = os.path.join(config_dir, 'genders.json')

    ## api keys
    deepl_api_key_path = os.path.join(secrets_dir, "deepl_api_key.txt")
    openai_api_key_path = os.path.join(secrets_dir,'openai_api_key.txt')
    gemini_api_key_path = os.path.join(secrets_dir,'gemini_api_key.txt')
    google_translate_service_key_json_path = os.path.join(secrets_dir, "google_translate_service_key.json")
    
    ## temp files
    temp_file_path = os.path.join(script_dir, "temp.txt")

    ## favicon
    favicon_path = os.path.join(gui_lib, "Kudasai_Logo.png")

    ## js
    js_save_to_file_path = os.path.join(gui_lib, "save_to_file.js")
    js_save_to_zip_path = os.path.join(gui_lib, "save_to_zip.js")

    ## translation settings description
    translation_settings_description_path = os.path.join(common_lib, "translation_settings_description.txt")

    DEFAULT_TRANSLATION_SETTING = {
    "base translation settings": {
        "prompt_assembly_mode": 1,
        "number_of_lines_per_batch": 36,
        "sentence_fragmenter_mode": 2,
        "je_check_mode": 2,
        "number_of_malformed_batch_retries": 1,
        "batch_retry_timeout": 300,
        "number_of_concurrent_batches": 5,
        "gender_context_insertion": False,
        "is_cote": False,
    },

    "openai settings": {
        "openai_model": "gpt-4",
        "openai_system_message": "Translate the text from Japanese to English.",
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
        "gemini_prompt": "Translate the text from Japanese to English",
        "gemini_temperature": 0.3,
        "gemini_top_p": None,
        "gemini_top_k": None,
        "gemini_candidate_count": 1,
        "gemini_stream": False,
        "gemini_stop_sequences": None,
        "gemini_max_output_tokens": None
    },

    "deepl settings":{
        "deepl_context": "",
        "deepl_split_sentences": "ALL",
        "deepl_preserve_formatting": True,
        "deepl_formality": "default"
    }
}
    
    DEFAULT_GENDER_SETTINGS = {
    "Male": {},
    "Female": {},
    "Unknown": {}
    }
    
    INVALID_TRANSLATION_SETTINGS_PLACEHOLDER = {
    "INVALID JSON": 
    {
        "INVALID JSON":"INVALID JSON"
    }
    }

    INVALID_GENDER_SETTINGS_PLACEHOLDER = {
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
    def is_hugging_space() -> bool:
    
        """
        
        Determines if Kudasai is running on a Hugging Face server.

        Returns:
        bool : whether or not Kudasai is running on a Hugging Face server.

        """

        return os.path.exists(FileEnsurer.hugging_face_flag)

##--------------------start-of-exit_kudasai()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def exit_kudasai():

        """
        
        Pushes the log batch to the log and exits.

        """

        print("Cleaning up and exiting...")

        exit()

##-------------------start-of-setup_needed_files()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    @permission_error_decorator()
    def setup_needed_files() -> None:

        """

        Ensures that the required files and directories exist.

        Decorated By:
        permission_error_decorator

        """


        FileEnsurer.purge_storage()

        ## creates the output directory and config directory if they don't exist
        FileEnsurer.standard_create_directory(FileEnsurer.config_dir)
        FileEnsurer.standard_create_directory(FileEnsurer.output_dir)
        FileEnsurer.standard_create_directory(FileEnsurer.secrets_dir)

        ## creates the 5 output files
        FileEnsurer.standard_create_file(FileEnsurer.preprocessed_text_path)
        FileEnsurer.standard_create_file(FileEnsurer.translated_text_path)
        FileEnsurer.standard_create_file(FileEnsurer.je_check_path)
        FileEnsurer.standard_create_file(FileEnsurer.kairyou_log_path)
        FileEnsurer.standard_create_file(FileEnsurer.error_log_path)

        ## creates the kijiku rules file if it doesn't exist
        if(os.path.exists(FileEnsurer.config_translation_settings_path) == False):
            with open(FileEnsurer.config_translation_settings_path, 'w+', encoding='utf-8') as file:
                json.dump(FileEnsurer.DEFAULT_TRANSLATION_SETTING, file)

        ## creates the genders file if it doesn't exist
        if(os.path.exists(FileEnsurer.config_translation_genders_path) == False):
            with open(FileEnsurer.config_translation_genders_path, 'w+', encoding='utf-8') as file:
                json.dump(FileEnsurer.DEFAULT_GENDER_SETTINGS, file)

##-------------------start-of-purge_storage()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
                
    @staticmethod
    @permission_error_decorator()
    def purge_storage() -> None:

        """
        
        In case of hugging face, purges the storage.

        Decorated By:
        permission_error_decorator

        """

        if(not FileEnsurer.is_hugging_space()):
            logging.debug("Not running on Hugging Face, skipping storage purge")
            return
        
        logging.debug("Running on Hugging Face, purging storage")

        stuff_to_purge = [
            FileEnsurer.temp_file_path
        ]

        stuff_to_truncate = [
            FileEnsurer.output_dir,
            FileEnsurer.archive_dir
        ]

        for thing in stuff_to_purge:
            if(os.path.exists(thing)):

                if(os.path.isdir(thing)):
                    shutil.rmtree(thing)

                else:
                    os.remove(thing)

        for thing in stuff_to_truncate:
            if(os.path.exists(thing)):
                if(os.path.isdir(thing)):
                    for file in os.listdir(thing):
                        file_path = os.path.join(thing, file)
                        if(os.path.isfile(file_path)):
                            with open(file_path, "w", encoding="utf-8") as file:
                                file.truncate()

                else:
                    with open(thing, "w", encoding="utf-8") as file:
                        file.truncate()
                        
##--------------------start-of-standard_create_directory()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    @permission_error_decorator()
    def standard_create_directory(directory_path:str) -> None:

        """

        Creates a directory if it doesn't exist, as well as logs what was created.

        Parameters:
        directory_path (str) : path to the directory to be created.

        Decorated By:
        permission_error_decorator

        """

        if(os.path.isdir(directory_path) == False):
            os.makedirs(directory_path)
            logging.debug(directory_path + " created due to lack of the folder")

##--------------------start-of-standard_create_file()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    @permission_error_decorator()
    def standard_create_file(file_path:str) -> None:

        """

        Creates a file if it doesn't exist, truncates it,  as well as logs what was created.

        Parameters:
        file_path (str) : path to the file to be created.

        Decorated By:
        permission_error_decorator

        """

        if(os.path.exists(file_path) == False):
            logging.debug(file_path + " was created due to lack of the file")
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

        Decorated By:
        permission_error_decorator

        """

        did_overwrite = False

        if(os.path.exists(file_path) == False or os.path.getsize(file_path) == 0):
            logging.debug(file_path + " was created due to lack of the file or because it is blank")
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
        omit (bool | optional | default=True) : whether or not to omit the content from the log.

        Decorated By:
        permission_error_decorator

        """

        with open(file_path, "w+", encoding="utf-8") as file:
            file.write(content_to_write)

        if(omit):
            content_to_write = "(Content was omitted)"
        
        logging.debug(file_path + " was overwritten with the following content: " + content_to_write)

##--------------------start-of-clear_file()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    @permission_error_decorator()
    def clear_file(file_path:str) -> None:

        """

        Clears a file, as well as logs what occurred.

        Parameters:
        file_path (str) : path to the file to be cleared.

        Decorated By:
        permission_error_decorator

        """

        with open(file_path, "w+", encoding="utf-8") as file:
            file.truncate()

        logging.debug(file_path + " was cleared")

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

        Decorated By:
        permission_error_decorator

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

        Decorated By:
        permission_error_decorator

        """

        traceback_msg = traceback.format_exc()

        logging.error(f"Kudasai has crashed "
        f"Please send the following to the developer on github at https://github.com/Bikatr7/Kudasai/issues :"
        f"{traceback_msg}")

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

        Decorated By:
        permission_error_decorator

        """

        if(FileEnsurer.is_hugging_space()):
            return

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

        Decorated By:
        permission_error_decorator

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

        Decorated By:
        permission_error_decorator

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

        list_of_result_tuples = [('kairyou_preprocessed_text', text_to_preprocess),
                     ('kairyou_preprocessing_log', preprocessing_log),
                     ('kairyou_error_log', error_log),
                     ('debug_log', FileEnsurer.standard_read_file(FileEnsurer.debug_log_path))]

        FileEnsurer.archive_results(list_of_result_tuples,
                        module='kairyou', 
                        timestamp=timestamp)

