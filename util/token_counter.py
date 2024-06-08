## built-in libraries
from pathlib import Path

import sys
import os

## Calculates the path to the modules directory and add it to sys.path
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent

## Add the parent directory to sys.path so 'modules' can be found
sys.path.append(str(parent_dir))

## third-party libraries
from easytl import EasyTL

## custom modules
from modules.common.toolkit import Toolkit

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
        self.service = "openai" if "gpt" in self.MODEL else "gemini"

        text_to_translate = [line for line in self.text.splitlines()]

        num_tokens, min_cost, self.MODEL = EasyTL.calculate_cost(text=text_to_translate, service=self.service, model=self.MODEL)

        print("\nNote that the cost estimate is not always accurate, and may be higher than the actual cost. However cost calculation now includes output tokens.\n")

        if(self.service == "gemini"):
            print(f"As of Kudasai {Toolkit.CURRENT_VERSION}, Gemini Pro 1.0 is free to use under 15 requests per minute, Gemini Pro 1.5 is free to use under 2 requests per minute.\nIt is up to you to set these in the settings json.\nIt is currently unknown whether the ultra model parameter is connecting to the actual ultra model and not a pro one. As it works, but does not appear on any documentation.\n")
        
        print("Estimated number of tokens : " + str(num_tokens))
        print("Estimated minimum cost : " + str(min_cost) + " USD")

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
