## built-in libraries
import os

## custom modules
from models.Kairyou import Kairyou
from models.Kaiseki import Kaiseki
from models.Kijiku import Kijiku

from modules.toolkit import Toolkit
from modules.file_ensurer import FileEnsurer
from modules.logger import Logger

##-------------------start-of-preloader---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class ResultsAssembler:

    """

    ResultsAssembler is a class that is used to assemble the results of the translation modules into a single output directory.

    It is used by all versions of Kudasai.
    
    """

##-------------------start-of-write_kaiseki_results()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def write_kaiseki_results(self, kaiseki_client:Kaiseki) -> None:

        """

        This function is called to write the results of the Kaiseki translation module to the output directory.

        Parameters:
        self (object - preloader) : the preloader object.
        kaiseki_client (object - Kaiseki) : the Kaiseki object.

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
        kairyou_client (object - Kairyou) : the Kairyou object.\n

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