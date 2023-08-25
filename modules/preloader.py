## built-in libraries
import os

## custom modules
from models.Kairyou import Kairyou
from models.Kaiseki import Kaiseki
from models.Kijiku import Kijiku

from modules.fileHandler import fileHandler
from modules.toolkit import toolkit

##-------------------start-of-preloader---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class preloader:

    """

    Preloader is the program that runs before Kudasai.py & Gui.py get started in full swing.\n
    
    """

##-------------------start-of-__init__()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self) -> None: 

        """
        
        Constructor for the preloader class.\n

        Parameters:\n
        None.\n

        Returns:\n
        None.\n

        """

        self.file_handler = fileHandler()

        self.toolkit = toolkit()

        self.preprocessed_text_path = os.path.join(self.file_handler.output_dir, "preprocessedText.txt") ## path for the preprocessed text
        self.translated_text_path = os.path.join(self.file_handler.output_dir, "translatedText.txt") ## path for translated text

        self.je_check_path = os.path.join(self.file_handler.output_dir, "jeCheck.txt") ## path for je check text (text generated by the translation modules to compare against the translated text)

        self.kairyou_log_path = os.path.join(self.file_handler.output_dir, "Kairyou Results.txt")  ## path for kairyou log (the results of preprocessing)
        self.error_log_path = os.path.join(self.file_handler.output_dir, "error log.txt") ## path for the error log (errors generated by the preprocessing and translation modules)
        self.debug_log_path = os.path.join(self.file_handler.output_dir, "debug log.txt") ## path for debug log (text generated by the translation modules to help with debugging)

        self.setup_needed_files()

##-------------------start-of-setup_needed_files()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def setup_needed_files(self) -> None:

        """

        spits out output file paths and creates the required directories for them\n
        
        Parameters:\n
        self (object - Kudasai) : the Kudasai object.\n

        Returns:\n
        None\n

        """

        ## creates the output directory and config directory if they don't exist
        self.file_handler.standard_create_directory(self.file_handler.config_dir)
        self.file_handler.standard_create_directory(self.file_handler.output_dir)

        ## creates and clears the log file
        self.file_handler.logger.clear_log_file()

        ## creates the remaining 5 output files
        self.file_handler.standard_create_file(self.preprocessed_text_path)
        self.file_handler.standard_create_file(self.translated_text_path)
        self.file_handler.standard_create_file(self.je_check_path)
        self.file_handler.standard_create_file(self.kairyou_log_path)
        self.file_handler.standard_create_file(self.error_log_path)


##-------------------start-of-write_kaiseki_results()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def write_kaiseki_results(self, kaiseki_client:Kaiseki) -> None:

        """

        This function is called to write the results of the Kaiseki translation module to the output directory.\n

        Parameters:\n
        self (object - preloader) : the preloader object.\n
        kaiseki_client (object - Kaiseki) : the Kaiseki object.\n

        Returns:\n
        None.\n

        """

        ## ensures the output directory exists, cause it could get moved or fucked with.
        self.file_handler.standard_create_directory(self.file_handler.output_dir)

        with open(self.error_log_path, 'a+', encoding='utf-8') as file:
            file.writelines(kaiseki_client.error_text) ## type: ignore (we know it's not None)

        with open(self.je_check_path, 'w', encoding='utf-8') as file:
            file.writelines(kaiseki_client.je_check_text) ## type: ignore (we know it's not None)

        with open(self.translated_text_path, 'w', encoding='utf-8') as file:
            file.writelines(kaiseki_client.translated_text) ## type: ignore (we know it's not None)

        ## pushes the tl debug log to the file
        self.file_handler.logger.clear_log_file()
        self.file_handler.logger.push_batch()

##-------------------start-of-write_kijiku_results()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def write_kijiku_results(self, kijiku_client:Kijiku) -> None:

        """
        
        This function is called to write the results of the Kijiku translation module to the output directory.\n

        Parameters:\n
        self (object - preloader) : the preloader object.\n
        kijiku_client (object - Kijiku) : the Kijiku object.\n

        Returns:\n
        None.\n

        """

        ## ensures the output directory exists, cause it could get moved or fucked with.
        self.file_handler.standard_create_directory(self.file_handler.output_dir)

        with open(self.error_log_path, 'a+', encoding='utf-8') as file:
            file.writelines(kijiku_client.error_text) ## type: ignore (we know it's not None)

        with open(self.je_check_path, 'w', encoding='utf-8') as file:
            file.writelines(kijiku_client.je_check_text) ## type: ignore (we know it's not None)

        with open(self.translated_text_path, 'w', encoding='utf-8') as file:
            file.writelines(kijiku_client.translated_text) ## type: ignore (we know it's not None)

        ## pushes the tl debug log to the file
        self.file_handler.logger.clear_log_file()
        self.file_handler.logger.push_batch()

##-------------------start-of-write_kairyou_results()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def write_kairyou_results(self, kairyou_client:Kairyou) -> None:

        """
        
        This function is called to write the results of the preprocessing module to the output directory.\n

        Parameters:\n
        self (object - preloader) : the preloader object.\n

        Returns:\n
        None.\n

        """

        ## ensures the output directory exists, cause it could get moved or fucked with.
        self.file_handler.standard_create_directory(self.file_handler.output_dir)

        with(open(self.preprocessed_text_path, 'w', encoding='utf-8')) as file:
            file.write(kairyou_client.text_to_preprocess) ## type: ignore (we know it's not None)

        with open(self.kairyou_log_path, 'w', encoding='utf-8') as file:
            file.write(kairyou_client.preprocessing_log) ## type: ignore (we know it's not None)

        with open(self.error_log_path, 'w', encoding='utf-8') as file:
            file.write(kairyou_client.error_log) ## type: ignore (we know it's not None)

        with open(self.je_check_path, 'w', encoding='utf-8') as file:
            file.truncate()

        with open(self.translated_text_path, 'w', encoding='utf-8') as file:
            file.truncate()

        ## pushes the tl debug log to the file
        self.file_handler.logger.clear_log_file()
        self.file_handler.logger.push_batch()