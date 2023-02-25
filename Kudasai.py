"""
Kudasai.py

Orginal Author: thevoidzero#4686
Refactored and Maintained by : Seinu#7854
Contrbutions by : SnOrT NeSqUiK™#9775

Run pip commands listed in requirements.txt before running Kudasai

Python Version : 3.7.6-3.11.1

Used to make Classroom of the Elite translation easier by automatically replacing characters in the japanese text with their english equivalents

Dervied from https://github.com/Atreyagaurav/mtl-related-scripts

CmdLineArgs
Argument 1 - Path to .txt file that needs to be edited
Argument 2 - Path to Json Criteria

Output : input file + "-Kudasai", input file + "-Kudasai-Output"

To use

Step 1 : Open Cmd
Step 2 : Copy path of Kudasai.py to cmd and type a space
Step 3 : Copy path of .txt file you want to alter to cmd and type a space
Step 4 : Copy path of Replacements.json to cmd
Step 5 : Press enter

After steps are completed, the output file will be in the same location as the input .txt file (same path) but with -Kudasai appended to it, Kudasai's output will also be at the same location but with "-Kudasai-Output" appended

Any questions or bugs, please email Seinuve@gmail.com

"""

import sys 
import json 
import os 
import time 
import itertools
import spacy

from enum import Flag 
from collections import namedtuple 

#-------------------start of globals---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Character = namedtuple('Character', 'jp_name en_name')

nlp = spacy.load("ja_core_news_lg") # large model

VERBOSE = True 
SINGLE_KANJI_FILTER = True ## filters out single kanji or uses specific function to deal with it when replacing names
JAPANESE_NAME_SEPERATORS = ["・", ""] 

japaneseText = ''
replacementText = ''

totalReplacements = 0 

replacementJson = dict() 

#-------------------start of Names()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Names(Flag): 
    NONE = 0 
    FULL_NAME = 1 
    FIRST_NAME = 2 
    FULL_AND_FIRST = 3 
    LAST_NAME = 4 
    FULL_AND_LAST = 5 
    FIRST_AND_LAST = 6 
    ALL_NAMES = 7 

#-------------------start of output_file_name()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def output_file_names(inputFile): ## returns the file path for the output files
    
    """
    spits out output file with -Kudasai ender
    """
    kudasaiPath, fileType = os.path.splitext(inputFile) 
    
    return f'{kudasaiPath}-Kudasai{fileType}',f'{kudasaiPath}-Kudasai-Output{fileType}' ## returns the paths for kudasai output and kudasai results

#-------------------start of replace_single_kanji()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def replace_single_kanji(jap, replacement): ## replaces a single kanji in the text

    global japaneseText, totalReplacements

    i = 0
    nameCount = 0

    japLines = japaneseText.split('\n')

    while(i < len(japLines)):
        if(jap in japLines[i]):

            sentence = nlp(japLines[i])

            for entity in sentence.ents:
                if(entity.text == jap and entity.label_ == "PERSON"):
                    nameCount += 1
                    japLines[i] = japLines[i].replace(jap,replacement)

        i+=1

    japaneseText = '\n'.join(japLines)
    totalReplacements += nameCount
    
    return nameCount

#-------------------start of replace_single_word()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def replace_single_word(word, replacement): ## replaces all single words in the japanese text with their english equivalents
    
    global japaneseText, totalReplacements 
    
    numOccurences = japaneseText.count(word) 
    
    if(numOccurences == 0): 
        return 0 

    japaneseText = japaneseText.replace(word, replacement) 
    totalReplacements += numOccurences 
    
    return numOccurences 

#-------------------start of loop_names()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def loop_names(character, replace=Names.FULL_NAME, honorific=Names.ALL_NAMES):
    
    """
    generates tuples of English and Japanese names to be replaced, along with a boolean indicating whether honorifics should be kept or removed
    """
    
    japaneseNames = character.jp_name.split(" ") 
    englishNames = character.en_name.split(" ") 
    
    try: 
        assert len(japaneseNames) == len(englishNames) ## checks if the number of elements in japaneseNames is equal to the number of elements in englishNames

    except AssertionError:
        print("Character lengths do not match : \n") 
        print(character) 
        print("\nPlease correct character disrepency in JSON\n")

        os.system('pause')
        exit()
    
    if Names.FULL_NAME in replace:
        indices = range(len(japaneseNames)) ## create a range of integers from 0 to the length of japaneseNames
        combinations = itertools.chain(*(itertools.combinations(indices, i) for i in range(2, len(indices)+1))) ## create a chain of combinations of indices, starting with combinations of length 2 up to the length of indices
        
        for comb in combinations: 
            for seperator in JAPANESE_NAME_SEPERATORS: 
                yield (" ".join(map(lambda i: englishNames[i], comb)), ## yield a tuple containing the following elements:
                       seperator.join(map(lambda i: japaneseNames[i], comb)), ## a string created by joining the elements in comb using the map function to apply the function lambda i: englishNames[i] to each element in comb and then joining the resulting list with spaces, 
                       Names.FULL_NAME in honorific) ## a boolean indicating whether FULL_NAME is in honorific
    
    if Names.FIRST_NAME in replace: 
        yield (englishNames[0], f'{japaneseNames[0]}', Names.FIRST_NAME in honorific)
        
    if Names.LAST_NAME in replace: 
        yield (englishNames[-1], f'{japaneseNames[-1]}', Names.LAST_NAME in honorific) 

#-------------------start of replace_name()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def replace_name(character,replace=Names.FULL_NAME,noHonorific=Names.ALL_NAMES,replacedNames=list()):

    global replacementText
    
    for eng, jap, noHonor in loop_names(character, replace, noHonorific):
        if jap in replacedNames:
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
                data['NA'] = replace_single_kanji(jap,eng)
                

        total = sum(data.values())

        replacedNames[jap] = total
        if not VERBOSE or total == 0:
            continue

        print(f'{eng} : {total} (', end='')
        replacementText += f'{eng} : {total} ('

        print(", ".join(map(lambda x: f'{x}-{data[x]}',
                            filter(lambda x: data[x]>0, data))), end=')\n')
        
        replacementText += ', '.join([f'{key}-{value}' for key, value in data.items() if value > 0]) + ')\n'

#-------------------start of replace()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def replace(): 
    global japaneseText, replacementRules,replacementText

    ## (title, json_key, is_name, replace_name, noHonorific)
    
    replacementRules = [ 
    ('Punctuation', 'kutouten', False, None, None), 
    ('Phrases','phrases',False,None,None),
    ('Words','single_words',False,None,None),
    ('Full Names', 'full_names', True,Names.ALL_NAMES, Names.FULL_NAME),
    ('Single Names', 'single_names', True, Names.FIRST_AND_LAST, Names.FIRST_AND_LAST),
    ('Name Like', 'name_like', True, Names.LAST_NAME, Names.NONE),
    ]

    replacementRules = {rule[1]: rule[2] for rule in replacementRules} ## creates a dictionary with the keys being the second element of each tuple in replacementRules and the values being the third element of each tuple in replacementRules
    
    replacedNames = {} 

    timeStart = time.time() 

    for json_key, is_name in replacementRules.items(): # Iterate through replacementRules dictionary

        if is_name == True: ## Replace names or single words depending on the value of is_name

            replaceNameParam = Names.ALL_NAMES 
            noHonorific = Names.ALL_NAMES 
            
            try:
                for jap, eng in replacementJson[json_key].items(): # Iterate through dictionary 
                    if not isinstance(eng, list):  ## makes eng into a list
                        eng = [eng]

                    char = Character(" ".join(eng), jap)

                    keys_list = list(replacementRules.keys())

                    replace_name(char, replaceNameParam, noHonorific, replacedNames) # Replace names in text

            except KeyError: 
                continue # Go to the next iteration of the loop

        else: # If is_name is False
            try:
                for jap, eng in replacementJson[json_key].items(): # Iterate through dictionary at replacementJson[json_key]
                    numReplacements = replace_single_word(jap, eng)
                    if(numReplacements > 0): # If a replacement was made
                        print(str(jap) + " → " + str(eng) + " : " + str(numReplacements))
                        replacementText += str(jap) + " → " + str(eng) + " : " + str(numReplacements) + "\n"

            except KeyError: 
                continue # Go to the next iteration of the loop

    timeEnd = time.time() 

    print("\nTotal Replacments " + str(totalReplacements))
    replacementText += "\nTotal Replacments " + str(totalReplacements)

    print("\nTime Taken " + str(timeEnd-timeStart))
    replacementText += "\nTime Taken " + str(timeEnd-timeStart)

    return japaneseText # Return the modified text

#-------------------start of main()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def main(inputFile, jsonFile):
    
    """
    reads the text from `inputFile`, replaces names and honorifics in the text based on the data in `jsonFile`, and writes the resulting text to a file with "-Kudasai" appended to the inputFile name
    """
    
    global japaneseText, replacementJson, totalReplacements, replacementText 
    
    with open(inputFile, 'r', encoding='utf-8') as file: 
        japaneseText = file.read()
        
    with open(jsonFile, 'r', encoding='utf-8') as file: ## opens the jsonFile in read mode with utf-8 encoding
        replacementJson = json.load(file) ## loads the contents of the file as a JSON object and assigns it to the variable replacementJson
    
    replace() 
    
    outputFile,replacement_file = output_file_names(inputFile) 

    with open(outputFile, 'w+', encoding='utf-8') as file: 
        file.write(japaneseText) ## writes the contents of the updated text to the file

    with open(replacement_file, 'w+', encoding='utf-8') as file: 
        file.write(replacementText) ## writes the contents of kudasai's results to the file

    print("\n\nResults have been written to : " + outputFile)
    print("\nKudasai replacement output has been written to : " + replacement_file)

#-------------------start of sub_main()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

if(__name__ == '__main__'): # checks sys arguments and if less than 3 or called outside cmd prints usage statement
    if(len(sys.argv) < 3): 

        try:
            f = open(os.getcwd() + "\README.md","r",encoding="utf-8")
            print(f.read() + "\n")
            f.close()
        except:
            pass

        print(f'\nUsage: {sys.argv[0]} input_txt_file replacement.json\n') 
        
        os.system('pause')
        exit(0) 

    os.system('cls')
    main(sys.argv[1], sys.argv[2]) # Call main function with the first and second command line arguments as the input file and replacement JSON, respectively

