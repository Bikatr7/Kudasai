## built-in libraries
from pathlib import Path

import sys
import os

## Calculates the path to the modules directory and add it to sys.path
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent

## Add the parent directory to sys.path so 'modules' can be found
sys.path.append(str(parent_dir))

## custom modules
from modules.common.toolkit import Toolkit
from models.kijiku import Kijiku

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

        ## lazy workaround for now
        Kijiku.text_to_translate = [line for line in self.text.splitlines()]

        num_tokens, min_cost, self.MODEL = Kijiku.estimate_cost(self.MODEL)
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
