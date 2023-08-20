## built-in libraries
import os

## custom modules
from Modules.fileHandler import fileHandler
from Modules.toolkit import toolkit

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

        self.preprocess_path = os.path.join(self.file_handler.output_dir, "preprocessedText.txt") ## path for preprocessed text
        self.output_path = os.path.join(self.file_handler.output_dir, "output.txt")  ## path for Kudasai output
        self.je_path = os.path.join(self.file_handler.output_dir, "jeCheck.txt") ## path for je check text
        self.translated_path = os.path.join(self.file_handler.output_dir, "translatedText.txt") ## path for translated text
        self.error_path = os.path.join(self.file_handler.output_dir, "errors.txt") ## path for errors

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

        self.file_handler.standard_create_directory(self.file_handler.config_dir)
        self.file_handler.standard_create_directory(self.file_handler.output_dir)

        self.file_handler.standard_create_file(self.preprocess_path)
        self.file_handler.standard_create_file(self.output_path)
        self.file_handler.standard_create_file(self.je_path)
        self.file_handler.standard_create_file(self.translated_path)
        self.file_handler.standard_create_file(self.error_path)