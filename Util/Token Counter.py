## built-in modules
import sys
import os
import time
import typing
import msvcrt

## third-party modules
import tiktoken

class TokenCounter:

    """
    
    Util script for counting tokens, characters, and estimating cost of translating a text.\n

    """

##-------------------start-of-__init__()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self) -> None:

        '''

        Constructor for TokenCounter class.\n

        Parameters:\n
        None.\n

        Returns:\n
        None.\n

        '''

        os.system("title " + "Token Counter")

        self.MODEL = None

##-------------------start-of-count_characters()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def count_characters(self) -> int:

        '''

        Counts the number of characters in a string.\n
    
        Parameters:\n
        self (object - TokenCounter) : the TokenCounter object.\n
        text (str) : the text that will be counting characters for.\n

        Returns:\n
        num_characters (int) the number of characters in the text.\n

        '''

        self.clear_console()

        num_characters = len(self.text)

        return num_characters

##-------------------start-of-estimate_cost()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def estimate_cost(self) -> typing.Tuple[int, float]:

        '''

        Attempts to estimate cost.\n
    
        Parameters:\n
        self (object - TokenCounter) : the TokenCounter object.\n

        Returns:\n
        num_tokens (int) the number of tokens in the text.\n
        min_cost (float) the minimum cost of translating the text.\n

        '''
        
        try:
            encoding = tiktoken.encoding_for_model(self.MODEL)  # type: ignore
            
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")

        if(self.MODEL == "gpt-3.5-turbo"):
            print("Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
            time.sleep(4)
            self.MODEL="gpt-3.5-turbo-0613"
            return self.estimate_cost()
        
        elif(self.MODEL == "gpt-3.5-turbo-0301"):
            print("Warning: gpt-3.5-turbo-0301 is outdated. gpt-3.5-turbo-0301's support ended September 13, Returning num tokens assuming gpt-3.5-turbo-0613.")
            time.sleep(4)
            self.MODEL="gpt-3.5-turbo-0613"
            return self.estimate_cost()

        elif(self.MODEL == "gpt-4"):
            print("Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-0613.")
            time.sleep(4)
            self.MODEL="gpt-4-0613"
            return self.estimate_cost()
        
        elif(self.MODEL == "gpt-4-0314"):
            print("Warning: gpt-4-0314 is outdated. gpt-4-0314's support ended September 13, Returning num tokens assuming gpt-4-0613.")
            time.sleep(4)
            self.MODEL="gpt-4-0613"
            return self.estimate_cost()
        
        elif(self.MODEL == "gpt-3.5-turbo-0613"):
            cost_per_thousand_tokens = 0.0015


        elif(self.MODEL == "gpt-4-0613"):
            cost_per_thousand_tokens = 0.06

        else:
            raise NotImplementedError(f"""Kudasai does not support : {self.MODEL}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
        
        num_tokens = len(encoding.encode(self.text))

        min_cost = round((float(num_tokens) / 1000.00) * cost_per_thousand_tokens, 5)

        return num_tokens, min_cost

##-------------------start-of-count_tokens()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def count_tokens(self, text_file:str) -> None:

        '''

        Counts the number of tokens in a text file.\n

        Parameters:\n
        self (object - TokenCounter) : the TokenCounter object.\n
        text_file (string) the text file that will be counting tokens for.\n

        Returns:\n
        None.\n
        
        '''


        with open(text_file, 'r', encoding='utf-8') as file: 
            self.text = file.read()

        self.MODEL = input("Please enter model : ")

        num_tokens, min_cost = self.estimate_cost()
        num_characters = self.count_characters()

        print("Estimated Number of Tokens in Text : " + str(num_tokens))
        print("Estimated Minimum Cost of Translation : " + str(min_cost))
        print("Number of Characters in Text : " + str(num_characters) + "\n")

        self.pause_console()

##-------------------start-of-clear_console()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def clear_console(self) -> None:

        """

        clears the console\n

        Parameters:\n
        self (object - TokenCounter) : the TokenCounter object.\n

        Returns:\n
        None\n

        """

        os.system('cls' if os.name == 'nt' else 'clear')

##-------------------start-of-pause_console()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def pause_console(self, message:str="Press any key to continue...") -> None:

        """

        Pauses the console.\n

        Parameters:\n
        self (object - TokenCounter) : the TokenCounter object.\n
        message (str | optional) : the message that will be displayed when the console is paused.\n

        Returns:\n
        None\n

        """

        print(message)  ## Print the custom message
        
        if(os.name == 'nt'):  ## Windows
            
            msvcrt.getch() 

        else:  ## Linux, No idea if any of this works lmao

            import termios

            ## Save terminal settings
            old_settings = termios.tcgetattr(0)

            try:
                new_settings = termios.tcgetattr(0)
                new_settings[3] = new_settings[3] & ~termios.ICANON
                termios.tcsetattr(0, termios.TCSANOW, new_settings)
                os.read(0, 1)  ## Wait for any key press

            finally:

                termios.tcsetattr(0, termios.TCSANOW, old_settings)

##-------------------start-of-sub_main()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

client = TokenCounter()

## checks sys arguments and if less than 2 or called outside cmd prints usage statement
if(__name__ == '__main__'): 

    if(len(sys.argv) < 2): 

        print(f'\nUsage: {sys.argv[0]} input_txt_file\n') 
        
        client.pause_console()
        exit() 

    client.clear_console()

    client.count_tokens(sys.argv[1])