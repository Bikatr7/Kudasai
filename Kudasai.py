## built in modules
import os
import time
import sys

## third party modules

import json

## custom modules
from Models.Kaiseki import Kaiseki 
from Models.Kijiku import Kijiku
from Models.Kairyou import Kairyou
from Modules.preloader import preloader


##-------------------start-of-Kudasai---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Kudasai:

    """

    Kudasai class is the main class for the Kudasai program. It handles all the stuff except for the gui.\n
    
    """
##-------------------start-of-__init__()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self) -> None: 

        """
        
        Constructor for Kudasai class.

        Parameters:\n
        self (object - Kudasai) : the Kudasai object.\n

        Returns:\n
        None\n

        """

        os.system("title " + "Kudasai")

        self.preloader = preloader()

        self.kairyou_client = None

        self.kaiseki_client = None

        self.kijiku_client = None
 


##-------------------start-of-setup()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    def setup_kairyou(self, input_file, replacement_json) -> None:

        """
        
        If the user is running the CLI version of Kudasai, this function is called to setup the text to be processed and the replacement json file.\n
        
        Parameters:\n
        self (object - Kudasai) : the Kudasai object.\n
        input_file (str) : The path to the input file to be processed.\n
        replacement_json (str) : The path to the replacement json file.\n

        Returns:\n
        None\n

        """

        try:

            with open(replacement_json, 'r', encoding='utf-8') as file: 
                replacement_json = json.load(file) 
    
        except:

            print("The second path you provided is either invalid, not a JSON file, or the JSON file has an error.\n")
            self.preloader.toolkit.pause_console()

            exit()


        with open(input_file, 'r', encoding='utf-8') as file: 
            japanese_text = file.read()
        
        self.kairyou_client = Kairyou(replacement_json, japanese_text)

##-------------------start-of-run_kudasai_cli()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def run_kudasai_cli(self) -> None:

        """
        
        If the user is running the CLI version of Kudasai, this function is called to run the program.\n
        
        Parameters:\n
        self (object - Kudasai) : the Kudasai object.\n

        Returns:\n
        None\n

        """

##-------------------start-of-main()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

kudasai_client = Kudasai()

## determines if we will run the Kudasai CLI or the Kudasai Console
if(__name__ == '__main__'):

    ## to be implemented later, for now we will just run the CLI version
    if(len(sys.argv) < 3):
        pass

    else:

        kudasai_client.setup_kairyou(sys.argv[1], sys.argv[2])

        kudasai_client.run_kudasai_cli()
