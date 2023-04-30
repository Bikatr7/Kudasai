"""
Kudasai.py

Original Author: thevoidzero#4686
Refactored and Maintained by: Seinu#7854
Contributions by: SnOrT NeSqUiK™#9775

Windows only.

Python Version: 3.7.6-3.11.2

Used to make Classroom of the Elite translation easier by preprocessing the Japanese text (optional auto translation using deepL/openai API).

Derived from https://github.com/Atreyagaurav/mtl-related-scripts

---------------------------------------------------------------------------------------------------------------------------------------------------

Run the pip commands listed in requirements.txt before running Kudasai.

Please note that issues can occur when trying to install these dependencies:

python -m spacy download ja_core_news_lg
python -m spacy download en_core_web_lg

if these do not work, either reinstall spacy or try:

pip install en_core_web_lg
pip install ja_core_news_lg

---------------------------------------------------------------------------------------------------------------------------------------------------

CmdLineArgs

Argument 1: Path to a .txt file that needs to be preprocessed
Argument 2: Path to JSON Criteria

Note:
For the json it has to be a specific format, you can see several examples in the 'Replacements' Folder or an outline below

{
  "honorifics": {
    "さん": "san",
    "くん": "kun"
  },

  "single_words": {
    "β": "Beta"
  },

  "unicode": {
    "\u3000": " "
  },

  "phrases": {
    "ケヤキモール" : "Keyaki Mall",
    "高育" : "ANHS"
  },

  "kutouten": {
    "「": "\"",
    "」": "\"",
    "『": "'",
    "』": "'",
    "、": ","
  },

  "name_like": {
    "お兄": "Onii",
  },

  "single_names": {
    "Kijima": "鬼島",
    "king": "Wan-sama"

  },

  "full_names": {
    "Amasawa Ichika": ["天沢","一夏"]
  }

}

---------------------------------------------------------------------------------------------------------------------------------------------------

Output: 

KudasaiOutput (folder created where this script (Kudasai.py) is located)

KudasaiOutput contains:

jeCheck.txt (a txt file for j-e checkers to cross-check sentences that were translated by deepL)
output.txt (a txt file containing Kudasai's output, basically what Kudasai replaced)
preprocessedText.txt (a txt file containing the results of Kudasai's preprocessing)
tlDebug.txt (a txt file containing debug material for the developer)
translatedText.txt (a txt file containing the results of your chosen auto translation module)
errorText.txt (a txt file containing the errors that occurred during auto translation (if any))

---------------------------------------------------------------------------------------------------------------------------------------------------

To use

Step 1: Open CMD
Step 2: Copy the path of Kudasai.py to cmd and type a space.
Step 3: Copy the path of .txt file you want to preprocess to cmd and type a space
Step 4: Copy the path of replacements.json to CMD
Step 5: Press enter
Step 6: Follow internal instructions to use auto-translation

Any questions or bugs, please email Seinuve@gmail.com

---------------------------------------------------------------------------------------------------------------------------------------------------

Security:

api keys are stored locally in ProgramData and are obfuscated.

---------------------------------------------------------------------------------------------------------------------------------------------------

Util:

Util folder has a script called Token Counter.py that lets you estimated the number of tokens/cost in a file/string

---------------------------------------------------------------------------------------------------------------------------------------------------

"""


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

from Models import Kaiseki 
from Models import Kijiku

#-------------------start-of-globals---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Character = namedtuple('Character', 'japName engName')

ner = spacy.load("ja_core_news_lg") # large model for japanese NER (named entity recognition)

VERBOSE = True ## lowkey forgot what this does
SINGLE_KANJI_FILTER = True ## filters out single kanji or uses specific function to deal with it when replacing names

JAPANESE_NAME_SEPARATORS = ["・", ""] ## japanese names are separated by the　・ or not at all

japaneseText = ''
replacementText = ''

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

def check_update():

    """

    determines if Kudasai has a new latest release using requests

    Parameters:
    None

    Returns:
    None

    """

    try:
    
        CURRENT_VERSION = "v1.4.3" ## hardcoded current vers

        response = requests.get("https://api.github.com/repos/Seinuve/Kudasai/releases/latest")
        latestVersion = response.json()["tag_name"]

        if(latestVersion != CURRENT_VERSION):
            print("There is a new update for Kudasai (" + latestVersion + ")\nIt is recommended that you use the latest version of Kudasai\nYou can download it at https://github.com/Seinuve/Kudasai/releases/latest \n")
            os.system('pause')
            os.system('cls')

        return True

    except: ## used to determine if user lacks an internet connection or posses another issue that would cause the automated mtl to fail

        return False 
    
#-------------------start-of-output_file_names()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def output_file_names():

    """
    spits out output file paths and creates directory for them
    
    Parameters:
    None

    Returns:
    preprocessPath (string) where the preprocessed text is stored
    outputPath (string) where the output/results is stored
    debugPath (string) where the debug text is stored
    jePath (string) where the text for the j-e checkers is stored
    translatedPath (string) where the text translated by Kijiku/Kaiseki is stored
    errorPath (string) where the errors are stored (if any)
    """
    scriptDir = os.path.dirname(os.path.abspath(__file__))
    outputDir = os.path.join(scriptDir, "KudasaiOutput")
    configDir = os.path.join(os.environ['USERPROFILE'],"KudasaiConfig")

    if(not os.path.exists(outputDir)):
        os.mkdir(outputDir)

    if(not os.path.exists(configDir)):
        os.mkdir(configDir)

    preprocessPath = os.path.join(outputDir, "preprocessedText.txt")
    outputPath = os.path.join(outputDir, "output.txt")
    debugPath = os.path.join(outputDir, "tlDebug.txt")
    jePath = os.path.join(outputDir, "jeCheck.txt")
    translatedPath = os.path.join(outputDir, "translatedText.txt")
    errorPath = os.path.join(outputDir, "errors.txt")
    
    return preprocessPath, outputPath, debugPath, jePath, translatedPath, errorPath,scriptDir,configDir

#-------------------start-of-replace_single_kanji()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def replace_single_kanji(jap, replacement): ## replaces a single kanji in the text

    """

    uses ner (Named Entity Recognition) from the spacy module to replace names that are composed of a single kanji in the japanese text

    Parameters:
    jap (string) holds a japanese word to be replaced
    replacement (string) holds the replacement for jap

    Returns:
    nameCount (int) how many names were replaced 

    """

    global japaneseText, totalReplacements

    i = 0
    nameCount = 0

    japLines = japaneseText.split('\n')

    while(i < len(japLines)):
        if(jap in japLines[i]):

            sentence = ner(japLines[i])

            for entity in sentence.ents:
                if(entity.text == jap and entity.label_ == "PERSON"):
                    nameCount += 1
                    japLines[i] = japLines[i][:entity.start_char] + replacement + japLines[i][entity.end_char:]

        i+=1

    japaneseText = '\n'.join(japLines)
    totalReplacements += nameCount
    
    return nameCount

#-------------------start-of-replace_single_word()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def replace_single_word(word, replacement): 

    """

    replaces single words/names in the japanese text

    Parameters:
    word (string) word to be replaced
    replacement (string) replacement for the word

    Returns:
    numOccurrences (int) number of occurrences for word

    """
    
    global japaneseText, totalReplacements 
    
    numOccurrences = japaneseText.count(word) 
    
    if(numOccurrences == 0): 
        return 0 

    japaneseText = japaneseText.replace(word, replacement) 
    totalReplacements += numOccurrences 
    
    return numOccurrences 

#-------------------start-of-loop_names()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def loop_names(character, replace=Names.FULL_NAME, honorific=Names.ALL_NAMES):
    
    """

    generates tuples of English and Japanese names to be replaced, along with a boolean indicating whether honorifics should be kept or removed

    Parameters:
    character (object- namedtuple - ('character', japName engName) ) represents a japanese word/name along with it's replacements
    replace  (object- name) how a name should be replaced
    honorific (object - name) how a honorific should be replaced

    Returns:
    tuple (string, string, bool) tuple containing the japanese name, english name, and a boolean indicating whether honorifics should be kept or removed

    """
    
    japaneseNames = character.japName.split(" ") 
    englishNames = character.engName.split(" ") 
    
    try: 
        assert len(japaneseNames) == len(englishNames) ## checks if the number of elements in japaneseNames is equal to the number of elements in englishNames

    except AssertionError:
        print("Character lengths do not match for : ") 
        print(character) 
        print("\nPlease correct character discrepancy in JSON\n")

        os.system('pause')
        exit()
    
    if(Names.FULL_NAME in replace):
        indices = range(len(japaneseNames)) ## create a range of integers from 0 to the length of japaneseNames
        combinations = itertools.chain(*(itertools.combinations(indices, i) for i in range(2, len(indices)+1))) ## create a chain of combinations of indices, starting with combinations of length 2 up to the length of indices
        
        for comb in combinations: 
            for separator in JAPANESE_NAME_SEPARATORS: 
                yield (" ".join(map(lambda i: englishNames[i], comb)), ## yield a tuple containing the following elements:
                       separator.join(map(lambda i: japaneseNames[i], comb)), ## a string created by joining the elements in comb using the map function to apply the function lambda i: englishNames[i] to each element in comb and then joining the resulting list with spaces, 
                       Names.FULL_NAME in honorific) ## a boolean indicating whether FULL_NAME is in honorific
    
    if(Names.FIRST_NAME in replace): 
        yield (englishNames[0], f'{japaneseNames[0]}', Names.FIRST_NAME in honorific)
        
    if(Names.LAST_NAME in replace): 
        yield (englishNames[-1], f'{japaneseNames[-1]}', Names.LAST_NAME in honorific) 

#-------------------start-of-replace_name()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def replace_name(character,replace=Names.FULL_NAME,noHonorific=Names.ALL_NAMES,replacedNames=dict()):

    """

    replaces names in the japanese text based off of tuples returned by loop_names

    Parameters
    character (object - namedtuple - ('character', japName engName) ) represents a japanese word/name along with it's replacements
    replace  (object - name) how a name should be replaced
    noHonorific (object - name) if a name has honorific or not
    replacedNames (dict - string) a list of replaced names and their occurrences 

    Returns:
    None

    """

    global replacementText
    
    for eng, jap, noHonor in loop_names(character, replace, noHonorific):
        if(jap in replacedNames):
            continue

        data = dict()

        for honor, honorificEnglish in replacementJson['honorifics'].items():
            data[honorificEnglish] = replace_single_word(
                f'{jap}{honor}',
                f'{eng}-{honorificEnglish}'
            )

        if(noHonor == True):
            if(len(jap) > 1 or not SINGLE_KANJI_FILTER):
                data['NA'] = replace_single_word(jap, eng)

            elif(len(jap) == 1 and SINGLE_KANJI_FILTER == True):
                data['NA'] = replace_single_kanji(jap, eng)
                

        total = sum(data.values())

        replacedNames[jap] = total

        if(not VERBOSE or total == 0):
            continue

        print(f'{eng} : {total} (', end='')
        replacementText += f'{eng} : {total} ('

        print(", ".join(map(lambda x: f'{x}-{data[x]}',
                            filter(lambda x: data[x]>0, data))), end=')\n')
        
        replacementText += ', '.join([f'{key}-{value}' for key, value in data.items() if value > 0]) + ')\n'

#-------------------start-of-replace()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def replace(): 

    """

    handles replacements and replacement rules for names in the japanese text

    Parameters:
    None

    Returns:
    japaneseText (string) the text that will be modified

    """

    global japaneseText, replacementRules, replacementText

    ## (title, jsonKey, isName, replace_name, noHonorific)
    
    replacementRules = [ 
    ('Punctuation', 'kutouten', False, None, None), 
    ('Unicode','unicode',False, None, None),
    ('Phrases','phrases',False,None,None),
    ('Words','single_words',False,None,None),
    ('Full Names', 'full_names', True,Names.ALL_NAMES, Names.FULL_NAME),
    ('Single Names', 'single_names', True, Names.FIRST_AND_LAST, Names.FIRST_AND_LAST),
    ('Name Like', 'name_like', True, Names.LAST_NAME, Names.NONE),
    ]

    replacementRules = {rule[1]: rule[2] for rule in replacementRules} ## creates a dictionary with the keys being the second element of each tuple in replacementRules and the values being the third element of each tuple in replacementRules
    
    replacedNames = {} 

    timeStart = time.time() 

    for jsonKey, isName in replacementRules.items(): ## Iterate through replacementRules dictionary

        if isName == True: ## Replace names or single words depending on the value of isName

            replaceNameParam = Names.ALL_NAMES 
            noHonorific = Names.ALL_NAMES 
            
            try:
                for jap, eng in replacementJson[jsonKey].items(): ## Iterate through dictionary 
                    if not isinstance(eng, list):  ## makes eng into a list
                        eng = [eng]

                    char = Character(" ".join(eng), jap)

                    replace_name(char, replaceNameParam, noHonorific, replacedNames) ## Replace names in text

            except KeyError: 
                continue ## Go to the next iteration of the loop

        else: 
            try:
                for jap, eng in replacementJson[jsonKey].items(): ## Iterate through dictionary at replacementJson[jsonKey]
                    numReplacements = replace_single_word(jap, eng)
                    if(numReplacements > 0): ## If a replacement was made
                        print(str(jap) + " → " + str(eng) + " : " + str(numReplacements))
                        replacementText += str(jap) + " → " + str(eng) + " : " + str(numReplacements) + "\n"

            except KeyError: 
                continue ## Go to the next iteration of the loop

    timeEnd = time.time() 

    print("\nTotal Replacements " + str(totalReplacements))
    replacementText += "\nTotal Replacements " + str(totalReplacements)

    print("\nTime Taken " + str(timeEnd-timeStart))
    replacementText += "\nTime Taken " + str(timeEnd-timeStart)

    return japaneseText ## Return the modified text

#-------------------start-of-determine_translation_automation()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def determine_translation_automation(preprocessPath,scriptDir,configDir):

    """

    determines which translation module the user wants to use and calls it

    Parameters:
    preprocessPath (string) path to where the preprocessed text was stored
    scriptDir (string) path to where the script is
    configDir (string) path to where the config is

    Returns:
    None

    """

    print("Please choose an auto translation model")
    print("\n1.Kaiseki - DeepL based line by line translation (Not very accurate by itself) (Free if using trial) (Good with punctuation)")
    print("\n2.Kijiku - OpenAI based batch translator (Very accurate) (Pricey) ($0.002 per 1k Tokens)\n")
    
    mode = input()

    if(mode == "1"):
        run_kaiseki(preprocessPath,scriptDir,configDir)
    
    elif(mode == "2"):
        run_kijiku(preprocessPath,scriptDir,configDir)

    else:
        exit()

#-------------------start-of-run_kaiseki()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def run_kaiseki(preprocessPath,scriptDir,configDir):

    """

    Handles the optional auto translation using the deepL api if enabled

    Parameters:
    preprocessPath (string) path to where the preprocessed text was stored

    Returns:
    None

    """

    os.system('cls')
    
    print("Commencing Automated Translation\n")

    sleep(2)

    translator,japaneseText = Kaiseki.initialize_translator(preprocessPath,configDir)

    Kaiseki.commence_translation(translator,japaneseText,scriptDir)

#-------------------start-of-run_kijiku()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def run_kijiku(preprocessPath,scriptDir,configDir):

    """

    Handles the optional auto translation using the gpt/openai api if enabled

    Parameters:
    preprocessPath (string) path to where the preprocessed text was stored

    Returns:
    None

    """

    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    ctypes.windll.user32.ShowWindow(hwnd, 3) 

    os.system('cls')

    japaneseText,kijikuRules = Kijiku.initialize_text(preprocessPath,configDir)

    print("\nAre these settings okay? (1 for yes or 2 for no) : \n\n")

    for key,value in kijikuRules["open ai settings"].items():
        print(key + " : " + str(value))

    if(input("\n") == "1"):
        pass
    else:
        Kijiku.change_settings(kijikuRules,configDir)

    os.system('cls')

    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    ctypes.windll.user32.ShowWindow(hwnd, 9)

    print("Commencing Automated Translation\n")

    sleep(2)

    Kijiku.commence_translation(japaneseText,scriptDir,configDir)

#-------------------start of main()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def main(inputFile, jsonFile):

    """

    reads the text from `inputFile`, replaces names and honorifics in the text based on the data in `jsonFile`, and writes the results to the folder "KudasaiInput"

    Parameters:
    inputFile (string) path to the txt file we are preprocessing
    jsonFile (string) path to the json file whose "rules" we are following

    Returns:
    None

    """
    
    global japaneseText, replacementJson, totalReplacements, replacementText 

    connection = check_update()
    
    with open(inputFile, 'r', encoding='utf-8') as file: 
        japaneseText = file.read()
        
    try:

        with open(jsonFile, 'r', encoding='utf-8') as file: ## opens the jsonFile in read mode with utf-8 encoding
            replacementJson = json.load(file) ## loads the contents of the file as a JSON object and assigns it to the variable replacementJson
    
    except:

        print("The second path you provided is either invalid, not a JSON file, or the JSON file has an error.\n")
        os.system('pause')

        exit()

    replace() 
    
    preprocessPath,outputPath,debugPath,jePath,translatedPath,errorPath,scriptDir,configDir = output_file_names()

    with open(preprocessPath, 'w+', encoding='utf-8') as file: 
        file.write(japaneseText) ## writes the contents of the preprocessed text to the file

    with open(outputPath, 'w+', encoding='utf-8') as file: 
        file.write(replacementText) ## writes the contents of kudasai's results to the file

    with open(debugPath, 'w+', encoding='utf-8') as file: 
        file.truncate(0)

    with open(jePath, 'w+', encoding='utf-8') as file: 
        file.truncate(0)

    with open(translatedPath, 'w+', encoding='utf-8') as file: 
        file.truncate(0)

    with open(errorPath, 'w+', encoding='utf-8') as file: 
        file.truncate(0)

    print("\n\nResults have been written to : " + preprocessPath)
    print("\nKudasai replacement output has been written to : " + outputPath + "\n")
    
    os.system('pause /P "Press any key to auto translate..."')
    os.system('cls')
    
    if(connection == True):
        determine_translation_automation(preprocessPath,scriptDir,configDir)

#-------------------start of sub_main()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

if(__name__ == '__main__'): # checks sys arguments and if less than 3 or called outside cmd prints usage statement

    if(len(sys.argv) < 3): 

        print(f'\nUsage: {sys.argv[0]} input_txt_file replacement.json\nSee README.md for more information.\n') 
        
        os.system('pause')
        exit() 

    os.system('cls')

    os.system("title " + "Kudasai")

    main(sys.argv[1], sys.argv[2]) # Call main function with the first and second command line arguments as the input file and replacement JSON, respectively

