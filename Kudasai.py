## built in modules
import os
import itertools 
import time
import enum
import typing
import sys

## third party modules
import spacy
import json

## custom modules
from Models.Kaiseki import Kaiseki 
from Models.Kijiku import Kijiku
from Modules import toolkit 


##-------------------start-of-Kudasai---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Kudasai:

    """

    Kudasai class is the main class for the Kudasai program. It contains all the functions and variables needed to run the base preprocessor.\n
    
    """
##-------------------start-of-__init__()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, from_gui:bool) -> None: 

        """
        
        Constructor for Kudasai class. Takes in the input file, replacement json file, and if it is being run from the GUI or not.

        Parameters:\n
        self (object - Kudasai) : the Kudasai object.\n
        from_gui (boolean) : indicates whether or not the request is from the gui.\n

        Returns:\n
        None\n

        """

        ## represents a japanese name along with its equivalent english name
        self.Name = Name

        ## large model for japanese NER (named entity recognition)
        self.ner = spacy.load("ja_core_news_lg") 

        ## filters out single kanji or uses a specific function to deal with it when replacing names
        self.SINGLE_KANJI_FILTER = True 

        ## determines if the user is connected to the internet or not
        self.connection = False 

        ## determines if Kudasai is being run from the GUI or not
        self.from_GUI = from_gui

        ## how japanese names are separated in the japanese text
        self.JAPANESE_NAME_SEPARATORS = ["・", ""] 

        ## log for errors
        self.error_text = [] 

        ## holds the japanese text from the input file
        self.japanese_text = '' 

        ## results of the replacement process, not the japanese text, but like a log
        self.replacement_text = '' 

        ## dictionary that holds the replacement json file
        self.replacement_json = dict()

        ## total number of replacements made
        self.total_replacements = 0


##-------------------start-of-setup()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    def setup(self, input_file, replacement_json) -> None:

        """
        
        Sets up the Kudasai object, loads the input file and the replacement json file.\n
        
        Parameters:\n
        self (object - Kudasai) : the Kudasai object.\n
        input_file (str) : The path to the input file to be processed.\n
        replacement_json (str) : The path to the replacement json file.\n

        Returns:\n
        None\n

        """

        with open(input_file, 'r', encoding='utf-8') as file: 
            self.japanese_text = file.read()
        
        try:

            with open(replacement_json, 'r', encoding='utf-8') as file: 
                self.replacement_json = json.load(file) 
    
        except:

            print("The second path you provided is either invalid, not a JSON file, or the JSON file has an error.\n")
            toolkit.pause_console()

            exit()

##-------------------start-of-write_results()-------------------------------------------------------------------------------------------------------------------------------------
        
    def write_results(self) -> None: 

        """

        writes the results of Kudasai to the output files\n

        Parameters:\n
        self (object - Kudasai) : the Kudasai object.\n

        Returns:\n
        None\n

        """

        with open(self.preprocess_path, 'w+', encoding='utf-8') as file: 
            file.write(self.japanese_text) 

        with open(self.output_path, 'w+', encoding='utf-8') as file:
            file.write(self.replacement_text) 

        if(not os.path.exists(self.debug_path)):
            with open(self.debug_path, 'w+', encoding='utf-8') as file:
                pass

        if(not os.path.exists(self.je_path)):
            with open(self.je_path, 'w+', encoding='utf-8') as file:
                pass

        if(not os.path.exists(self.translated_path)):
            with open(self.translated_path, 'w+', encoding='utf-8') as file:
                pass

        with open(self.error_path, 'w+', encoding='utf-8') as file: 
            file.writelines(self.error_text) 

##-------------------start-of-determine_translation_automation()-------------------------------------------------------------------------------------------------------------------------------------

    def determine_translation_automation(self) -> None:

        """

        determines which translation module the user wants to use and calls it\n

        Parameters:\n
        preprocessPath (string) : path to where the preprocessed text was stored\n

        Returns:\n
        None\n

        """

        toolkit.clear_console()

        print("Please choose an auto translation model")
        print("\n1.Kaiseki - DeepL based line by line translation (Not very accurate by itself) (Free if using trial)")
        print("\n2.Kijiku - OpenAI based batch translator (Very accurate) (Price depends on model)")
        print("\n3.Exit\n")
        
        mode = input()

        if(mode == "1"):
            self.run_kaiseki()
        
        elif(mode == "2"):
            self.run_kijiku()

        else:
            exit()

##-------------------start-of-run_kaiseki()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def run_kaiseki(self) -> None:

        """

        runs the kaiseki module for auto translation\n

        Parameters:\n
        self (object - Kudasai) : the Kudasai object.\n

        Returns:\n
        None\n

        """

        toolkit.clear_console()
        
        print("Commencing Automated Translation\n")

        time.sleep(1)

        kaiseki_client = Kaiseki(self.config_dir,self.script_dir,from_gui=False)

        kaiseki_client.translate(self.preprocess_path)

##-------------------start-of-run_kijiku()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def run_kijiku(self) -> None:
        
        """
        
        runs the kijiku module for auto translation\n

        Parameters:\n
        self (object - Kudasai) : the Kudasai object.\n

        Returns:\n
        None\n

        """

        toolkit.clear_console()

        kijiku_client = Kijiku(self.config_dir,self.script_dir,from_gui=False)

        print("Commencing Automated Translation\n")

        time.sleep(2)

        kijiku_client.translate(self.preprocess_path)

##-------------------start-of-main()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

if(__name__ == '__main__'): ## checks sys arguments and if less than three or called outside cmd prints usage statement

    if(len(sys.argv) < 3): 

        print(f'Usage: {sys.argv[0]} input_txt_file replacement.json\n\nSee README.md for more information.\n') 
        
        toolkit.pause_console()
        exit() 

    toolkit.clear_console() 

    os.system("title " + "Kudasai") 

    kudasai_client = Kudasai(from_gui=False) ## creates Kudasai object, passing in input file and replacement json file, and if it is being run from the GUI or not

    kudasai_client.preprocess(sys.argv[1], sys.argv[2]) ## preprocesses the text

    kudasai_client.determine_translation_automation() ## determines which translation module the user wants to use and calls it