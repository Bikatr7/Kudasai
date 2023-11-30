## built-in libraries
import enum
import itertools
import typing
import time

## third-party libraries
import spacy

## custom modules
from modules.toolkit import Toolkit
from modules.file_ensurer import FileEnsurer
from modules.logger import Logger

from handlers.katakana_handler import KatakanaHandler



##-------------------start-of-Name---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Name(typing.NamedTuple):

    """

    Represents a Japanese name along with its equivalent english name.
    The Name class extends the NamedTuple class, allowing for the creation of a tuple with named fields.

    """

    jap : str
    eng : str

##-------------------start-of-ReplacementType---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class ReplacementType(enum.Flag):

    """

    Represents name markers for different types of names.

    The ReplacementType class extends the Flag class, allowing for the combination of name markers using bitwise operations.
    
    Name Markers:
    - NONE : No specific name marker.
    - FULL_NAME : Represents a full name, first and last name.
    - FIRST_NAME : Represents the first name only.
    - FULL_AND_FIRST : Represents both the full name and the first name separately.
    - LAST_NAME : Represents the last name only.
    - FULL_AND_LAST : Represents both the full name and the last name.
    - FIRST_AND_LAST : Represents both the first name and the last name.
    - ALL_NAMES : Represents all possible names.

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

    ## The dictionary containing the rules for preprocessing.
    replacement_json = {}

    ## The text to be preprocessed.
    text_to_preprocess = ""

    ## The log of the preprocessing, showing the replacements made.
    preprocessing_log = ""

    ## The log of the errors that occurred during preprocessing (if any).
    error_log = ""

    ## The total number of replacements made.
    total_replacements = 0
    
    ## How japanese names are separated in the japanese text
    JAPANESE_NAME_SEPARATORS = ["・", ""]

    ## will be set to false if given an invalid json file
    need_to_run = True

    ##------------------------/

    ner = spacy.load("ja_core_news_lg")

##-------------------start-of-preprocess()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def preprocess() -> None: 

        """

        Preprocesses the text to be translated.

        """

        ## If we don't need to run, don't run.
        if(not Kairyou.need_to_run):
            return

        Toolkit.clear_console()

        print("Preprocessing...")

        ## (title, json_key, is_name, replace_name, honorific_type)
        replacement_rules = [ 
            ('Punctuation', 'kutouten', False, None, None), 
            ('Unicode','unicode', False, None, None),
            ('Phrases','phrases', False, None ,None),
            ('Words','single_words', False, None, None),
            ('Enhanced Check Whitelist', 'enhanced_check_whitelist', True, ReplacementType.ALL_NAMES, ReplacementType.ALL_NAMES),
            ('Full Names', 'full_names', True, ReplacementType.ALL_NAMES, ReplacementType.ALL_NAMES),       
            ('Single Names', 'single_names', True, ReplacementType.ALL_NAMES, ReplacementType.ALL_NAMES),
            ('Name Like', 'name_like', True, ReplacementType.ALL_NAMES, ReplacementType.NONE),
        ]
    
        replaced_names = dict()
        
        time_start = time.time()

        Kairyou.replace_non_katakana(replacement_rules, replaced_names)
        Kairyou.replace_katakana(replacement_rules, replaced_names)

        time_end = time.time()

        Toolkit.clear_console()

        Kairyou.preprocessing_log += "\nTotal Replacements  : " + str(Kairyou.total_replacements)
        Kairyou.preprocessing_log += "\nTime Elapsed : " + Toolkit.get_elapsed_time(time_start, time_end)

##-------------------start-of-replace_non_katakana()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def replace_non_katakana(replacement_rules:list, replaced_names:dict) -> None:

        """
        
        Handles non-katakana replacements.

        Parameters:
        replacement_rules (list) : The rules to replace by.
        replaced_names (dict - str) : Names we have replaced.

        """

        ## for non-katakana replacements
        for rule in replacement_rules: 

            title, json_key, is_name, replace_name_param, honorific_type = rule 

            if(is_name == True): 
                
                try:
                    for eng, jap in Kairyou.replacement_json[json_key].items(): 

                        ## makes jap entries into a list if not already
                        if(isinstance(jap, list) == False):
                            jap = [jap]

                        current_name = Name(" ".join(jap), eng)

                        ## katakana is replaced at the end
                        if(KatakanaHandler.is_katakana_only(current_name.jap)):
                            continue
                        
                        Kairyou.replace_name(current_name, replace_name_param, honorific_type, replaced_names, json_key, is_potential_name=True, is_katakana=False)

                except Exception as E: 
                    Kairyou.error_log += "Issue with the following key : " + json_key + "\n"
                    Kairyou.error_log += "Error is as follows : " + str(E) 
                    continue ## Go to the next iteration of the loop

            else: 
                try:
                    for jap, eng in Kairyou.replacement_json[json_key].items(): 
                        num_replacements = Kairyou.replace_single_word(jap, eng, is_potential_name=False)

                        if(num_replacements > 0):
                            Kairyou.preprocessing_log += str(jap) + " → " + str(eng) + " : " + str(num_replacements) + "\n"


                except Exception as E: 
                    Kairyou.error_log += "Issue with the following key : " + json_key + "\n"
                    Kairyou.error_log += "Error is as follows : " + str(E) 
                    continue ## Go to the next iteration of the loop

##-------------------start-of-replace_katakana()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def replace_katakana(replacement_rules:list, replaced_names:dict) -> None:

        """
        
        Handles katakana replacements.

        Parameters:
        replacement_rules (list) : The rules to replace by.
        replaced_names (dict - str) : Names we have replaced.

        """

        katakana_entries = []

        for rule in replacement_rules: 

            title, json_key, is_name, replace_name_param, honorific_type = rule 

            if(is_name == True): 

                for eng, jap in Kairyou.replacement_json[json_key].items(): 

                    if(isinstance(jap, list) == False):
                        jap = [jap]

                    current_name = Name(" ".join(jap), eng)

                    if(KatakanaHandler.is_katakana_only(current_name.jap) and not KatakanaHandler.is_actual_word(current_name.jap)):
                        katakana_entries.append((current_name, replace_name_param, honorific_type, json_key))
            else:

                for jap, eng in Kairyou.replacement_json[json_key].items():

                    if(KatakanaHandler.is_katakana_only(jap) and not KatakanaHandler.is_actual_word(jap)):
                        katakana_entries.append((jap, eng))

        ## Sort the katakana entries by the length of Japanese phrases in descending order
        katakana_entries.sort(key=lambda entry: len(entry[0].jap if isinstance(entry[0], Name) else entry[0]), reverse=True)

        ## Replace katakana names and words
        for entry in katakana_entries:

            ## names
            if(isinstance(entry[0], Name)):

                current_name, replace_name_param, honorific_type, json_key = entry

                try:
                    Kairyou.replace_name(current_name, replace_name_param, honorific_type, replaced_names, json_key, is_potential_name=True, is_katakana=True)
                    
                except Exception as E: 
                    Kairyou.error_log += "Issue with the following key : " + json_key + "\n"
                    Kairyou.error_log += "Error is as follows : " + str(E) 
                    continue
            else:
                ## Handling non-names
                jap, eng = entry

                try:
                    num_replacements = Kairyou.replace_single_word(jap, eng, is_potential_name=False, is_katakana=True)

                    if(num_replacements > 0):
                        Kairyou.preprocessing_log += str(jap) + " → " + str(eng) + " : " + str(num_replacements) + "\n"

                except Exception as E:
                    Kairyou.error_log += "Issue with the word : " + jap + "\n"
                    Kairyou.error_log += "Error is as follows : " + str(E) 
                    continue

##-------------------start-of-yield_name_replacements()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def yield_name_replacements(Name:Name, replace_type:ReplacementType, honorific_type:ReplacementType) -> typing.Generator[tuple[str, str, bool], None, None]:

        
        """

        Generates tuples of English and Japanese names to be replaced, along with a boolean indicating whether honorifics should be kept or removed.

        Parameters:
        Name (object - Name) : represents a japanese name along with its english equivalent.
        replace_type  (object - ReplacementType) : how a name should be replaced.
        honorific_type (object - ReplacementType) : how a honorific_type should be replaced.

        Returns:
        tuple (string, string, bool) : tuple containing the japanese name, english name, and a boolean indicating whether honorifics should be kept or removed.
        
        tuple is wrapped in a generator along with two None values. No, I don't know why.

        """
        
        japanese_names = Name.jap.split(" ") 
        english_names = Name.eng.split(" ") 
        
        ## if the lengths of the names don't match, the entire Name is fucked.
        try:
        
            assert len(japanese_names) == len(english_names)

        except AssertionError as e:

            print("Name lengths do not match for : ") 
            print(Name) 
            print("\nPlease correct Name discrepancy in JSON\n")

            Toolkit.pause_console()
            
            raise e
        
        if(ReplacementType.FULL_NAME in replace_type):
            indices = range(len(japanese_names)) 
            combinations = itertools.chain(*(itertools.combinations(indices, i) for i in range(2, len(indices)+1))) ## create a chain of combinations of indices, starting with combinations of length 2 up to the length of indices
            
            for comb in combinations:  
                for separator in Kairyou.JAPANESE_NAME_SEPARATORS: 
                    yield (" ".join(map(lambda i: english_names[i], comb)), 
                        separator.join(map(lambda i: japanese_names[i], comb)), 
                        ReplacementType.FULL_NAME in honorific_type) 
        
        if(ReplacementType.FIRST_NAME in replace_type): 
            yield (english_names[0], 
                f'{japanese_names[0]}',
                ReplacementType.FIRST_NAME in honorific_type)
            
        if(ReplacementType.LAST_NAME in replace_type): 
            yield (english_names[-1],  
                f'{japanese_names[-1]}', 
                ReplacementType.LAST_NAME in honorific_type)

##-------------------start-of-replace_single_word()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def replace_single_word(word:str, replacement:str, is_potential_name:bool, is_katakana:bool=False) -> int: 

        """

        Replaces a single word in the Japanese text, with an additional check for Katakana words.

        The function is extremely picky with katakana in general.

        Parameters:
        word (string) : The word to be replaced.
        replacement (string) : The replacement for the word.
        is_katakana (bool | optional | default=false) : Indicates if the word is in Katakana.

        Returns:
        num_occurrences (int) : The number of occurrences of the word replaced.

        """
            
        num_occurrences = 0

        if(is_katakana):
            if(KatakanaHandler.is_actual_word(word)):

                ## Skip replacement if it's an actual word.
                return 0  
            
            else:

                ## Use NER to ensure we're not replacing a proper name that's not in our list of Katakana words.
                if(is_potential_name):
                    Kairyou.perform_enhanced_replace(word, replacement)

                else:
                    num_occurrences = Kairyou.text_to_preprocess.count(word)
                    if(num_occurrences > 0):
                        Kairyou.text_to_preprocess = Kairyou.text_to_preprocess.replace(word, replacement)

        else:
            num_occurrences = Kairyou.text_to_preprocess.count(word)
            if(num_occurrences > 0):
                Kairyou.text_to_preprocess = Kairyou.text_to_preprocess.replace(word, replacement)
        
        Kairyou.total_replacements += num_occurrences

        return num_occurrences
        
##-------------------start-of-replace_name()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def replace_name(Name:Name, replace_type:ReplacementType, honorific_type:ReplacementType, replaced_names:dict, json_key:str, is_potential_name:bool, is_katakana:bool) -> None:

        """

        Replaces names in the japanese text based off of tuples returned by yield_name_replacements.

        Parameters:
        Name (object - Name)  : represents a japanese name along with its english equivalent.
        replace_type  (object - ReplacementType) : how a name should be replaced.
        honorific_type (object - ReplacementType) : how a honorific should be replaced.
        replaced_names (dict - string) : a dict of replaced names and their occurrences.
        is_katakana (bool) : Indicates if the name is in Katakana.

        """

        for eng, jap, no_honor in Kairyou.yield_name_replacements(Name, replace_type, honorific_type):
            
            ## Skip the replacement if this name has already been processed.
            if(jap in replaced_names):
                continue

            replacement_data = dict()

            ## Process honorifics if necessary
            for honor, honorific_english in Kairyou.replacement_json['honorifics'].items(): 
                replacement_data[honorific_english] = Kairyou.replace_single_word(
                    f'{jap}{honor}',
                    f'{eng}-{honorific_english}',

                    ## if honorifics, don't worry about additonal checking
                    is_potential_name=False,
                    is_katakana=False,
                )

            if(is_katakana):
                if(KatakanaHandler.is_actual_word(jap)):
                    ## Skip replacement if it's an actual Katakana word.
                    continue
                else:
                    ## Perform enhanced replacement check with NER 
                    replacement_data['NA'] = Kairyou.perform_enhanced_replace(jap, eng)

            ## If the name does not have honorific and isn't a known Katakana word, or we aren't checking for Katakana
            if(no_honor):
                if(json_key == "enhanced_check_whitelist" or len(jap) == 1):
                    replacement_data['NA'] = Kairyou.perform_enhanced_replace(jap, eng)

                else:
                    replacement_data['NA'] = Kairyou.replace_single_word(jap, eng, is_potential_name, is_katakana)

            ## Sum the total replacements for this name
            total = sum(replacement_data.values())

            replaced_names[jap] = total

            ## If no replacements occurred, skip the logging
            if(total == 0): 
                continue

            ## Log the replacements
            Kairyou.preprocessing_log += f'{eng} : {total} ('
            Kairyou.preprocessing_log += ', '.join([f'{key}-{value}' for key, value in replacement_data.items() if value > 0]) + ')\n'  

##-------------------start-of-perform_enhanced_replace()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def perform_enhanced_replace(jap:str, replacement:str) -> int: 

        """

        Uses ner (Named Entity Recognition) from the spacy module to replace names that need to be more carefully replaced, such as single kanji, katakana names, or those placed in the user whitelist.

        May miss true positives, but should not replace false positives.

        Parameters:
        jap (str) : Japanese to be replaced.
        replacement (str) : the replacement for the Japanese

        Returns:
        jap_replace_count (int) : How many japanese replacements that were made.

        """

        i = 0
        jap_replace_count = 0

        jap_lines = Kairyou.text_to_preprocess.split('\n')

        while(i < len(jap_lines)):
            if(jap in jap_lines[i]):

                sentence = Kairyou.ner(jap_lines[i])

                for entity in sentence.ents:
                    if(entity.text == jap and entity.label_ == "PERSON"):
                        jap_replace_count += 1
                        jap_lines[i] = jap_lines[i][:entity.start_char] + replacement + jap_lines[i][entity.end_char:]

            i+=1

        Kairyou.text_to_preprocess = '\n'.join(jap_lines)
        Kairyou.total_replacements += jap_replace_count
        
        return jap_replace_count
    
##-------------------start-of-write_kairyou_results()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def write_kairyou_results() -> None:

        """
        
        This function is called to write the results to the output directory.

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
        Logger.push_batch()
