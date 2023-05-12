import os

from spacy import load as spacy_load
from json import  load as json_load

from itertools import chain, combinations as combinator
from time import time
from enum import Flag 
from typing import Generator, NamedTuple
from sys import argv

from Models import Kaiseki 
from Models import Kijiku
from Util import associated_functions 

##-------------------start-of-ReplacementType()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class ReplacementType(Flag): ## ex

    """
    Represents name markers for different types of names.

    The ReplacementType class extends the Flag class, allowing for the combination of name markers using bitwise operations.
    
    Name Markers:
    - NONE: No specific name marker.
    - FULL_NAME: Represents a full name, consisting of both the first name and last name.
    - FIRST_NAME: Represents the first name only.
    - FULL_AND_FIRST: Represents both the full name and the first name.
    - LAST_NAME: Represents the last name only.
    - FULL_AND_LAST: Represents both the full name and the last name.
    - FIRST_AND_LAST: Represents both the first name and the last name.
    - ALL_NAMES: Represents all possible names (full name, first name, and last name).
    
    """

    NONE = 0 
    FULL_NAME = 1 
    FIRST_NAME = 2 
    FULL_AND_FIRST = 3 
    LAST_NAME = 4 
    FULL_AND_LAST = 5 
    FIRST_AND_LAST = 6 
    ALL_NAMES = 7 

##-------------------start-of-Character()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Character(NamedTuple):

    """

    Represents a japanese name along with equivalent english name.

    """

    jap : str
    eng : str

##-------------------start-of-Kudasai()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Kudasai:

    """

    Kudasai class is the main class for the Kudasai program. It contains all the functions and variables needed to run the base preprocessor.

    """
##-------------------start-of-__init__()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, inputFile:str, replacementJson:str, isGui:bool) -> None: # constructor for Kudasai class

        """
        
        Constructor for Kudasai class. Takes in the input file, replacement json file, and if it is being run from the GUI or not.

        Parameters:\n
        self : (object - Kudasai) the Kudasai object.\n
        inputFile (str): The path to the input file to be processed.\n
        replacementJson (str): The path to the replacement json file.\n
        isGui (bool): Determines if Kudasai is being run from the GUI or not.\n

        Returns:\n
        None\n

        """

        self.character = Character ## represents a japanese name along with an equivalent english name

        self.ner = spacy_load("ja_core_news_lg") ## large model for japanese NER (named entity recognition)

        self.SINGLE_KANJI_FILTER = True ## filters out single kanji or uses a specific function to deal with it when replacing names
        self.connection = False ## determines if the user is connected to the internet or not
        self.fromGui = isGui ## determines if Kudasai is being run from the GUI or not

        self.JAPANESE_NAME_SEPARATORS = ["・", ""] ## how japanese names are separated in the japanese text
        self.errorText = [] ## log for errors

        self.japaneseText = '' ## holds the japanese text from the input file
        self.replacementText = '' ## results of the replacement process, not the japanese text, but like a log

        self.totalReplacements = 0
    
        self.replacementJson = dict() ## dictionary that holds the replacement json file

        self.setup(inputFile,replacementJson) ## calls setup function to load input file and replacement json file

##-------------------start-of-setup()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    def setup(self,inputFile,replacementJson):

        """
        
        Sets up the Kudasai object, loading the input file, replacement json file.\n
        
        Parameters:\n
        inputFile (str): The path to the input file to be processed.\n
        replacementJson (str): The path to the replacement json file.\n

        Returns:\n
        None\n

        """

        with open(inputFile, 'r', encoding='utf-8') as file: 
            self.japaneseText = file.read()
        
        try:

            with open(replacementJson, 'r', encoding='utf-8') as file: 
                self.replacementJson = json_load(file) 
    
        except:

            print("The second path you provided is either invalid, not a JSON file, or the JSON file has an error.\n")
            associated_functions.pause_console()

            exit()


##-------------------start-of-preprocess()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def preprocess(self) -> None:

        if(not self.fromGui):
            self.connection = associated_functions.check_update() ## checks if there is a new update for Kudasai

        self.replace() ## calls replace function to handle replacements in the japanese text

        self.setup_needed_files() ## calls output_file_names function to set up paths and make sure needed directories exist

        self.write_results() ## calls write_results function to write the results of the replacement process to the output files


##-------------------start-of-replace()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    def replace(self) -> None: 

        """

        handles replacements in the japanese text\n

        Parameters:\n
        None\n

        Returns:\n
        None\n

        """

        ## (title, jsonKey, isName, replace_name, noHonorific)
        
        replacementRules = [ 
        ('Punctuation', 'kutouten', False, None, None), 
        ('Unicode','unicode',False, None, None),
        ('Phrases','phrases',False,None,None),
        ('Words','single_words',False,None,None),
        ('Full Names', 'full_names', True,ReplacementType.ALL_NAMES, ReplacementType.ALL_NAMES),
        ('Single Names', 'single_names', True, ReplacementType.ALL_NAMES, ReplacementType.ALL_NAMES),
        ('Name Like', 'name_like', True, ReplacementType.ALL_NAMES, ReplacementType.NONE),
        ]

        replacedNames = dict()

        timeStart = time() 

        for rule in replacementRules: 

            title, jsonKey, isName, replaceNameParam, noHonorific = rule 

            if(isName == True): 
                
                try:
                    for eng, jap in self.replacementJson[jsonKey].items(): 

                        if(isinstance(jap, list) == False):  ## makes jap entries into a list if not already
                            jap = [jap]

                        char = self.character(" ".join(jap), eng)

                        self.replace_name(char, replaceNameParam, noHonorific, replacedNames)

                except Exception as E: 
                    self.errorText.append(str(E) + '\n')
                    self.errorText.append("Exception with : " + jsonKey  + '\n')
                    continue ## Go to the next iteration of the loop

            else: 
                try:
                    for jap, eng in self.replacementJson[jsonKey].items(): 
                        numReplacements = self.replace_single_word(jap, eng)

                        if(numReplacements > 0):

                            self.replacementText += str(jap) + " → " + str(eng) + " : " + str(numReplacements) + "\n"

                            if(not self.fromGui): 
                                print(str(jap) + " → " + str(eng) + " : " + str(numReplacements))
                            

                except Exception as E: 
                    self.errorText.append(str(E) + '\n')
                    self.errorText.append("Exception with : " + jsonKey  + '\n')
                    continue ## Go to the next iteration of the loop

        timeEnd = time()

        self.replacementText += "\nTotal Replacements  : " + str(self.totalReplacements)
        self.replacementText += "\nTime Elapsed : " + associated_functions.get_elapsed_time(timeStart, timeEnd)

        if(not self.fromGui): 

            print("\nTotal Replacements " + str(self.totalReplacements))
            print("\nTime Elapsed " + associated_functions.get_elapsed_time(timeStart, timeEnd))

#-------------------start-of-replace_name()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def replace_name(self,character:Character, replace:ReplacementType, noHonorific:ReplacementType, replacedNames:dict) -> None:

        """

        replaces names in the japanese text based off of tuples returned by loop_names\n

        Parameters:\n
        character (object - Character) represents a japanese name along with its english equivalent\n
        replace  (object - name) how a name should be replaced\n
        noHonorific (object - name) if a name is to replaced without honorifics\n
        replacedNames (dict - string) a list of replaced names and their occurrences\n

        Returns:\n
        None\n

        """

        global replacementText,fromGui 
        
        for eng, jap, noHonor in self.loop_names(character, replace, noHonorific): ## if name already replaced, skip
            if(jap in replacedNames):
                continue

            data = dict()

            for honor, honorificEnglish in self.replacementJson['honorifics'].items(): ## replaces honorifics
                data[honorificEnglish] = self.replace_single_word(
                    f'{jap}{honor}',
                    f'{eng}-{honorificEnglish}'
                )

            if(noHonor == True): ## if name does not have honorific
                if(len(jap) > 1 or not self.SINGLE_KANJI_FILTER): ## if name is not singular kanji, or we do not care if singular kanji are replaced
                    data['NA'] = self.replace_single_word(jap, eng)

                elif(len(jap) == 1 and self.SINGLE_KANJI_FILTER == True): 
                    data['NA'] = self.replace_single_kanji(jap, eng)
                    

            total = sum(data.values())

            replacedNames[jap] = total

            if(total == 0): ## if no replacements happened skip display
                continue

            self.replacementText += f'{eng} : {total} ('
            self.replacementText += ', '.join([f'{key}-{value}' for key, value in data.items() if value > 0]) + ')\n'

            if(not self.fromGui):

                print(f'{eng} : {total} (', end='')
                print(", ".join(map(lambda x: f'{x}-{data[x]}',
                                    filter(lambda x: data[x]>0, data))), end=')\n')
                
#-------------------start-of-loop_names()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def loop_names(self,character:Character, replace:ReplacementType, honorific:ReplacementType) -> Generator[tuple[str, str, bool], None, None]:

        
        """

        generates tuples of English and Japanese names to be replaced, along with a boolean indicating whether honorifics should be kept or removed\n

        Parameters:\n
        character (object - Character) represents a japanese name along with its english equivalent\n
        replace  (object - name) how a name should be replaced\n
        honorific (object - name) how a honorific should be replaced\n

        Returns:\n
        tuple (string, string, bool) tuple containing the japanese name, english name, and a boolean indicating whether honorifics should be kept or removed\n
        
        tuple is wrapped in a generator along with two None values\n

        """
        
        japaneseNames = character.jap.split(" ") 
        englishNames = character.eng.split(" ") 
        
        try: 
            assert len(japaneseNames) == len(englishNames)

        except AssertionError:
            print("Character lengths do not match for : ") 
            print(character) 
            print("\nPlease correct character discrepancy in JSON\n")

            associated_functions.pause_console()
            exit()
        
        if(ReplacementType.FULL_NAME in replace):
            indices = range(len(japaneseNames)) 
            combinations = chain(*(combinator(indices, i) for i in range(2, len(indices)+1))) ## create a chain of combinations of indices, starting with combinations of length 2 up to the length of indices
            
            for comb in combinations:  
                for separator in self.JAPANESE_NAME_SEPARATORS: 
                    yield (" ".join(map(lambda i: englishNames[i], comb)), ## yield a tuple containing the following elements:
                        separator.join(map(lambda i: japaneseNames[i], comb)), ## a string created by joining the elements in comb using the map function to apply the function lambda i: englishNames[i] to each element in comb and then joining the resulting list with spaces, 
                        ReplacementType.FULL_NAME in honorific) ## a boolean indicating whether FULL_NAME is in honorific
        
        if(ReplacementType.FIRST_NAME in replace): ## if FIRST_NAME is in replace, yield a tuple containing the following elements: 
            yield (englishNames[0], ## the first element of englishNames, 
                    f'{japaneseNames[0]}', ## the first element of japaneseNames,
                    ReplacementType.FIRST_NAME in honorific) ## a boolean indicating whether FIRST_NAME is in honorific
            
        if(ReplacementType.LAST_NAME in replace): ## if LAST_NAME is in replace, yield a tuple containing the following elements:
            yield (englishNames[-1],  ## the last element of englishNames,
                f'{japaneseNames[-1]}', ## the last element of japaneseNames,
                ReplacementType.LAST_NAME in honorific)  ## a boolean indicating whether LAST_NAME is in honorific
          
#-------------------start-of-replace_single_word()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def replace_single_word(self,word:str, replacement:str) -> int: 

        """

        replaces single words in the japanese text\n

        Parameters:\n
        word (string) word to be replaced\n
        replacement (string) replacement for the word\n

        Returns:\n
        numOccurrences (int) number of occurrences for word\n

        """
            
        numOccurrences = self.japaneseText.count(word) 
        
        if(numOccurrences == 0): 
            return 0 

        self.japaneseText = self.japaneseText.replace(word, replacement) 
        self.totalReplacements += numOccurrences 

        return numOccurrences
    
#-------------------start-of-replace_single_kanji()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def replace_single_kanji(self, kanji:str, replacement:str) -> int: 

        """

        uses ner (Named Entity Recognition) from the spacy module to replace names that are composed of a single kanji in the japanese text\n

        may miss true positives, but should not replace false positives\n

        Parameters:\n
        kanji (string) japanese kanji to be replaced\n
        replacement (string) the replacement for kanji\n

        Returns:\n
        kanjiCount (int) how many kanji were replaced\n

        """

        i = 0
        kanjiCount = 0

        japLines = self.japaneseText.split('\n')

        while(i < len(japLines)):
            if(kanji in japLines[i]):

                sentence = self.ner(japLines[i])

                for entity in sentence.ents:
                    if(entity.text == kanji and entity.label_ == "PERSON"):
                        kanjiCount += 1
                        japLines[i] = japLines[i][:entity.start_char] + replacement + japLines[i][entity.end_char:]

            i+=1

        self.japaneseText = '\n'.join(japLines)
        self.totalReplacements += kanjiCount
        
        return kanjiCount
    
##-------------------start-of-setup_needed_files---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def setup_needed_files(self) -> None:

        """
        spits out output file paths and creates the Kudasai required directories for them\n
        
        Parameters:\n
        None\n

        Returns:\n
        None\n

        """

        scriptDir = os.path.dirname(os.path.abspath(__file__))
        outputDir = os.path.join(scriptDir, "KudasaiOutput")

        if(os.name == 'nt'):  # Windows
            configDir = os.path.join(os.environ['USERPROFILE'],"KudasaiConfig")
        else:  # Linux
            configDir = os.path.join(os.path.expanduser("~"), "KudasaiConfig")

        if(not os.path.exists(outputDir)):
            os.mkdir(outputDir)

        if(not os.path.exists(configDir)):
            os.mkdir(configDir)

        self.preprocessPath = os.path.join(outputDir, "preprocessedText.txt") # path for preprocessed text
        self.outputPath = os.path.join(outputDir, "output.txt")  # path for Kudasai output
        self.debugPath = os.path.join(outputDir, "tlDebug.txt") # path for tl debug text (mostly for developers)
        self.jePath = os.path.join(outputDir, "jeCheck.txt") # path for je check text
        self.translatedPath = os.path.join(outputDir, "translatedText.txt") # path for translated text
        self.errorPath = os.path.join(outputDir, "errors.txt") # path for errors

##-------------------start-of-write_results()-------------------------------------------------------------------------------------------------------------------------------------
        
    def write_results(self) -> None: 

        """
        writes the results of Kudasai to the output files\n

        Parameters:\n
        None\n

        Returns:\n
        None\n

        """

        with open(self.preprocessPath, 'w+', encoding='utf-8') as file: 
            file.write(self.japaneseText) 

        with open(self.outputPath, 'w+', encoding='utf-8') as file:
            file.write(self.replacementText) 

        if(not os.path.exists(self.debugPath)):
            with open(self.debugPath, 'w+', encoding='utf-8') as file:
                pass

        if(not os.path.exists(self.jePath)):
            with open(self.jePath, 'w+', encoding='utf-8') as file:
                pass

        if(not os.path.exists(self.translatedPath)):
            with open(self.translatedPath, 'w+', encoding='utf-8') as file:
                pass

        with open(self.errorPath, 'w+', encoding='utf-8') as file: 
            file.writelines(self.errorText) 


##-------------------start-of-main()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

if(__name__ == '__main__'): # checks sys arguments and if less than 3 or called outside cmd prints usage statement

    if(len(argv) < 3): 

        print(f'\nUsage: {argv[0]} input_txt_file replacement.json\nSee README.md for more information.\n') 
        
        associated_functions.pause_console()
        exit() 

    associated_functions.clear_console() 

    os.system("title " + "Kudasai") 

    client = Kudasai(argv[1], argv[2],isGui=False) # creates Kudasai object, passing in input file and replacement json file, and if it is being run from the GUI or not

    Kudasai.preprocess(client) # preprocesses the text