class katakanaHandler:

    """
    
    Has some helper functions for dealing with katakana characters while replacing text.\n

    """
##--------------------start-of-__init__()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, katakana_lib_file:str) -> None:

        """
        
        Parameters:\n
        katakana_lib_file (str) : path to the katakana library file.\n

        Returns:\n
        None.\n

        """

        self.load_katakana_words(katakana_lib_file)

##--------------------start-of-load_katakana_words()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def load_katakana_words(self, katakana_lib_file:str) -> None:

        """
        
        Parameters:\n
        katakana_lib_file (str) : path to the katakana library file.\n

        Returns:\n
        None.\n

        """

        self.katakana_words = []

        with open(katakana_lib_file, "r", encoding="utf-8") as file:
            for line in file:
                self.katakana_words.append(line.strip())