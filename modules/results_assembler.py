## custom modules
from models.kaiseki import Kaiseki
from models.kijiku import Kijiku
from models.kairyou import Kairyou

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

    @staticmethod
    def write_kaiseki_results() -> None:

        """

        This function is called to write the results of the Kaiseki translation module to the output directory.

        """

        ## ensures the output directory exists, cause it could get moved or fucked with.
        FileEnsurer.standard_create_directory(FileEnsurer.output_dir)

        with open(FileEnsurer.error_log_path, 'a+', encoding='utf-8') as file:
            file.writelines(Kaiseki.error_text)

        with open(FileEnsurer.je_check_path, 'w', encoding='utf-8') as file:
            file.writelines(Kaiseki.je_check_text) 

        with open(FileEnsurer.translated_text_path, 'w', encoding='utf-8') as file:
            file.writelines(Kaiseki.translated_text) 

        ## pushes the tl debug log to the file
        Logger.clear_log_file()
        Logger.push_batch()

##-------------------start-of-write_kijiku_results()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def write_kijiku_results() -> None:

        """
        
        This function is called to write the results of the Kijiku translation module to the output directory.

        """

        ## ensures the output directory exists, cause it could get moved or fucked with.
        FileEnsurer.standard_create_directory(FileEnsurer.output_dir)

        with open(FileEnsurer.error_log_path, 'a+', encoding='utf-8') as file:
            file.writelines(Kijiku.error_text)

        with open(FileEnsurer.je_check_path, 'w', encoding='utf-8') as file:
            file.writelines(Kijiku.je_check_text)

        with open(FileEnsurer.translated_text_path, 'w', encoding='utf-8') as file:
            file.writelines(Kijiku.translated_text)

        ## pushes the tl debug log to the file
        Logger.clear_log_file()
        Logger.push_batch()

##-------------------start-of-write_kairyou_results()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def write_kairyou_results() -> None:

        """
        
        This function is called to write the results of the preprocessing module to the output directory.

        """

        ## ensures the output directory exists, cause it could get moved or fucked with.
        FileEnsurer.standard_create_directory(FileEnsurer.output_dir)

        with(open(FileEnsurer.preprocessed_text_path, 'w', encoding='utf-8')) as file:
            file.write(Kairyou.text_to_preprocess) 

        with open(FileEnsurer.kairyou_log_path, 'w', encoding='utf-8') as file:
            file.write(Kairyou.preprocessing_log)

        with open(FileEnsurer.error_log_path, 'w', encoding='utf-8') as file:
            file.write(Kairyou.error_log)

        with open(FileEnsurer.je_check_path, 'w', encoding='utf-8') as file:
            file.truncate()

        with open(FileEnsurer.translated_text_path, 'w', encoding='utf-8') as file:
            file.truncate()

        ## pushes the tl debug log to the file
        Logger.clear_log_file()
        Logger.push_batch()