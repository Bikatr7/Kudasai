## built-in modules
import sys
import os
import time
import typing

## custom modules
from modules.toolkit import Toolkit

class TokenCounter:

    """
    
    Util script for counting tokens, characters, and estimating cost of translating a text.\n

    """

##-------------------start-of-__init__()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self) -> None:

        """

        Constructor for TokenCounter class.

        """

        os.system("title " + "Token Counter")

        self.MODEL = None

##-------------------start-of-count_characters()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def count_characters(self) -> int:

        """

        Counts the number of characters in a string.
    
        Parameters:
        self (object - TokenCounter) : The TokenCounter object.

        Returns:
        num_characters (int) The number of characters in the text.

        """

        Toolkit.clear_console()

        num_characters = len(self.text)

        return num_characters

##-------------------start-of-alculate_min_cost()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def calculate_min_cost(self) -> typing.Tuple[int, float]:

        """

        Gives a cost estimate for translating a text using Kudasai.
    
        Parameters:
        self (object - TokenCounter) : The TokenCounter object.

        Returns:
        num_tokens (int) The number of tokens in the text.
        min_cost (float) The minimum cost of translating the text.

        """

        cost_per_thousand_tokens = 0

        try:
            import tiktoken

        except ImportError:
            Toolkit.clear_console()
            raise ImportError("tiktoken not found. Please install tiktoken using pip install tiktoken.")
        
        try:
            encoding = tiktoken.encoding_for_model(self.MODEL) ## type: ignore
            
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding. Cost estimate will be extremely inaccurate.")
            encoding = tiktoken.get_encoding("cl100k_base")

        if(self.MODEL == "gpt-3.5-turbo"):
            print("Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-1106.")
            self.MODEL="gpt-3.5-turbo-1106"
            return self.calculate_min_cost()
        
        elif(self.MODEL == "gpt-3.5-turbo-0613"):
            print("Warning: gpt-3.5-turbo-0613 is outdated and will be considered depreciated by June 13th 2024. Please consider switching to gpt-3.5-turbo-1106 unless you are specifically trying to break the filter. Returning num tokens assuming gpt-3.5-turbo-1106.")
            self.MODEL="gpt-3.5-turbo-1106"
            return self.calculate_min_cost()
        
        elif(self.MODEL == 	"gpt-3.5-turbo-16k-0613"):
            print("Warning: gpt-3.5-turbo-16k-0613 is outdated and will be considered depreciated by June 13th 2024. Returning num tokens assuming gpt-3.5-turbo-16k-0613.")

        elif(self.MODEL == "gpt-3.5-turbo-0301"):
            print("Warning: gpt-3.5-turbo-0301 is outdated. gpt-3.5-turbo-0301's support ended September 13, and will be considered depreciated by June 13th 2024. Please consider switching to gpt-3.5-turbo-1106 unless you are specifically trying to break the filter. Returning num tokens assuming gpt-3.5-turbo-1106.")
            return self.calculate_min_cost()

        elif(self.MODEL == "gpt-4"):
            print("Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-0613.")
            self.MODEL="gpt-4-0613"
            return self.calculate_min_cost()
        
        elif(self.MODEL == "gpt-4-0314"):
            print("Warning: gpt-4-0314 is outdated. gpt-4-0314's support ended September 13, and will be considered depreciated by June 13th 2024.Returning num tokens assuming gpt-4-0613.")
            self.MODEL="gpt-4-0613"
            return self.calculate_min_cost()
        
        elif(self.MODEL == "gpt-4-32k"):
            print("Warning: gpt-4-32k may change over time. Returning num tokens assuming gpt-4-32k-0613.")
            self.MODEL="gpt-4-32k-0613"
            return self.calculate_min_cost()
        
        elif(self.MODEL == "gpt-4-32k-0314"):
            print("Warning: gpt-4-32k-0314 is outdated. gpt-4-32k-0314's support ended September 13, and will be considered depreciated by June 13th 2024. Please consider switching to gpt-4-32k-0613 unless you are specifically trying to break the filter. Returning num tokens assuming gpt-4-32k-0613.")
            self.MODEL="gpt-4-32k-0613"
            return self.calculate_min_cost()
        
        elif(self.MODEL == "gpt-3.5-turbo-1106"):
            cost_per_thousand_tokens = 0.0015

        elif(self.MODEL == "gpt-3.5-turbo-16k-0613"):
            cost_per_thousand_tokens = 0.0030

        elif(self.MODEL == "gpt-4-0613"):
            cost_per_thousand_tokens = 0.03

        elif(self.MODEL == "gpt-4-32k-0613"):
            cost_per_thousand_tokens = 0.06

        elif(self.MODEL == "gpt-4-1106-preview"):
            cost_per_thousand_tokens = 0.01

        else:
            raise NotImplementedError(f"""Kudasai does not support : {self.MODEL}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
        
        num_tokens = len(encoding.encode(self.text))

        min_cost = round((float(num_tokens) / 1000.00) * cost_per_thousand_tokens, 5)

        return num_tokens, min_cost

##-------------------start-of-estimate_cost()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def estimate_cost(self, text_file:str) -> None:

        """

        Counts the number of tokens in a text file.

        Parameters:
        self (object - TokenCounter) : The TokenCounter object.
        text_file (string)  : The text file that will be counting tokens for.
        
        """


        with open(text_file, 'r', encoding='utf-8') as file: 
            self.text = file.read()

        self.MODEL = input("Please enter model : ")

        num_tokens, min_cost = self.calculate_min_cost()
        num_characters = self.count_characters()

        print("THIS ESTIMATE DOES NOT YET CONSIDER OUTPUT TOKENS, OUTPUT TOKENS ARE ROUGHLY 2X AS EXPENSIVE AS INPUT TOKENS.\n\n")
        print("Estimated Number of Tokens in Text : " + str(num_tokens))
        print("Estimated Minimum Cost of Translation : " + str(min_cost))
        print("Number of Characters in Text : " + str(num_characters) + "\n")

        Toolkit.pause_console()

##-------------------start-of-sub_main()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

client = TokenCounter()

## checks sys arguments and if less than 2 or called outside cmd prints usage statement
if(__name__ == '__main__'): 

    if(len(sys.argv) < 2): 

        print(f'\nUsage: {sys.argv[0]} input_txt_file\n') 
        
        Toolkit.pause_console()
        exit() 

    Toolkit.clear_console()

    client.estimate_cost(sys.argv[1])
