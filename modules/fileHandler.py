## built-in libaries
import os
import traceback

## custom modules
from modules.logger import logger

class fileHandler():

    """
    
    The handler that handles interactions with files.\n

    """
##--------------------start-of-__init__()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self) -> None:

        """
        
        Initializes the fileHandler class.\n

        Parameters:\n
        self (object - fileHandler) : the fileHandler object.\n

        Returns:\n
        None.\n

        """

        self.script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.output_dir = os.path.join(self.script_dir, "KudasaiOutput")

        if(os.name == 'nt'):  # Windows
            self.config_dir = os.path.join(os.environ['USERPROFILE'],"KudasaiConfig")
        else:  # Linux
            self.config_dir = os.path.join(os.path.expanduser("~"), "KudasaiConfig")

        ## log file
        self.log_path = os.path.join(self.output_dir, "debug log.txt")

        self.logger = logger(self.log_path)

##--------------------start-of-standard_create_directory()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def standard_create_directory(self, directory_path:str) -> None:

        """

        Creates a directory if it doesn't exist, as well as logs what was created.\n

        Parameters:\n
        self (object - fileHandler) : the fileHandler object.\n
        directory_path (str) : path to the directory to be created.\n

        Returns:\n
        None.\n

        """

        if(os.path.isdir(directory_path) == False):
            os.mkdir(directory_path)
            self.logger.log_action(directory_path + " created due to lack of the folder")

##--------------------start-of-standard_create_file()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def standard_create_file(self, file_path:str) -> None:

        """

        Creates a file if it doesn't exist, truncates it,  as well as logs what was created.\n

        Parameters:\n
        self (object - fileHandler) : the fileHandler object.\n
        file_path (str) : path to the file to be created.\n

        Returns:\n
        None.\n

        """

        if(os.path.exists(file_path) == False):
            self.logger.log_action(file_path + " was created due to lack of the file")
            with open(file_path, "w+", encoding="utf-8") as file:
                file.truncate()

##--------------------start-of-modified_create_file()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def modified_create_file(self, file_path:str, content_to_write:str) -> None:

        """

        Creates a path if it doesn't exist or if it is blank or empty, writes to it, as well as logs what was created.\n

        Parameters:\n
        self (object - fileHandler) : the fileHandler object.\n
        file_path (str) : path to the file to be created.\n
        content to write (str) : content to be written to the file.\n

        Returns:\n
        None.\n

        """

        if(os.path.exists(file_path) == False or os.path.getsize(file_path) == 0):
            self.logger.log_action(file_path + " was created due to lack of the file or because it is blank")
            with open(file_path, "w+", encoding="utf-8") as file:
                file.write(content_to_write)

##--------------------start-of-standard_overwrite_file()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def standard_overwrite_file(self, file_path:str, content_to_write:str, omit:bool = False) -> None:

        """

        Writes to a file, creates it if it doesn't exist, overwrites it if it does, as well as logs what occurred.\n

        Parameters:\n
        self (object - fileHandler) : the fileHandler object.\n
        file_path (str) : path to the file to be overwritten.\n
        content to write (str) : content to be written to the file.\n

        Returns:\n
        None.\n

        """

        with open(file_path, "w+", encoding="utf-8") as file:
            file.write(content_to_write)

        if(omit):
            content_to_write = "omitted"
        
        self.logger.log_action(file_path + " was overwritten with the following content: " + content_to_write)

##-------------------start-of-handle_critical_exception()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def handle_critical_exception(self, critical_exception:Exception) -> None:

        """

        Handles a critical exception by logging it and then throwing it.\n

        Parameters:\n
        self (object - fileHandler) : the fileHandler object.\n
        critical_exception (object - Exception) : the exception to be handled.\n

        Returns:\n
        None.\n

        """

        ## if crash, catch and log, then throw
        self.logger.log_action("--------------------------------------------------------------")
        self.logger.log_action("Kudasai has crashed")

        traceback_str = traceback.format_exc()
        
        self.logger.log_action(traceback_str)

        self.logger.push_batch()

        raise critical_exception
