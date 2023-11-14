## built-in libaries
import os
import traceback

## custom modules
from modules.logger import Logger

class FileEnsurer():

    """
    
    FileEnsurer is a class that is used to ensure that the required files and directories exist.

    """

    ## main dirs
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(script_dir, "KudasaiOutput")

    if(os.name == 'nt'):  ## Windows
        config_dir = os.path.join(os.environ['USERPROFILE'],"KudasaiConfig")
    else:  ## Linux
        config_dir = os.path.join(os.path.expanduser("~"), "KudasaiConfig")

    Logger.log_file_path = os.path.join(output_dir, "debug_log.txt")

    ##----------------------------------/

    ## sub dirs
    lib_dir = os.path.join(script_dir, "lib")

    sudachi_lib = os.path.join(lib_dir, "sudachi")
    dic_lib = os.path.join(lib_dir, "dicts")

    ##----------------------------------/

    ## output files
    preprocessed_text_path = os.path.join(output_dir, "preprocessedText.txt") ## path for the preprocessed text
    translated_text_path = os.path.join(output_dir, "translatedText.txt") ## path for translated text

    je_check_path = os.path.join(output_dir, "jeCheck.txt") ## path for je check text (text generated by the translation modules to compare against the translated text)

    kairyou_log_path = os.path.join(output_dir, "Kairyou Results.txt")  ## path for kairyou log (the results of preprocessing)
    error_log_path = os.path.join(output_dir, "error log.txt") ## path for the error log (errors generated by the preprocessing and translation modules)
    debug_log_path = os.path.join(output_dir, "debug log.txt") ## path for debug log (text generated by the translation modules to help with debugging)

    ## sudachi files (not in use)
    system_zip = os.path.join(dic_lib, "system.zip")
    sudachi_config_json = os.path.join(sudachi_lib, "sudachi.json")
    sudachi_system_dic = os.path.join(dic_lib, "system.dic") 

    ## kairyou files
    katakana_words_path = os.path.join(sudachi_lib, "katakana_words.txt")

    ## kijiku rules
    external_kijiku_rules_path = os.path.join(script_dir,'Kijiku Rules.json')
    config_kijiku_rules_path = os.path.join(config_dir,'Kijiku Rules.json')

    ## api keys
    deepl_api_key_path = os.path.join(config_dir, "DeeplApiKey.txt")

##-------------------start-of-setup_needed_files()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def setup_needed_files() -> None:

        """

        Ensures that the required files and directories exist.\n

        """

        ## creates the output directory and config directory if they don't exist
        FileEnsurer.standard_create_directory(FileEnsurer.config_dir)
        FileEnsurer.standard_create_directory(FileEnsurer.output_dir)

        ## creates and clears the log file
        Logger.clear_log_file()

        ## creates the remaining 5 output files
        FileEnsurer.standard_create_file(FileEnsurer.preprocessed_text_path)
        FileEnsurer.standard_create_file(FileEnsurer.translated_text_path)
        FileEnsurer.standard_create_file(FileEnsurer.je_check_path)
        FileEnsurer.standard_create_file(FileEnsurer.kairyou_log_path)
        FileEnsurer.standard_create_file(FileEnsurer.error_log_path)

        if(not os.path.exists(FileEnsurer.katakana_words_path)):
           raise FileNotFoundError(f"Katakana words file not found at {FileEnsurer.katakana_words_path}. Can not continue, preprocess failed.")

##--------------------start-of-standard_create_directory()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
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
    def modified_create_file(file_path:str, content_to_write:str) -> None:

        """

        Creates a path if it doesn't exist or if it is blank or empty, writes to it, as well as logs what was created.

        Parameters:
        file_path (str) : path to the file to be created.
        content to write (str) : content to be written to the file.

        """

        if(os.path.exists(file_path) == False or os.path.getsize(file_path) == 0):
            Logger.log_action(file_path + " was created due to lack of the file or because it is blank")
            with open(file_path, "w+", encoding="utf-8") as file:
                file.write(content_to_write)

##--------------------start-of-standard_overwrite_file()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def standard_overwrite_file(file_path:str, content_to_write:str, omit:bool = False) -> None:

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
            content_to_write = "Content was omitted"
        
        Logger.log_action(file_path + " was overwritten with the following content: " + content_to_write)

##-------------------start-of-handle_critical_exception()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_critical_exception(critical_exception:Exception) -> None:

        """

        Handles a critical exception by logging it and then throwing it.\n

        Parameters:\n
        critical_exception (object - Exception) : the exception to be handled.\n

        """

        ## if crash, catch and log, then throw
        Logger.log_action("--------------------------------------------------------------")
        Logger.log_action("Please send the following to the developer on github:")  
        Logger.log_action("Kudasai has crashed")

        traceback_str = traceback.format_exc()
        
        Logger.log_action(traceback_str)

        Logger.push_batch()

        raise critical_exception
