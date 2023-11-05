## built-in libraries
from __future__ import annotations ## used for cheating the circular import issue that occurs when i need to type check some things

import typing

## custom modules
if(typing.TYPE_CHECKING): ## used for cheating the circular import issue that occurs when i need to type check some things
    from models.Kairyou import Name


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

        Loads the katakana library file into memory.\n
        
        Parameters:\n
        self (object - katakanaHandler) : the katakanaHandler object.\n
        katakana_lib_file (str) : path to the katakana library file.\n

        Returns:\n
        None.\n

        """

        self.katakana_words = []

        with open(katakana_lib_file, "r", encoding="utf-8") as file:
            for line in file:
                self.katakana_words.append(line.strip())

##--------------------start-of-is_katakana_only()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def is_katakana_only(self, word:str) -> bool:

        """

        Checks if the word is only katakana.\n
        
        Parameters:\n
        self (object - katakanaHandler) : the katakanaHandler object.\n
        word (str) : the word to check.\n

        Returns:\n
        bool : True if the word is only katakana, False otherwise.\n

        """

        return all('ァ' <= char <= 'ヴ' or char == 'ー' for char in word)

##--------------------start-of-get_katakana_entities()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def get_katakana_entities(self, names:dict) -> typing.List[Name]:

        """

        Gets the katakana entities from the names dictionary.\n

        Parameters:\n
        self (object - katakanaHandler) : the katakanaHandler object.\n

        Returns:\n
        list : a list of Name objects.\n

        """

        return [Name(jap=j, eng=e) for e, j in names.items() if self.is_katakana_only(j)]
    
##--------------------start-of-is_actual_word()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def is_actual_word(self, jap:str) -> bool:

        """
        

        Checks if the given jap is an actual katakana word.\n

        Parameters:\n
        self (object - katakanaHandler) : the katakanaHandler object

        Returns:
        bool : True if the word is an actual katakana word, False otherwise.\n

        """

        if(jap in self.katakana_words):
            return True
        
        else:
            return False