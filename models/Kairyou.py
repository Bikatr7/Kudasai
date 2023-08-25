## built-in libraries
import enum
import itertools
import typing
import time

## third-party libraries
import spacy

## custom modules
from modules.preloader import preloader

##-------------------start-of-Name()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Name(typing.NamedTuple):

    """

    Represents a Japanese name along with its equivalent english name.\n
    The Name class extends the NamedTuple class, allowing for the creation of a tuple with named fields.\n

    """

    jap : str
    eng : str

##-------------------start-of-ReplacementType()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class ReplacementType(enum.Flag):

    """

    Represents name markers for different types of names.\n

    The ReplacementType class extends the Flag class, allowing for the combination of name markers using bitwise operations.\n
    
    Name Markers:\n
    - NONE: No specific name marker.\n
    - FULL_NAME: Represents a full name, first and last name.\n
    - FIRST_NAME: Represents the first name only.\n
    - FULL_AND_FIRST: Represents both the full name and the first name separately.\n
    - LAST_NAME: Represents the last name only.\n
    - FULL_AND_LAST: Represents both the full name and the last name.\n
    - FIRST_AND_LAST: Represents both the first name and the last name.\n
    - ALL_NAMES: Represents all possible names.\n
    
    """

    NONE = 0 
    FULL_NAME = 1 
    FIRST_NAME = 2 
    FULL_AND_FIRST = 3 
    LAST_NAME = 4 
    FULL_AND_LAST = 5 
    FIRST_AND_LAST = 6 
    ALL_NAMES = 7 

##-------------------start-of-Kairyou---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Kairyou:

    """

    Kairyou is the preprocessor for the Kudasai program.
    
    """

##-------------------start-of-__init__()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, inc_replacement_json:dict, inc_text_to_preprocess:str, inc_preloader:preloader) -> None: 

        """
        
        Constructor for Kairyou class.\n

        Parameters:\n
        inc_replacement_json (dict - string) : the dictionary containing the rules for preprocessing.\n
        inc_text_to_preprocess (string) : the text to be preprocessed.\n
        inc_preloader (object - preloader) : the preloader object.\n

        Returns:\n
        None.\n

        """

        ## The preloader object.
        self.preloader = inc_preloader

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

##-------------------start-of-preprocess()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    def preprocess(self) -> None: 

        """

        Handles the preprocessing of the text.\n

        Parameters:\n
        self (object - Kairyou) : the Kairyou object.\n

        Returns:\n
        None.\n

        """

        self.preloader.toolkit.clear_console()

        ## (title, json_key, is_name, replace_name, honorific_type)
        replacement_rules = [ 
        ('Punctuation', 'kutouten', False, None, None), 
        ('Unicode','unicode', False, None, None),
        ('Full Names', 'full_names', True, ReplacementType.ALL_NAMES, ReplacementType.ALL_NAMES),
        ('Single Names', 'single_names', True, ReplacementType.ALL_NAMES, ReplacementType.ALL_NAMES),
        ('Name Like', 'name_like', True, ReplacementType.ALL_NAMES, ReplacementType.NONE),
        ('Phrases','phrases', False, None ,None),
        ('Words','single_words', False, None, None),
        ]
 
        replaced_names = dict()

        time_start = time.time() 

        for rule in replacement_rules: 

            title, json_key, is_name, replace_name_param, honorific_type = rule 

            if(is_name == True): 
                
                try:
                    for eng, jap in self.replacement_json[json_key].items(): 

                        if(isinstance(jap, list) == False):  ## makes jap entries into a list if not already
                            jap = [jap]

                        current_name = Name(" ".join(jap), eng)

                        self.replace_name(current_name, replace_name_param, honorific_type, replaced_names)

                except Exception as E: 
                    self.error_log += "Issue with the following key : " + json_key + "\n"
                    self.error_log += "Error is as follows : " + str(E) 
                    continue ## Go to the next iteration of the loop

            else: 
                try:
                    for jap, eng in self.replacement_json[json_key].items(): 
                        num_replacements = self.replace_single_word(jap, eng)

                        if(num_replacements > 0):

                            self.preprocessing_log += str(jap) + " → " + str(eng) + " : " + str(num_replacements) + "\n"


                except Exception as E: 
                    self.error_log += "Issue with the following key : " + json_key + "\n"
                    self.error_log += "Error is as follows : " + str(E) 
                    continue ## Go to the next iteration of the loop

        time_end = time.time()

        self.preprocessing_log += "\nTotal Replacements  : " + str(self.total_replacements)
        self.preprocessing_log += "\nTime Elapsed : " + self.preloader.toolkit.get_elapsed_time(time_start, time_end)

##-------------------start-of-replace_name()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def replace_name(self, Name:Name, replace_type:ReplacementType, honorific_type:ReplacementType, replaced_names:dict) -> None:

        """

        Replaces names in the japanese text based off of tuples returned by yield_name_replacements.\n

        Parameters:\n
        self (object - Kairyou) : the Kairyou object.\n
        Name (object - Name)  : represents a japanese name along with its english equivalent.\n
        replace_type  (object - ReplacementType) : how a name should be replaced.\n
        honorific_type (object - ReplacementType) : how a honorific should be replaced.\n
        replaced_names (dict - string) : a dict of replaced names and their occurrences.\n

        Returns:\n
        None.\n

        """

        for eng, jap, no_honor in self.yield_name_replacements(Name, replace_type, honorific_type):
            
            ## if we have already replaced the current name, bail.
            if(jap in replaced_names):
                continue

            replacement_data = dict()

            ## replaces honorifics
            for honor, honorific_english in self.replacement_json['honorifics'].items(): 
                replacement_data[honorific_english] = self.replace_single_word(
                    f'{jap}{honor}',
                    f'{eng}-{honorific_english}'
                )

            ## if name does not have honorific
            if(no_honor == True): 

                ## if name is not singular kanji.
                if(len(jap) > 1): 
                    replacement_data['NA'] = self.replace_single_word(jap, eng)

                ## if singular kanji
                elif(len(jap) == 1): 
                    replacement_data['NA'] = self.replace_single_kanji(jap, eng)
                    

            total = sum(replacement_data.values())

            replaced_names[jap] = total

            ## if no replacements happened skip display assembly.
            if(total == 0): 
                continue

            self.preprocessing_log += f'{eng} : {total} ('
            self.preprocessing_log += ', '.join([f'{key}-{value}' for key, value in replacement_data.items() if value > 0]) + ')\n'

##-------------------start-of-yield_name_replacements()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def yield_name_replacements(self, Name:Name, replace_type:ReplacementType, honorific_type:ReplacementType) -> typing.Generator[tuple[str, str, bool], None, None]:

        
        """

        Generates tuples of English and Japanese names to be replaced, along with a boolean indicating whether honorifics should be kept or removed.\n

        Parameters:\n
        self (object - Kairyou) : the Kairyou object.\n
        Name (object - Name) : represents a japanese name along with its english equivalent.\n
        replace_type  (object - ReplacementType) : how a name should be replaced.\n
        honorific_type (object - ReplacementType) : how a honorific_type should be replaced.\n

        Returns:\n
        tuple (string, string, bool) : tuple containing the japanese name, english name, and a boolean indicating whether honorifics should be kept or removed.\n
        
        tuple is wrapped in a generator along with two None values. No, I don't know why.\n

        """
        
        japanese_names = Name.jap.split(" ") 
        english_names = Name.eng.split(" ") 
        
        ## if the lengths of the names don't match, the entire thing is fucked.
        try:

            assert len(japanese_names) == len(english_names)

        except AssertionError as e:

            print("Name lengths do not match for : ") 
            print(Name) 
            print("\nPlease correct Name discrepancy in JSON\n")

            self.preloader.toolkit.pause_console()
            
            raise e
        
        if(ReplacementType.FULL_NAME in replace_type):
            indices = range(len(japanese_names)) 
            combinations = itertools.chain(*(itertools.combinations(indices, i) for i in range(2, len(indices)+1))) ## create a chain of combinations of indices, starting with combinations of length 2 up to the length of indices
            
            for comb in combinations:  
                for separator in self.JAPANESE_NAME_SEPARATORS: 
                    yield (" ".join(map(lambda i: english_names[i], comb)), 
                        separator.join(map(lambda i: japanese_names[i], comb)), 
                        ReplacementType.FULL_NAME in honorific_type) 
        
        if(ReplacementType.FIRST_NAME in replace_type): 
            yield (english_names[0], 
                f'{japanese_names[0]}',
                ReplacementType.FIRST_NAME in honorific_type) #
            
        if(ReplacementType.LAST_NAME in replace_type): 
            yield (english_names[-1],  
                f'{japanese_names[-1]}', 
                ReplacementType.LAST_NAME in honorific_type)  
            
##-------------------start-of-replace_single_word()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def replace_single_word(self, word:str, replacement:str) -> int: 

        """

        Replaces single a word in the Japanese text.\n

        Parameters:\n
        self (object - Kairyou) : the Kairyou object.\n
        word (string) : word to be replaced.\n
        replacement (string) : replacement for the word.\n

        Returns:\n
        num_occurrences (int) : number of occurrences for the word.\n

        """
            
        num_occurrences = self.text_to_preprocess.count(word) 
        
        if(num_occurrences == 0): 
            return 0 

        self.text_to_preprocess = self.text_to_preprocess.replace(word, replacement) 
        self.total_replacements += num_occurrences 

        return num_occurrences
    
##-------------------start-of-replace_single_kanji()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def replace_single_kanji(self, kanji:str, replacement:str) -> int: 

        """

        Uses ner (Named Entity Recognition) from the spacy module to replace names that are composed of a single kanji in the japanese text.\n

        May miss true positives, but should not replace false positives.\n

        Parameters:\n
        self (object - Kairyou) : the Kairyou object.\n
        kanji (str) : Japanese kanji to be replaced.\n
        replacement (str) : the replacement for kanji.\n

        Returns:\n
        kanji_count (int) : how many kanji were replaced\n

        """

        i = 0
        kanji_count = 0

        jap_lines = self.text_to_preprocess.split('\n')

        while(i < len(jap_lines)):
            if(kanji in jap_lines[i]):

                sentence = self.ner(jap_lines[i])

                for entity in sentence.ents:
                    if(entity.text == kanji and entity.label_ == "PERSON"):
                        kanji_count += 1
                        jap_lines[i] = jap_lines[i][:entity.start_char] + replacement + jap_lines[i][entity.end_char:]

            i+=1

        self.text_to_preprocess = '\n'.join(jap_lines)
        self.total_replacements += kanji_count
        
        return kanji_count
    
##-------------------start-of-reset()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def reset(self) -> None:

        """

        Resets the Kairyou object.

        Parameters:\n
        self (object - Kairyou) : the Kairyou object.\n

        Returns:\n
        None\n

        """

        self.total_replacements = 0

        self.error_log = ""

        self.preprocessing_log = ""
        
