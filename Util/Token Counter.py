## built-in modules
import sys
import os
import time

## third-party modules
import tiktoken

## custom modules
import associated_functions

##-------------------start-of-count_characters()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def count_characters(text:str) -> int:

    '''

    counts the number of characters in a string\n
 
    Parameters:\n
    text (string) the text that will be counting characters for\n

    Returns:\n
    num_characters (int) the number of characters in the text\n

    '''

    associated_functions.clear_console()

    num_characters = len(text)

    return num_characters

##-------------------start-of-estimate_cost()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def estimate_cost(text:str, model:str) -> tuple[int,float]:
    
    '''

    attempts to estimate cost and number of tokens in a string\n
 
    Parameters:\n
    text (string) the text that will be counting tokens for\n
    model (string)  represents which model we will be using\n

    Returns:\n
    num_tokens (int) the estimated number of tokens in the text\n
    min_cost (double) the estimated cost of translating text\n

    '''

    associated_functions.clear_console()
    
    try:

        encoding = tiktoken.encoding_for_model(model)

    except KeyError:

        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")

    if(model == "gpt-3.5-turbo"):
        print("Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301.")
        time.sleep(1)
        return estimate_cost(text, model="gpt-3.5-turbo-0301")
    
    elif(model == "gpt-4"):
        print("Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-0314.")
        time.sleep(1)
        return estimate_cost(text, model="gpt-4-0314")
    
    elif(model == "gpt-3.5-turbo-0301"):
        cost_per_1000_tokens = 0.002

    elif(model == "gpt-4-0314"):
        cost_per_1000_tokens = 0.06

    else:
        raise NotImplementedError(f"""Token Counter does not support : {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how text are converted to tokens.""")
    
    num_tokens = len(encoding.encode(text))

    min_cost = round((float(num_tokens) / 1000.00) * cost_per_1000_tokens, 5)

    return num_tokens, min_cost

##-------------------start-of-main()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def main(text_file:str) -> None:

    '''

    main function\n

    Parameters:\n
    text_file (string) the text file that will be counting tokens for\n

    Returns:\n
    None\n
    
    '''


    with open(text_file, 'r', encoding='utf-8') as file: 
        text = file.read()

    model = input("Please enter model : ")

    num_tokens,min_cost = estimate_cost(text,model)
    num_characters = count_characters(text)

    print("Estimated Number of Tokens in Text : " + str(num_tokens))
    print("Estimated Minimum Cost of Translation : " + str(min_cost))
    print("Number of Characters in Text : " + str(num_characters) + "\n")

    associated_functions.pause_console()

##-------------------start-of-sub_main()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

if(__name__ == '__main__'): ## checks sys arguments and if less than 2 or called outside cmd prints usage statement

    if(len(sys.argv) < 2): 

        print(f'\nUsage: {sys.argv[0]} input_txt_file\n') 
        
        associated_functions.pause_console()
        exit() 

    associated_functions.clear_console()

    os.system("title " + "Token Counter")

    main(sys.argv[1]) ## Call main function with the first command line argument