## built in modules
import os
import itertools 
import time
import enum
import typing
import sys

## third party modules
import spacy
import json

## custom modules
from Models import Kaiseki 
from Models import Kijiku
from Util import associated_functions 

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

    Represents a japanese name along with equivalent english name.

    The Name class extends the NamedTuple class, allowing for the creation of a tuple with named fields.

    """

    jap : str
    eng : str

##-------------------start-of-Kudasai()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Kudasai:

    """

    Kudasai class is the main class for the Kudasai program. It contains all the functions and variables needed to run the base preprocessor.

    """
##-------------------start-of-__init__()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, input_file:str, replacement_json:str, is_GUI:bool) -> None: # constructor for Kudasai class

        """
        
        Constructor for Kudasai class. Takes in the input file, replacement json file, and if it is being run from the GUI or not.

        Parameters:\n
        self : (object - Kudasai) the Kudasai object.\n
        input_file (str): The path to the input file to be processed.\n
        replacement_json (str): The path to the replacement json file.\n
        is_GUI (bool): Determines if Kudasai is being run from the GUI or not.\n

        Returns:\n
        None\n

        """

        ## represents a japanese name along with an equivalent english name
        self.Name = Name

        ## large model for japanese NER (named entity recognition)
        self.ner = spacy.load("ja_core_news_lg") 

        ## filters out single kanji or uses a specific function to deal with it when replacing names
        self.SINGLE_KANJI_FILTER = True 

        ## determines if the user is connected to the internet or not
        self.connection = False 

        ## determines if Kudasai is being run from the GUI or not
        self.from_GUI = is_GUI 

        ## how japanese names are separated in the japanese text
        self.JAPANESE_NAME_SEPARATORS = ["・", ""] 

        ## log for errors
        self.error_text = [] 

        ## holds the japanese text from the input file
        self.japanese_text = '' 

        ## results of the replacement process, not the japanese text, but like a log
        self.replacement_text = '' 

        ## dictionary that holds the replacement json file
        self.replacement_json = dict()

        ## total number of replacements made
        self.total_replacements = 0
    

        self.setup(input_file,replacement_json) ## calls setup function to load input file and replacement json file

##-------------------start-of-setup()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    def setup(self, input_file, replacement_json):

        """
        
        Sets up the Kudasai object, loading the input file, replacement json file.\n
        
        Parameters:\n
        self (object - Kudasai) : the Kudasai object.\n
        input_file (str): The path to the input file to be processed.\n
        replacement_json (str): The path to the replacement json file.\n

        Returns:\n
        None\n

        """

        with open(input_file, 'r', encoding='utf-8') as file: 
            self.japanese_text = file.read()
        
        try:

            with open(replacement_json, 'r', encoding='utf-8') as file: 
                self.replacement_json = json.load(file) 
    
        except:

            print("The second path you provided is either invalid, not a JSON file, or the JSON file has an error.\n")
            associated_functions.pause_console()

            exit()

##-------------------start-of-preprocess()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def preprocess(self) -> None:

        """

        Preprocesses the input file, replacing all the names and writing the results to the output files.\n

        Parameters:\n
        self (object - Kudasai) : the Kudasai object.\n

        Returns:\n
        None\n

        """

        if(not self.from_GUI):
            self.connection = associated_functions.check_update() ## checks if there is a new update for Kudasai

        self.replace_type() ## calls replace_type function to handle replacements in the japanese text

        self.setup_needed_files() ## calls output_file_names function to set up paths and make sure needed directories exist

        self.write_results() ## calls write_results function to write the results of the replacement process to the output files

##-------------------start-of-replace_type()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    def replace_type(self) -> None: 

        """

        handles replacements in the japanese text\n

        Parameters:\n
        self (object - Kudasai) : the Kudasai object.\n

        Returns:\n
        None\n

        """

        ## (title, json_key, is_name, replace_name, no_honorific)
        replacement_rules = [ 
        ('Punctuation', 'kutouten', False, None, None), 
        ('Unicode','unicode', False, None, None),
        ('Phrases','phrases', False, None ,None),
        ('Words','single_words', False, None, None),
        ('Full Names', 'full_names', True, ReplacementType.ALL_NAMES, ReplacementType.ALL_NAMES),
        ('Single Names', 'single_names', True, ReplacementType.ALL_NAMES, ReplacementType.ALL_NAMES),
        ('Name Like', 'name_like', True, ReplacementType.ALL_NAMES, ReplacementType.NONE),
        ]
 
        replaced_names = dict()

        time_start = time.time() 

        for rule in replacement_rules: 

            title, json_key, is_name, replace_name_param, no_honorific = rule 

            if(is_name == True): 
                
                try:
                    for eng, jap in self.replacement_json[json_key].items(): 

                        if(isinstance(jap, list) == False):  ## makes jap entries into a list if not already
                            jap = [jap]

                        char = self.Name(" ".join(jap), eng)

                        self.replace_name(char, replace_name_param, no_honorific, replaced_names)

                except Exception as E: 
                    self.error_text.append(str(E) + '\n')
                    self.error_text.append("Exception with : " + json_key  + '\n')
                    continue ## Go to the next iteration of the loop

            else: 
                try:
                    for jap, eng in self.replacement_json[json_key].items(): 
                        num_replacements = self.replace_single_word(jap, eng)

                        if(num_replacements > 0):

                            self.replacement_text += str(jap) + " → " + str(eng) + " : " + str(num_replacements) + "\n"

                            if(not self.from_GUI): 
                                print(str(jap) + " → " + str(eng) + " : " + str(num_replacements))
                            

                except Exception as E: 
                    self.error_text.append(str(E) + '\n')
                    self.error_text.append("Exception with : " + json_key  + '\n')
                    continue ## Go to the next iteration of the loop

        time_end = time.time()

        self.replacement_text += "\nTotal Replacements  : " + str(self.total_replacements)
        self.replacement_text += "\nTime Elapsed : " + associated_functions.get_elapsed_time(time_start, time_end)

        if(not self.from_GUI): 

            print("\nTotal Replacements " + str(self.total_replacements))
            print("\nTime Elapsed " + associated_functions.get_elapsed_time(time_start, time_end))

#-------------------start-of-replace_name()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def replace_name(self, Name:Name, replace_type:ReplacementType, no_honorific:ReplacementType, replaced_names:dict) -> None:

        """

        replaces names in the japanese text based off of tuples returned by loop_names\n

        Parameters:\n
        self (object - Kudasai) : the Kudasai object.\n
        Name (object - Name) represents a japanese name along with its english equivalent\n
        replace_type  (object - name) how a name should be replaced\n
        no_honorific (object - name) if a name is to replaced without honorifics\n
        replaced_names (dict - string) a list of replaced names and their occurrences\n

        Returns:\n
        None\n

        """

        for eng, jap, no_honor in self.loop_names(Name, replace_type, no_honorific): ## if name already replaced, skip
            if(jap in replaced_names):
                continue

            replacement_data = dict()

            for honor, honorific_english in self.replacement_json['honorifics'].items(): ## replaces honorifics
                replacement_data[honorific_english] = self.replace_single_word(
                    f'{jap}{honor}',
                    f'{eng}-{honorific_english}'
                )

            if(no_honor == True): ## if name does not have honorific
                if(len(jap) > 1 or not self.SINGLE_KANJI_FILTER): ## if name is not singular kanji, or we do not care if singular kanji are replaced
                    replacement_data['NA'] = self.replace_single_word(jap, eng)

                elif(len(jap) == 1 and self.SINGLE_KANJI_FILTER == True): 
                    replacement_data['NA'] = self.replace_single_kanji(jap, eng)
                    

            total = sum(replacement_data.values())

            replaced_names[jap] = total

            if(total == 0): ## if no replacements happened skip display
                continue

            self.replacement_text += f'{eng} : {total} ('
            self.replacement_text += ', '.join([f'{key}-{value}' for key, value in replacement_data.items() if value > 0]) + ')\n'

            if(not self.from_GUI):

                print(f'{eng} : {total} (', end='')
                print(", ".join(map(lambda x: f'{x}-{replacement_data[x]}',
                                    filter(lambda x: replacement_data[x]>0, replacement_data))), end=')\n')
                
#-------------------start-of-loop_names()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def loop_names(self, Name:Name, replace_type:ReplacementType, honorific:ReplacementType) -> typing.Generator[tuple[str, str, bool], None, None]:

        
        """

        generates tuples of English and Japanese names to be replaced, along with a boolean indicating whether honorifics should be kept or removed\n

        Parameters:\n
        self (object - Kudasai) : the Kudasai object.\n
        Name (object - Name) represents a japanese name along with its english equivalent\n
        replace_type  (object - name) how a name should be replaced\n
        honorific (object - name) how a honorific should be replaced\n

        Returns:\n
        tuple (string, string, bool) tuple containing the japanese name, english name, and a boolean indicating whether honorifics should be kept or removed\n
        
        tuple is wrapped in a generator along with two None values\n

        """
        
        japanese_names = Name.jap.split(" ") 
        english_names = Name.eng.split(" ") 
        
        try: 
            assert len(japanese_names) == len(english_names)

        except AssertionError:
            print("Name lengths do not match for : ") 
            print(Name) 
            print("\nPlease correct Name discrepancy in JSON\n")

            associated_functions.pause_console()
            exit()
        
        if(ReplacementType.FULL_NAME in replace_type):
            indices = range(len(japanese_names)) 
            combinations = itertools.chain(*(itertools.combinations(indices, i) for i in range(2, len(indices)+1))) ## create a chain of combinations of indices, starting with combinations of length 2 up to the length of indices
            
            for comb in combinations:  
                for separator in self.JAPANESE_NAME_SEPARATORS: 
                    yield (" ".join(map(lambda i: english_names[i], comb)), ## yield a tuple containing the following elements:
                        separator.join(map(lambda i: japanese_names[i], comb)), ## a string created by joining the elements in comb using the map function to apply the function lambda i: english_names[i] to each element in comb and then joining the resulting list with spaces, 
                        ReplacementType.FULL_NAME in honorific) ## a boolean indicating whether FULL_NAME is in honorific
        
        if(ReplacementType.FIRST_NAME in replace_type): ## if FIRST_NAME is in replace_type, yield a tuple containing the following elements: 
            yield (english_names[0], ## the first element of english_names, 
                    f'{japanese_names[0]}', ## the first element of japanese_names,
                    ReplacementType.FIRST_NAME in honorific) ## a boolean indicating whether FIRST_NAME is in honorific
            
        if(ReplacementType.LAST_NAME in replace_type): ## if LAST_NAME is in replace_type, yield a tuple containing the following elements:
            yield (english_names[-1],  ## the last element of english_names,
                f'{japanese_names[-1]}', ## the last element of japanese_names,
                ReplacementType.LAST_NAME in honorific)  ## a boolean indicating whether LAST_NAME is in honorific
          
#-------------------start-of-replace_single_word()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def replace_single_word(self, word:str, replacement:str) -> int: 

        """

        replaces single words in the japanese text\n

        Parameters:\n
        self (object - Kudasai) : the Kudasai object.\n
        word (string) word to be replaced\n
        replacement (string) replacement for the word\n

        Returns:\n
        num_occurrences (int) number of occurrences for word\n

        """
            
        num_occurrences = self.japanese_text.count(word) 
        
        if(num_occurrences == 0): 
            return 0 

        self.japanese_text = self.japanese_text.replace(word, replacement) 
        self.total_replacements += num_occurrences 

        return num_occurrences
    
#-------------------start-of-replace_single_kanji()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def replace_single_kanji(self, kanji:str, replacement:str) -> int: 

        """

        uses ner (Named Entity Recognition) from the spacy module to replace_type names that are composed of a single kanji in the japanese text\n

        may miss true positives, but should not replace_type false positives\n

        Parameters:\n
        self (object - Kudasai) : the Kudasai object.\n
        kanji (string) japanese kanji to be replaced\n
        replacement (string) the replacement for kanji\n

        Returns:\n
        kanji_count (int) how many kanji were replaced\n

        """

        i = 0
        kanji_count = 0

        jap_lines = self.japanese_text.split('\n')

        while(i < len(jap_lines)):
            if(kanji in jap_lines[i]):

                sentence = self.ner(jap_lines[i])

                for entity in sentence.ents:
                    if(entity.text == kanji and entity.label_ == "PERSON"):
                        kanji_count += 1
                        jap_lines[i] = jap_lines[i][:entity.start_char] + replacement + jap_lines[i][entity.end_char:]

            i+=1

        self.japanese_text = '\n'.join(jap_lines)
        self.total_replacements += kanji_count
        
        return kanji_count
    
##-------------------start-of-setup_needed_files---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def setup_needed_files(self) -> None:

        """
        spits out output file paths and creates the Kudasai required directories for them\n
        
        Parameters:\n
        self (object - Kudasai) : the Kudasai object.\n

        Returns:\n
        None\n

        """

        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, "KudasaiOutput")

        if(os.name == 'nt'):  # Windows
            config_dir = os.path.join(os.environ['USERPROFILE'],"KudasaiConfig")
        else:  # Linux
            config_dir = os.path.join(os.path.expanduser("~"), "KudasaiConfig")

        if(not os.path.exists(output_dir)):
            os.mkdir(output_dir)

        if(not os.path.exists(config_dir)):
            os.mkdir(config_dir)

        self.preprocess_path = os.path.join(output_dir, "preprocessedText.txt") # path for preprocessed text
        self.output_path = os.path.join(output_dir, "output.txt")  # path for Kudasai output
        self.debug_path = os.path.join(output_dir, "tlDebug.txt") # path for tl debug text (mostly for developers)
        self.je_path = os.path.join(output_dir, "jeCheck.txt") # path for je check text
        self.translated_path = os.path.join(output_dir, "translatedText.txt") # path for translated text
        self.error_path = os.path.join(output_dir, "errors.txt") # path for errors

##-------------------start-of-write_results()-------------------------------------------------------------------------------------------------------------------------------------
        
    def write_results(self) -> None: 

        """
        writes the results of Kudasai to the output files\n

        Parameters:\n
        self (object - Kudasai) : the Kudasai object.\n

        Returns:\n
        None\n

        """

        with open(self.preprocess_path, 'w+', encoding='utf-8') as file: 
            file.write(self.japanese_text) 

        with open(self.output_path, 'w+', encoding='utf-8') as file:
            file.write(self.replacement_text) 

        if(not os.path.exists(self.debug_path)):
            with open(self.debug_path, 'w+', encoding='utf-8') as file:
                pass

        if(not os.path.exists(self.je_path)):
            with open(self.je_path, 'w+', encoding='utf-8') as file:
                pass

        if(not os.path.exists(self.translated_path)):
            with open(self.translated_path, 'w+', encoding='utf-8') as file:
                pass

        with open(self.error_path, 'w+', encoding='utf-8') as file: 
            file.writelines(self.error_text) 


##-------------------start-of-main()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

if(__name__ == '__main__'): # checks sys arguments and if less than 3 or called outside cmd prints usage statement

    if(len(sys.argv) < 3): 

        print(f'\nUsage: {sys.argv[0]} input_txt_file replacement.json\nSee README.md for more information.\n') 
        
        associated_functions.pause_console()
        exit() 

    associated_functions.clear_console() 

    os.system("title " + "Kudasai") 

    client = Kudasai(sys.argv[1], sys.argv[2], is_GUI=False) # creates Kudasai object, passing in input file and replacement json file, and if it is being run from the GUI or not

    Kudasai.preprocess(client) # preprocesses the text