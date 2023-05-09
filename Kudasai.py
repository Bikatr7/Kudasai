import sys 
import json 
import os 
import time 
import itertools
import spacy
import requests
import ctypes

from time import sleep
from enum import Flag 
from collections import namedtuple 
from typing import Generator

from Models import Kaiseki 
from Models import Kijiku
from Util import associated_functions 

#-------------------start-of-globals---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Character = namedtuple('Character', 'japName engName') ## represents a japanese name along with equivalent english name

ner = spacy.load("ja_core_news_lg") # large model for japanese NER (named entity recognition)

SINGLE_KANJI_FILTER = True ## filters out single kanji or uses specific function to deal with it when replacing names
fromGui = False ## determines if Kudasai is being run from the GUI or not

JAPANESE_NAME_SEPARATORS = ["・", ""] ## japanese names are separated by the ・ or not at all

japaneseText = ''
replacementText = ''
errorText = []

totalReplacements = 0 

replacementJson = dict() 

#-------------------start-of-Names()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Names(Flag):  ## name markers
    NONE = 0 
    FULL_NAME = 1 
    FIRST_NAME = 2 
    FULL_AND_FIRST = 3 
    LAST_NAME = 4 
    FULL_AND_LAST = 5 
    FIRST_AND_LAST = 6 
    ALL_NAMES = 7 

#-------------------start-of-check_update()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def check_update() -> bool:

    """

    determines if Kudasai has a new latest release\n

    Parameters:\n
    None\n

    Returns:\n
    None\n

    """

    try:
    
        CURRENT_VERSION = "v1.4.4" 

        response = requests.get("https://api.github.com/repos/Seinuve/Kudasai/releases/latest")
        latestVersion = response.json()["tag_name"]

        if(latestVersion != CURRENT_VERSION):
            print("There is a new update for Kudasai (" + latestVersion + ")\nIt is recommended that you use the latest version of Kudasai\nYou can download it at https://github.com/Seinuve/Kudasai/releases/latest \n")
            associated_functions.pause_console()
            associated_functions.clear_console()

        return True

    except: ## used to determine if user lacks an internet connection or possesses another issue that would cause the automated mtl to fail

        return False 
    
#-------------------start-of-output_file_names()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def output_file_names() -> tuple[str,str,str,str,str,str,str,str]:

    """
    spits out output file paths and creates the Kudasai required directories for them\n
    
    Parameters:\n
    None\n

    Returns:\n
    preprocessPath (string) where the preprocessed text is stored\n
    outputPath (string) where the output for Kudasai is stored\n
    debugPath (string) where the debug text is stored\n
    jePath (string) where the text for the j-e checkers is stored\n
    translatedPath (string) where the text translated by Kijiku/Kaiseki is stored\n
    errorPath (string) where the errors are stored (if any)\n

    """

    scriptDir = os.path.dirname(os.path.abspath(__file__))
    outputDir = os.path.join(scriptDir, "KudasaiOutput")

    if(os.name == 'nt'):  # Windows
        configDir = os.path.join(os.environ['USERPROFILE'],"KudasaiConfig")
    else:  # Linux
        configDir = os.path.join(os.path.expanduser("~"), "KudasaiConfig")

    if(os.path.exists(outputDir) == False):
        os.mkdir(outputDir)

    if(os.path.exists(configDir) == False):
        os.mkdir(configDir)

    preprocessPath = os.path.join(outputDir, "preprocessedText.txt")
    outputPath = os.path.join(outputDir, "output.txt")
    debugPath = os.path.join(outputDir, "tlDebug.txt")
    jePath = os.path.join(outputDir, "jeCheck.txt")
    translatedPath = os.path.join(outputDir, "translatedText.txt")
    errorPath = os.path.join(outputDir, "errors.txt")
    
    return preprocessPath, outputPath, debugPath, jePath, translatedPath, errorPath,scriptDir,configDir

#-------------------start-of-replace_single_kanji()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def replace_single_kanji(kanji:str, replacement:str) -> int: 

    """

    uses ner (Named Entity Recognition) from the spacy module to replace names that are composed of a single kanji in the japanese text\n

    may miss true positives, but will not replace false positives\n

    Parameters:\n
    kanji (string) holds a japanese word to be replaced\n
    replacement (string) holds the replacement for jap\n

    Returns:\n
    kanjiCount (int) how many kanji s were replaced\n

    """

    global japaneseText, totalReplacements

    i = 0
    kanjiCount = 0

    japLines = japaneseText.split('\n')

    while(i < len(japLines)):
        if(kanji in japLines[i]):

            sentence = ner(japLines[i])

            for entity in sentence.ents:
                if(entity.text == kanji and entity.label_ == "PERSON"):
                    kanjiCount += 1
                    japLines[i] = japLines[i][:entity.start_char] + replacement + japLines[i][entity.end_char:]

        i+=1

    japaneseText = '\n'.join(japLines)
    totalReplacements += kanjiCount
    
    return kanjiCount

#-------------------start-of-replace_single_word()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def replace_single_word(word:str, replacement:str) -> int: 

    """

    replaces single words in the japanese text\n

    Parameters:\n
    word (string) word to be replaced\n
    replacement (string) replacement for the word\n

    Returns:\n
    numOccurrences (int) number of occurrences for word\n

    """
    
    global japaneseText, totalReplacements 
    
    numOccurrences = japaneseText.count(word) 
    
    if(numOccurrences == 0): 
        return 0 

    japaneseText = japaneseText.replace(word, replacement) 
    totalReplacements += numOccurrences 
    
    return numOccurrences 

#-------------------start-of-loop_names()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def loop_names(character:Character, replace:Names, honorific:Names) -> Generator[tuple[str, str, bool], None, None]:

    
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
    
    japaneseNames = character.japName.split(" ") 
    englishNames = character.engName.split(" ") 
    
    try: 
        assert len(japaneseNames) == len(englishNames)

    except AssertionError:
        print("Character lengths do not match for : ") 
        print(character) 
        print("\nPlease correct character discrepancy in JSON\n")

        associated_functions.pause_console()
        exit()
    
    if(Names.FULL_NAME in replace):
        indices = range(len(japaneseNames)) 
        combinations = itertools.chain(*(itertools.combinations(indices, i) for i in range(2, len(indices)+1))) ## create a chain of combinations of indices, starting with combinations of length 2 up to the length of indices
        
        for comb in combinations: 
            for separator in JAPANESE_NAME_SEPARATORS: 
                yield (" ".join(map(lambda i: englishNames[i], comb)), ## yield a tuple containing the following elements:
                       separator.join(map(lambda i: japaneseNames[i], comb)), ## a string created by joining the elements in comb using the map function to apply the function lambda i: englishNames[i] to each element in comb and then joining the resulting list with spaces, 
                       Names.FULL_NAME in honorific) ## a boolean indicating whether FULL_NAME is in honorific
    
    if(Names.FIRST_NAME in replace): ## if FIRST_NAME is in replace, yield a tuple containing the following elements: 
        yield (englishNames[0], ## the first element of englishNames, 
                f'{japaneseNames[0]}', ## the first element of japaneseNames,
                Names.FIRST_NAME in honorific) ## a boolean indicating whether FIRST_NAME is in honorific
        
    if(Names.LAST_NAME in replace): ## if LAST_NAME is in replace, yield a tuple containing the following elements:
        yield (englishNames[-1],  ## the last element of englishNames,
               f'{japaneseNames[-1]}', ## the last element of japaneseNames,
               Names.LAST_NAME in honorific)  ## a boolean indicating whether LAST_NAME is in honorific

#-------------------start-of-replace_name()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def replace_name(character:Character, replace:Names, noHonorific:Names, replacedNames:dict) -> None:

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
    
    for eng, jap, noHonor in loop_names(character, replace, noHonorific): ## if name already replaced, skip
        if(jap in replacedNames):
            continue

        data = dict()

        for honor, honorificEnglish in replacementJson['honorifics'].items(): ## replaces honorifics
            data[honorificEnglish] = replace_single_word(
                f'{jap}{honor}',
                f'{eng}-{honorificEnglish}'
            )

        if(noHonor == True): ## if name does not have honorific
            if(len(jap) > 1 or not SINGLE_KANJI_FILTER): ## if name is not singular kanji, or we do not care if singular kanji are replaced
                data['NA'] = replace_single_word(jap, eng)

            elif(len(jap) == 1 and SINGLE_KANJI_FILTER == True): 
                data['NA'] = replace_single_kanji(jap, eng)
                

        total = sum(data.values())

        replacedNames[jap] = total

        if(total == 0 or fromGui): ## if no replacements happened or calling from GUI, skip display
            continue


        print(f'{eng} : {total} (', end='')
        replacementText += f'{eng} : {total} ('

        print(", ".join(map(lambda x: f'{x}-{data[x]}',
                            filter(lambda x: data[x]>0, data))), end=')\n')
        
        replacementText += ', '.join([f'{key}-{value}' for key, value in data.items() if value > 0]) + ')\n'

#-------------------start-of-replace()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def replace() -> str: 

    """

    handles replacements in the japanese text\n

    Parameters:\n
    None\n

    Returns:\n
    japaneseText (string) the japanese text we are preprocessing\n

    """

    global japaneseText, replacementJson, replacementText,errorText,fromGui 

    ## (title, jsonKey, isName, replace_name, noHonorific)
    
    replacementRules = [ 
    ('Punctuation', 'kutouten', False, None, None), 
    ('Unicode','unicode',False, None, None),
    ('Phrases','phrases',False,None,None),
    ('Words','single_words',False,None,None),
    ('Full Names', 'full_names', True,Names.ALL_NAMES, Names.ALL_NAMES),
    ('Single Names', 'single_names', True, Names.ALL_NAMES, Names.ALL_NAMES),
    ('Name Like', 'name_like', True, Names.ALL_NAMES, Names.NONE),
    ]

    replacedNames = dict()

    timeStart = time.time() 

    for rule in replacementRules: 

        title, jsonKey, isName, replaceNameParam, noHonorific = rule 

        if(isName == True): 
            
            try:
                for eng, jap in replacementJson[jsonKey].items(): 

                    if(isinstance(jap, list) == False):  ## makes eng into a list if not already
                        jap = [jap]

                    char = Character(" ".join(jap), eng)

                    replace_name(char, replaceNameParam, noHonorific, replacedNames)

            except Exception as E: 
                errorText.append(str(E) + '\n')
                errorText.append("Exception with : " + jsonKey  + '\n')
                continue ## Go to the next iteration of the loop

        else: 
            try:
                for jap, eng in replacementJson[jsonKey].items(): 
                    numReplacements = replace_single_word(jap, eng)
                    if(numReplacements > 0): ## If a replacement was made
                        print(str(jap) + " → " + str(eng) + " : " + str(numReplacements))
                        replacementText += str(jap) + " → " + str(eng) + " : " + str(numReplacements) + "\n"

            except Exception as E: 
                errorText.append(str(E) + '\n')
                errorText.append("Exception with : " + jsonKey  + '\n')
                continue ## Go to the next iteration of the loop

    timeEnd = time.time()

    if(not fromGui): 

        print("\nTotal Replacements " + str(totalReplacements))
        replacementText += "\nTotal Replacements  : " + str(totalReplacements)

        print("\nTime Elapsed " + associated_functions.get_elapsed_time(timeStart, timeEnd))
        replacementText += "\nTime Elapsed : " + associated_functions.get_elapsed_time(timeStart, timeEnd)

    return japaneseText 

#-------------------start-of-determine_translation_automation()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def determine_translation_automation(preprocessPath:str, scriptDir:str, configDir:str) -> None:

    """

    determines which translation module the user wants to use and calls it\n

    Parameters:\n
    preprocessPath (string) path to where the preprocessed text was stored\n
    scriptDir (string) path to where the script is\n
    configDir (string) path to where the config is\n

    Returns:\n
    None\n

    """

    print("Please choose an auto translation model")
    print("\n1.Kaiseki - DeepL based line by line translation (Not very accurate by itself) (Free if using trial) (Good with punctuation)")
    print("\n2.Kijiku - OpenAI based batch translator (Very accurate) (Pricey) ($0.002 per 1k Tokens)\n")
    print("\n3.Exit\n")
    
    mode = input()

    if(mode == "1"):
        run_kaiseki(preprocessPath,scriptDir,configDir)
    
    elif(mode == "2"):
        run_kijiku(preprocessPath,scriptDir,configDir)

    else:
        exit()

#-------------------start-of-run_kaiseki()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def run_kaiseki(preprocessPath:str, scriptDir:str, configDir:str) -> None:

    """

    runs the kaiseki module for auto translation\n

    Parameters:\n
    preprocessPath (string) path to where the preprocessed text was stored\n
    scriptDir (string) path to where the script is\n
    configDir (string) path to where the config is\n

    Returns:\n
    None\n

    """

    associated_functions.clear_console()
    
    print("Commencing Automated Translation\n")

    sleep(2)

    translator,japaneseText = Kaiseki.initialize_translator(preprocessPath,configDir)

    Kaiseki.commence_translation(translator,japaneseText,scriptDir)

#-------------------start-of-run_kijiku()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def run_kijiku(preprocessPath:str, scriptDir:str, configDir:str) -> None:

    """

    runs the kijiku module for auto translation\n

    Parameters:\n
    preprocessPath (string) path to where the preprocessed text was stored\n
    scriptDir (string) path to where the script is\n
    configDir (string) path to where the config is\n

    Returns:\n
    None\n

    """

    hwnd = ctypes.windll.kernel32.GetConsoleWindow() ## minimize console window
    ctypes.windll.user32.ShowWindow(hwnd, 3) 

    associated_functions.clear_console()

    japaneseText,kijikuRules = Kijiku.initialize_text(preprocessPath,configDir)

    print("\nAre these settings okay? (1 for yes or 2 for no) : \n\n")

    for key, value in kijikuRules["open ai settings"].items():
        print(key + " : " + str(value))

    if(input("\n") == "1"):
        pass
    else:
        Kijiku.change_settings(kijikuRules,configDir)

    associated_functions.clear_console()

    hwnd = ctypes.windll.kernel32.GetConsoleWindow() ## maximize console window
    ctypes.windll.user32.ShowWindow(hwnd, 9)

    print("Commencing Automated Translation\n")

    sleep(2)

    Kijiku.commence_translation(japaneseText,scriptDir,configDir,fromGui=False)

#-------------------start-of-main()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def main(inputFile:str, jsonFile:str,isGui:bool) -> None:

    """

    reads the text from `inputFile`, replaces names and honorifics in the text based on the data in `jsonFile`, and writes the results to the folder "KudasaiOutput"\n

    Parameters:\n
    inputFile (string) path to the txt file we are preprocessing\n
    jsonFile (string) path to the json file whose "rules" we are following\n
    isGui (bool) whether or not the program was called from the GUI\n

    Returns:\n
    None\n

    """
    
    global japaneseText, replacementJson, totalReplacements, replacementText,errorText,fromGui 

    connection = None
    fromGui = isGui

    if(fromGui == False):
        connection = check_update()
    
    with open(inputFile, 'r', encoding='utf-8') as file: 
        japaneseText = file.read()
        
    try:

        with open(jsonFile, 'r', encoding='utf-8') as file: 
            replacementJson = json.load(file) 
    
    except:

        print("The second path you provided is either invalid, not a JSON file, or the JSON file has an error.\n")
        associated_functions.pause_console()

        exit()

    replace() 
    
    preprocessPath,outputPath,debugPath,jePath,translatedPath,errorPath,scriptDir,configDir = output_file_names()

    with open(preprocessPath, 'w+', encoding='utf-8') as file: 
        file.write(japaneseText) 

    with open(outputPath, 'w+', encoding='utf-8') as file: 
        file.write(replacementText) 

    with open(debugPath, 'w+', encoding='utf-8') as file: 
        file.truncate(0)

    with open(jePath, 'w+', encoding='utf-8') as file: 
        file.truncate(0)

    with open(translatedPath, 'w+', encoding='utf-8') as file: 
        file.truncate(0)

    with open(errorPath, 'w+', encoding='utf-8') as file: 
        file.writelines(errorText) 

    if(not fromGui):
        print("\n\nResults have been written to : " + preprocessPath)
        print("\nKudasai replacement output has been written to : " + outputPath + "\n")
        
        os.system('pause /P "Press any key to auto translate..."')
        associated_functions.clear_console()
        
        if(connection == True):
            determine_translation_automation(preprocessPath,scriptDir,configDir)

#-------------------start-of-sub_main()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

if(__name__ == '__main__'): # checks sys arguments and if less than 3 or called outside cmd prints usage statement

    if(len(sys.argv) < 3): 

        print(f'\nUsage: {sys.argv[0]} input_txt_file replacement.json\nSee README.md for more information.\n') 
        
        associated_functions.pause_console()
        exit() 

    associated_functions.clear_console() 

    os.system("title " + "Kudasai") 

    main(sys.argv[1], sys.argv[2],isGui=False) # Call main function with the first and second command line arguments as the input file and replacement JSON, respectively

