## built-in libraries
from pathlib import Path

import sys
import os
import typing

## third-party libraries
import tiktoken

## Calculates the path to the modules directory and add it to sys.path
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent

## Add the parent directory to sys.path so 'modules' can be found
sys.path.append(str(parent_dir))

## custom modules
from modules.toolkit import Toolkit

class TokenCounter:

    """
    
    Util script for counting tokens, characters, and estimating cost of translating a text.

    """

##-------------------start-of-__init__()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self) -> None:

        """

        Constructor for TokenCounter class.

        """

        os.system("title " + "Token Counter")

        self.MODEL:str = ""

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

##-------------------start-of-calculate_min_cost()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def calculate_min_cost(self, model:str, price_case:int | None = None) -> typing.Tuple[int, float, str]:

        """

        Gives a cost estimate for translating a text using Kudasai.
    
        Parameters:
        self (object - TokenCounter) : The TokenCounter object.

        Returns:
        num_tokens (int) The number of tokens in the text.
        min_cost (float) The minimum cost of translating the text.
        model (string) The model used to translate the text.

        """

        allowed_models = [
            "gpt-3.5-turbo",
            "gpt-4",
            "gpt-3.5-turbo-0301",
            "gpt-4-0314",
            "gpt-4-32k-0314",
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k-0613",
            "gpt-3.5-turbo-1106",
            "gpt-4-0613",
            "gpt-4-32k-0613",
            "gpt-4-1106-preview"
        ]

        assert model in allowed_models, f"""Kudasai does not support : {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""

        if(price_case is None):

            if(model == "gpt-3.5-turbo"):
                print("Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-1106 as it is the most recent version of gpt-3.5-turbo.")
                return self.calculate_min_cost("gpt-3.5-turbo-1106", price_case=2)
            
            elif(model == "gpt-4"):
                print("Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-1106-preview as it is the most recent version of gpt-4.")
                return self.calculate_min_cost("gpt-4-1106-preview", price_case=4)
            
            elif(model == "gpt-3.5-turbo-0613"):
                print("Warning: gpt-3.5-turbo-0613 is considered depreciated by openai as of November 6, 2023 and could be shutdown as early as June 13, 2024. Consider switching to gpt-3.5-turbo-1106.")
                return self.calculate_min_cost(model, price_case=1)

            elif(model == "gpt-3.5-turbo-0301"):
                print("Warning: gpt-3.5-turbo-0301 is considered depreciated by openai as of June 13, 2023 and could be shutdown as early as June 13, 2024. Consider switching to gpt-3.5-turbo-1106 unless you are specifically trying to break the filter.")
                return self.calculate_min_cost(model, price_case=1)
            
            elif(model == "gpt-3.5-turbo-1106"):
                return self.calculate_min_cost(model, price_case=2)
            
            elif(model == "gpt-3.5-turbo-16k-0613"):
                print("Warning: gpt-3.5-turbo-16k-0613 is considered depreciated by openai as of November 6, 2023 and could be shutdown as early as June 13, 2024. Consider switching to gpt-3.5-turbo-1106.")
                return self.calculate_min_cost(model, price_case=3)
            
            elif(model == "gpt-4-1106-preview"):
                return self.calculate_min_cost(model, price_case=4)
            
            elif(model == "gpt-4-0314"):
                print("Warning: gpt-4-0314 is considered depreciated by openai as of June 13, 2023 and could be shutdown as early as June 13, 2024. Consider switching to gpt-4-0613.")
                return self.calculate_min_cost(model, price_case=5)
            
            elif(model == "gpt-4-0613"):
                return self.calculate_min_cost(model, price_case=5)
            
            elif(model == "gpt-4-32k-0314"):
                print("Warning: gpt-4-32k-0314 is considered depreciated by openai as of June 13, 2023 and could be shutdown as early as June 13, 2024. Consider switching to gpt-4-32k-0613.")
                return self.calculate_min_cost(model, price_case=6)
            
            elif(model == "gpt-4-32k-0613"):
                return self.calculate_min_cost(model, price_case=6)
            
        else:
            encoding = tiktoken.encoding_for_model(model)

            cost_per_thousand_input_tokens = 0
            cost_per_thousand_output_tokens = 0

            ## gpt-3.5-turbo-0301
            ## gpt-3.5-turbo-0613
            if(price_case == 1):
                cost_per_thousand_input_tokens = 0.0015
                cost_per_thousand_output_tokens = 0.0020

            ## gpt-3.5-turbo-1106
            elif(price_case == 2):
                cost_per_thousand_input_tokens = 0.0010
                cost_per_thousand_output_tokens = 0.0020

            ## gpt-3.5-turbo-16k-0613
            elif(price_case == 3):
                cost_per_thousand_input_tokens = 0.0030
                cost_per_thousand_output_tokens = 0.0040

            ## gpt-4-1106-preview
            elif(price_case == 4):
                cost_per_thousand_input_tokens = 0.01
                cost_per_thousand_output_tokens = 0.03

            ## gpt-4-0314
            ## gpt-4-0613
            elif(price_case == 5):
                cost_per_thousand_input_tokens = 0.03
                cost_per_thousand_output_tokens = 0.06

            ## gpt-4-32k-0314
            ## gpt-4-32k-0613
            elif(price_case == 6):
                cost_per_thousand_input_tokens = 0.06
                cost_per_thousand_output_tokens = 0.012

            num_tokens = len(encoding.encode(self.text))

            min_cost_for_input = round((float(num_tokens) / 1000.00) * cost_per_thousand_input_tokens, 5)
            min_cost_for_output = round((float(num_tokens) / 1000.00) * cost_per_thousand_output_tokens, 5)

            min_cost = round(min_cost_for_input + min_cost_for_output, 5)

            return num_tokens, min_cost, model
        
        raise Exception("An unknown error occurred.")

##-------------------start-of-estimate_cost()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def estimate_cost(self, text_file:str) -> None:

        """

        Counts the number of tokens in a text file.

        Parameters:
        self (object - TokenCounter) : The TokenCounter object.
        text_file (string)  : The path to the text file.
        
        """


        with open(text_file, 'r', encoding='utf-8') as file: 
            self.text = file.read()

        self.MODEL = input("Please enter model : ")

        num_tokens, min_cost, self.MODEL = self.calculate_min_cost(self.MODEL)
        num_characters = self.count_characters()

        print("This is an estimate of the cost of translating a text using Kudasai. The actual cost may be higher or lower depending on the model used and the number of tokens in the text.\n")
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
