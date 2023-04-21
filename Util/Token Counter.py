import sys
import os
import tiktoken

#-------------------start-of-estimate_cost()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def estimate_cost(text, model):
    
    '''

    attempts to estimate cost and number of tokens in a string, (seems accurate)
 
    Parameters:
    text (string) the text that will be counting tokens for
    model (string  represents which model we will be using

    Returns:
    numTokens (int - number) the estimated number of tokens in the text
    cost (double - money) the estimated cost of translating text

    '''

    os.system('cls')
    
    try:

        encoding = tiktoken.encoding_for_model(model)

    except KeyError:

        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")

    if(model == "gpt-3.5-turbo"):
        print("Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301.")
        return estimate_cost(text, model="gpt-3.5-turbo-0301")
    
    elif(model == "gpt-4"):
        print("Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-0314.")
        return estimate_cost(text, model="gpt-4-0314")
    
    elif(model == "gpt-3.5-turbo-0301"):
        cosPer1000Tokens = 0.002

    elif(model == "gpt-4-0314"):
        cosPer1000Tokens = 0.006

    else:
        raise NotImplementedError(f"""Token Counter does not support : {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how text are converted to tokens.""")
    
    numTokens = len(encoding.encode(text))

    minCost = (float(numTokens) / 1000.00) * cosPer1000Tokens

    return numTokens, minCost

#-------------------start-of-main()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------


def main(txtFile):

    with open(txtFile, 'r', encoding='utf-8') as file: 
        text = file.read()

    model = input("Please enter model : ")

    numTokens,minCost = estimate_cost(text,model)

    print("\nEstimated Number of Tokens in Text : " + str(numTokens))
    print("Estimated Minimum Cost of Translation : " + str(minCost) + "\n")

    os.system('pause')

#-------------------start-of-sub_main()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

if(__name__ == '__main__'): # checks sys arguments and if less than 2 or called outside cmd prints usage statement

    if(len(sys.argv) < 2): 

        print(f'\nUsage: {sys.argv[0]} input_txt_file\n') 
        
        os.system('pause')
        exit() 

    os.system('cls')

    os.system("title " + "Token Counter")

    main(sys.argv[1]) # Call main function with the first command line argument