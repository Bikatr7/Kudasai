## Kudasai.py

## Orginal Author: thevoidzero#4686
## Refactored and Added To By :Seinu#4440

## Purpose: Used to Make Classroom Of The Elite DeepL inserts easier

## Python Version : 3.7.6-3.11.1

## CmdLineArgs
## Argument 1 - Path to .txt file that needs to be edited
## Argument 2 - Path to Json Criteria

##  Output : input file + "-Kudasai"

import re ## imports the regular expression module
import sys ## imports the sys module
import json ## imports the json module
import os ## imports the os module
import time ## imports the time module
import itertools ## imports the itertools module

from enum import Flag ## imports the Flag enum from the enum module
from collections import namedtuple ## imports the namedtuple from the collections module

#-------------------start of globals---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Character = namedtuple('Character', 'jp_name en_name') ## defines a named tuple called Character with two fields: jp_name and en_name

VERBOSE = True ## assigns the value True to the constant VERBOSE
SINGLE_KANJI_FILTER=True ## assigns the value True to the constant SINGLE_KANJI_FILTER

text = '' ## assigns an empty string to the variable text

total_replacements = 0 ## assigns the value 0 to the variable total_replacements

rep = dict() ## assigns an empty dictionary to the variable rep

JP_NAME_SEPS = ["・", ""] ## assigns a list containing two strings to the constant JP_NAME_SEPS

#-------------------start of Names()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Names(Flag): ## defines a class called Names that inherits from the Flag class
    NONE = 0 ## defines a class constant NONE with a value of 0
    FULL_NAME = 1 ## defines a class constant FULL_NAME with a value of 1
    FIRST_NAME = 2 ## defines a class constant FIRST_NAME with a value of 2
    FULL_AND_FIRST = 3 ## defines a class constant FULL_AND_FIRST with a value of 3
    LAST_NAME = 4 ## defines a class constant LAST_NAME with a value of 4
    FULL_AND_LAST = 5 ## defines a class constant FULL_AND_LAST with a value of 5
    FIRST_AND_LAST = 6 ## defines a class constant FIRST_AND_LAST with a value of 6
    ALL_NAMES = 7 ## defines a class constant ALL_NAMES with a value of 7
    
#-------------------start of output_file_name()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def output_file_name(inputFile): ## defines a function that takes in an argument called inputFile
    
    """
    spits out output file with -Kudasai ender
    """
    
    p, e = os.path.splitext(inputFile) ## calls the splitext function from the os module on the inputFile and assigns the returned tuple to p and e
    
    return f'{p}-Kudasai{e}' ## returns a formatted string with p, "-Kudasai", and e interpolated

#-------------------start of  replace_singke_word()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def replace_single_word(word, replacement): ## defines a function that takes in two arguments: word and replacement

    """
    replaces all occurrences of `word` in the global variable `text` with `replacement` and increments the global variable `total_replacements` by the number of replacements
    """
    
    global text, total_replacements ## declares the global variables text and total_replacements to be used within this function
    
    n = text.count(word) ## counts the number of occurrences of `word` in `text` and assigns the result to `n`
    
    if(n == 0): ## if `n` is equal to 0
        return 0 ## return 0

    text = text.replace(word, replacement) ## replace all occurrences of `word` in `text` with `replacement`
    total_replacements += n ## increment `total_replacements` by `n`
    
    return n ## return `n`

#-------------------start of loop_names()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def loop_names(character, replace=Names.FULL_NAME, honorific=Names.ALL_NAMES):
    
    """
    generates tuples of English and Japanese names to be replaced, along with a boolean indicating whether honorifics should be kept or removed
    """
    
    jp_names = character.jp_name.split(" ") ## splits the jp_name field of the character tuple by spaces and assigns the resulting list to jp_names
    en_names = character.en_name.split(" ") ## splits the en_name field of the character tuple by spaces and assigns the resulting list to en_names
    
    try: ## tries to execute the code in the following block
        assert len(jp_names) == len(en_names) ## checks if the number of elements in jp_names is equal to the number of elements in en_names
    except AssertionError: ## if an AssertionError is raised
        print("Character names do not match : \n") ## print a message
        print(character) ## print the character tuple

        os.system('pause') ## pause the system
        sys.exit(0) ## exit the program
    
    if Names.FULL_NAME in replace: ## if FULL_NAME is in the replace set
        indices = range(len(jp_names)) ## create a range of integers from 0 to the length of jp_names
        combinations = itertools.chain(*(itertools.combinations(indices, i) for i in range(2, len(indices)+1))) ## create a chain of combinations of indices, starting with combinations of length 2 up to the length of indices
        for comb in combinations: ## for each combination in combinations
            for sep in JP_NAME_SEPS: ## for each separator in JP_NAME_SEPS
                yield (" ".join(map(lambda i: en_names[i], comb)), ## yield a tuple containing the following elements:
                       sep.join(map(lambda i: jp_names[i], comb)), ## a string created by joining the elements in comb using the map function to apply the function lambda i: en_names[i] to each element in comb and then joining the resulting list with spaces, 
                       Names.FULL_NAME in honorific) ## a boolean indicating whether FULL_NAME is in honorific
    
    if Names.FIRST_NAME in replace: ## if FIRST_NAME is in the replace set
        yield (en_names[0], f'{jp_names[0]}', Names.FIRST_NAME in honorific) ## yield a tuple containing the first element of en_names, the first element of jp_names, and a boolean indicating whether FIRST_NAME is in honorific
        
    if Names.LAST_NAME in replace: ## if LAST_NAME is in the replace set
        yield (en_names[-1], f'{jp_names[-1]}', Names.LAST_NAME in honorific) ## yield a tuple containing the last element of en_names, the last element of jp_names, and a boolean indicating whether LAST_NAME is in honorific

#-------------------start of replace_name()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def replace_name(character, replace=Names.FULL_NAME, no_honorific=Names.ALL_NAMES, replaced_names=[]):
    
    """
    replaces all occurrences of the names and honorifics of a character in the global variable `text`
    """
    
    for name_en, name_jp, remove_honorific in loop_names(character, replace, no_honorific): ## for each tuple returned by loop_names
        if name_jp in replaced_names: ## if name_jp is in the list replaced_names
            continue ## skip the rest of the loop
        
        data = {} ## create an empty dictionary called data
        
        for honorific_jp, honorific_en in rep['honorifics'].items(): ## for each key-value pair in the honorifics field of the rep dictionary
            data[honorific_en] = replace_single_word(f'{name_jp}{honorific_jp}', f'{name_en}-{honorific_en}') ## call the replace_single_word function with the key as the first argument and the value as the second argument, and store the result in the data dictionary with the key being the value and the value being the result of the function call
        
        if no_honorific: ## if no_honorific is True
            if len(name_jp) > 1 or not SINGLE_KANJI_FILTER: ## if the length of name_jp is greater than 1 or SINGLE_KANJI_FILTER is False
                data['NA'] = replace_single_word(name_jp, name_en) ## call the replace_single_word function with name_jp as the first argument and name_en as the second argument, and store the result in the data dictionary with the key 'NA' and the value being the result of the function call
        
        total = sum(data.values()) ## sum the values in the data dictionary and assign the result to total
        replaced_names[name_jp] = total ## add a key-value pair to the replaced_names list with the key being name_jp and the value being total
        
        if not VERBOSE or total == 0: ## if VERBOSE is False or total is equal to 0
            continue ## skip the rest of the loop
        
        print(f'    {name_en} :{total} (', end='') ## print a formatted string with name_en and total interpolated, and end the line with ' ('
        print(", ".join(f'{x}-{data[x]}' for x in filter(lambda x: data[x]>0, data)), end=')\n') ## print a string created by joining a list of strings created by applying the function f'{x}-{data[x]}' to each element in a filtered version of the data dictionary using the filter function with the function lambda x: data[x]>0 as the filtering function, and end the line with ')\n'

#-------------------start of main()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def main(input_file, rep_file):
    
    """
    reads the text from `input_file`, replaces names and honorifics in the text based on the data in `rep_file`, and writes the resulting text to a file with "-Kudasai" appended to the input_file name
    """
    
    global text, rep, total_replacements ## declares the global variables text, rep, and total_replacements to be used within this function
    
    with open(input_file, 'r', encoding='utf-8') as file: ## opens the input_file in read mode with utf-8 encoding
        text = file.read() ## reads the contents of the file and assigns it to the variable text
        
    with open(rep_file, 'r', encoding='utf-8') as file: ## opens the rep_file in read mode with utf-8 encoding
        rep = json.load(file) ## loads the contents of the file as a JSON object and assigns it to the variable rep
    
    replace() ## calls the replace function
    
    out_file = output_file_name(input_file) ## calls the output_file_name function with input_file as the argument and assigns the result to out_file
    
    with open(out_file, 'w', encoding='utf-8') as file: ## opens the out_file in write mode with utf-8 encoding
        file.write(text) ## writes the contents of text to the file
        
#-------------------start of replace()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def replace(): ## defines the replace function
    global text, replacement_rules ## declares the global variables text and replacement_rules to be used within this function

    ## (title, json_key, is_name, replace_name, no_honorific)
    
    replacement_rules = [ ## creates a list of tuples containing the replacement rules
    ('Punctuation', 'Kutouten', False, None, None), ## tuple for replacing special words
    ('Full Names', 'full_names', True,Names.ALL_NAMES, Names.FULL_NAME), ## tuple for replacing remaining names
    ('Single Names', 'single_names', True, Names.LAST_NAME, Names.LAST_NAME), ## tuple for replacing single names
    ('Name Like', 'name_like', True, Names.LAST_NAME, Names.NONE), ## tuple for replacing name-like words
    ]
    replacement_rules = {rule[1]: rule[2] for rule in replacement_rules} ## creates a dictionary with the keys being the second element of each tuple in replacement_rules and the values being the third element of each tuple in replacement_rules

    ## Default value for replaced_names dictionary
    replaced_names = {} ## creates an empty dictionary called replaced_names
    time_start = time.time() ## gets the current time in seconds and assigns

    
    for json_key, is_name in replacement_rules.items(): # Iterate through replacement_rules dictionary
        prev_count = total_replacements # Save the current total number of replacements

        if is_name: ## Replace names or single words depending on the value of is_name
            replace_name_param = Names.ALL_NAMES # Set parameter for replace_name function
            no_honorific = Names.ALL_NAMES # Set parameter for replace_name function
            try:
                for k, v in rep[json_key].items(): # Iterate through dictionary at rep[json_key]
                    if not isinstance(v, list): # If v is not a list, set it to a list with v as the only element
                        v = [v]
                    char = Character(" ".join(v), k) # Create a Character object with " ".join(v) as the name and k as the key
                    replace_name(char, replace_name_param, no_honorific, replaced_names) # Replace names in text
            except KeyError: # If a KeyError is encountered
                continue # Go to the next iteration of the loop
        else: # If is_name is False
            try:
                for k, v in rep[json_key].items(): # Iterate through dictionary at rep[json_key]
                    n = replace_single_word(k, v) # Replace single word in text
                    if(n > 0): # If a replacement was made
                        print(f'    {k} → {v}:{n}') # Print number of replacements made
            except KeyError: # If a KeyError is encountered
                continue # Go to the next iteration of the loop
      
    time_end = time.time() # Set time_end to the current time

    print(f'\nTotal Replacements: {total_replacements}') # Print the total number of replacements made
    print(f'\nTime Taken: {time_end-time_start} seconds') # Print the time taken in seconds

    return text # Return the modified text

#-------------------start of sub_main()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

if(__name__ == '__main__'): ## checks sys arguments and if less than 3 or called outside cmd prints usage statement
    if(len(sys.argv) < 3): # If there are less than 3 command line arguments
        print(f'Usage: {sys.argv[0]} input_file replacement_json') # Print usage statement
        exit(0) # Exit the program

    os.system('cls')
    main(sys.argv[1], sys.argv[2]) # Call main function with the first and second command line arguments as the input file and replacement JSON, respectively
