## built-in libraries
import enum
import typing

## third-party libraries
import spacy

##-------------------start-of-Kairyou---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Kairyou:

    """

    Kairyou is the preprocessor for the Kudasai program.
    
    """

##-------------------start-of-__init__()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, inc_replacement_json:dict, inc_text_to_preprocess:str) -> None: 

        """
        
        Constructor for Kairyou class.\n

        Parameters:\n
        None.\n

        Returns:\n
        None.\n

        """

        ## The dictionary containing the rules for preprocessing.
        self.replacement_json = inc_replacement_json

        ## The text to be preprocessed.
        self.text_to_preprocess = inc_text_to_preprocess

        ## The log of the preprocessing, showing the replacements made.
        self.preprocessing_log = ""

        ## The log of the errors that occurred during preprocessing (if any).
        self.error_log = ""

        ## The total number of replacements made.
        self.total_replacements = 0
        
        ## How japanese names are separated in the japanese text
        self.JAPANESE_NAME_SEPARATORS = ["・", ""] 

        ## large model for japanese NER (named entity recognition)
        self.ner = spacy.load("ja_core_news_lg") 

##-------------------start-of-ReplacementType()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    class ReplacementType(enum.Flag):

        """

        Represents name markers for different types of names.

        The ReplacementType class extends the Flag class, allowing for the combination of name markers using bitwise operations.
        
        Name Markers:
        - NONE: No specific name marker.
        - FULL_NAME: Represents a full name, first and last name.
        - FIRST_NAME: Represents the first name only.
        - FULL_AND_FIRST: Represents both the full name and the first name separately.
        - LAST_NAME: Represents the last name only.
        - FULL_AND_LAST: Represents both the full name and the last name.
        - FIRST_AND_LAST: Represents both the first name and the last name.
        - ALL_NAMES: Represents all possible names.
        
        """

        NONE = 0 
        FULL_NAME = 1 
        FIRST_NAME = 2 
        FULL_AND_FIRST = 3 
        LAST_NAME = 4 
        FULL_AND_LAST = 5 
        FIRST_AND_LAST = 6 
        ALL_NAMES = 7 

##-------------------start-of-Name()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    class Name(typing.NamedTuple):

        """

        Represents a japanese name along with its equivalent english name.

        The Name class extends the NamedTuple class, allowing for the creation of a tuple with named fields.

        """

        jap : str
        eng : str