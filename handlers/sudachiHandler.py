## built-in imports
from __future__ import annotations ## used for cheating the circular import issue that occurs when i need to type check some things
from enum import Enum
from zipfile import ZipFile
from tempfile import NamedTemporaryFile
from time import sleep

import os
import csv
import subprocess
import typing
import json

## third-party imports
from spacy.tokens import Doc
from spacy.language import Language

from sudachipy import tokenizer
from sudachipy import dictionary

import spacy

## custom modules
if(typing.TYPE_CHECKING): ## used for cheating the circular import issue that occurs when i need to type check some things
    from modules.preloader import preloader

from handlers.katakanaHandler import katakanaHandler





##--------------------start-of-sudachiHandler------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class CustomSudachiTokenizer():

    """
    
    Our custom tokenizer for SudachiPy.

    """

    ## Subset of the Unidic part of speech tags, as listed:
    ## https://gist.github.com/masayu-a/e3eee0637c07d4019ec9
    class PartOfSpeech(str, Enum): 
        NOUN = "名詞"
        PROPER_NOUN = "固有名詞"
        PUNCTUATION = "補助記号"
        WHITESPACE = "空白"

    class Word(typing.NamedTuple):
        text:str
        part_of_speech:str

##--------------------start-of-__init__()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, nlp:Language, temp_config:str, katakana_handler:katakanaHandler) -> None:

        """

        Initializes the custom tokenizer.
        
        Parameters:
        nlp (object - Language) : the language object.
        sudachi_dict_path (str) : path to the sudachi dictionary.

        Returns:
        None.
        
        """

        self.vocab = nlp.vocab
        self.mode = tokenizer.Tokenizer.SplitMode.A
        self.sudachi = dictionary.Dictionary(config_path=temp_config).create(mode=self.mode)

        self.katakana_handler = katakana_handler

    def __call__(self, text:str):
        # Tokenize the text into words and parts of speech
        words = self.tokenize(text)
        # Create a list of token texts
        words_texts = [word.text for word in words]
        # Create a Doc object from the list of token texts and the original text
        doc = Doc(self.vocab, words=words_texts, spaces=[False]*len(words_texts))
        return doc

##--------------------start-of-__call__()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def tokenize(self, text:str) -> typing.List[Word]:
        word_list = []
        tagged_words = self.sudachi.tokenize(text)

        for word in tagged_words:
            word_text = word.surface()

            # TODO: Add an explanation of the part_of_speech_tuple tuple
            part_of_speech_tuple = word.part_of_speech()
            part_of_speech = part_of_speech_tuple[0]

            class PartOfSpeech(str, Enum): 
                NOUN = "名詞"
                PROPER_NOUN = "固有名詞"
                PUNCTUATION = "補助記号"
                WHITESPACE = "空白"

            class Word(typing.NamedTuple):
                text:str
                part_of_speech:str

            # Some tokenizers (Sudachi, Nagisa) tend to mistag long strings of punctuation
                PUNCTUATION = "補助記号"
                WHITESPACE = "空白"

            # Some tokenizers (Sudachi, Nagisa) tend to mistag long
            # strings of punctuation
            if part_of_speech != PartOfSpeech.PUNCTUATION and \
               self.katakana_handler.is_punctuation(word_text):
               part_of_speech = PartOfSpeech.PUNCTUATION
            # Prefer the more specific proper noun pos tag when available,
            # as it enables more accurate single kanji replacement
            elif part_of_speech_tuple[0] == PartOfSpeech.NOUN and \
                 part_of_speech_tuple[1] == PartOfSpeech.PROPER_NOUN:
                part_of_speech = part_of_speech_tuple[1]
            word_list.append(Word(word_text, part_of_speech))
        return word_list
    
##--------------------start-of-sudachiHandler------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class sudachiHandler:

    """
    
    Deals with the custom sudachi tokenizer we create every runtime.

    """
##--------------------start-of-__init__()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, replacement_json:dict, preloader:preloader, inc_katakana_handler:katakanaHandler) -> None:

        """
        
        Parameters:
        lib_dir (str) : path to the library directory.

        Returns:
        None.

        """

        self.replacement_json = replacement_json
    
        self.preloader = preloader

        self.katakana_handler = inc_katakana_handler

        if(os.path.exists(self.preloader.sudachi_system_dic) == False):

            with ZipFile(self.preloader.system_zip, 'r') as zip_ref:
                zip_ref.extractall(self.preloader.dic_lib)

            os.remove(self.preloader.system_zip)

            sleep(.1)
                
##--------------------start-of-prepare_sudachi()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def prepare_sudachi(self, name_of_replacement_json:str) -> None:

        """
        
        Prepares the sudachi tokenizer.

        Parameters:
        self (object - sudachiHandler) : the sudachiHandler object.
        name_of_replacement_json (str) : the name of the replacement JSON file.

        Returns:
        None.

        """

        csv_path, dic_path = self.generate_sudachi_dict_csv(name_of_replacement_json)

        self.compiled_dict_path = self.compile_sudachi_dict(csv_path, dic_path)

##--------------------start-of-update_sudachi_config()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def update_sudachi_config(self):

        """
        
        Updates the sudachi config file.

        Parameters:
        self (object - sudachiHandler) : the sudachiHandler object.

        Returns:
        None.

        """


        with open(self.preloader.sudachi_config_json, 'r', encoding='utf-8') as f:
            config = json.load(f)

        ## Update the system dictionary path
        config['systemDict'] = self.preloader.sudachi_system_dic


        ## Save the updated config
        with open(self.preloader.sudachi_config_json, 'w', encoding='utf-8') as file:
            json.dump(config, file, ensure_ascii=False, indent=4)

##--------------------start-of-generate_sudachi_dict_csv()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def generate_sudachi_dict_csv(self, name:str) -> typing.Tuple[str,str]:

        """
        
        Generates a CSV file for the custom sudachi tokenizer.

        Parameters:
        self (object - sudachiHandler) : the sudachiHandler object.
        name (str) : the name of the CSV file.

        Returns:
        output_file_path (str) : the path to the CSV file.

        """
        
        ## Define the output path for the CSV file
        csv_output_file_path = os.path.join(self.preloader.dic_lib, f"{name}_sudachi_dict.csv")
        dict_output_path = os.path.join(self.preloader.dic_lib, f"{name}_sudachi_dict.dic")
        
        word_id = 0

        # Open the file for writing
        with open(csv_output_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            for name_key in ['single_names', 'full_names']:

                for en_name, jp_names in self.replacement_json[name_key].items():

                    ## jp_names can be a list or a single string
                    if(not isinstance(jp_names, list)):
                        jp_names = [jp_names]

                    for jp_name in jp_names:

                        if(not self.katakana_handler.is_katakana_only(jp_name)):
                            continue

                        ### Write a row to the CSV file
                        ## Here, we're using dummy values for the POS IDs and cost, I.E. I stole them from WCT
                        
                        word_id += 1
                        writer.writerow([
                            jp_name,  # Surface Form (for Trie)
                            4786,     # Left Connection ID
                            4786,     # Right Connection ID
                            5000,     # Cost
                            jp_name,  # Surface Form (for Analysis Result Display)
                            '名詞',   # Part-of-Speech 1
                            '固有名詞', # Part-of-Speech 2
                            '一般',   # Part-of-Speech 3
                            '*',      # Part-of-Speech 4
                            '*',      # Conjugation Type
                            '*',      # Conjugation Form
                            jp_name,  # Reading (should be Katakana)
                            jp_name,  # Normalized Form
                            word_id,  # Dictionary Form ID
                            '*',      # Split Type
                            '*',      # A Unit Split Information
                            '*',      # B Unit Split Information
                            '*'       # Unused
                        ])


        print(f"Sudachi dictionary CSV written to: {csv_output_file_path}")

        return csv_output_file_path, dict_output_path
    
##--------------------start-of-compile_sudachi_dict()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    def compile_sudachi_dict(self, csv_file_path:str, dict_output_path:str) -> str:

        """

        Compiles the Sudachi dictionary from the CSV and returns the path to the compiled dictionary.

        Parameters:
        csv_file_path (str): The path to the CSV file.
        dict_output_path (str): The path where the compiled dictionary should be saved.

        Returns:
        str: The path to the compiled Sudachi dictionary.

        """

        if(os.path.exists(dict_output_path)):
            os.remove(dict_output_path)

        subprocess.run([
            'sudachipy', 'ubuild',
            '-o', dict_output_path,
            '-s', self.preloader.sudachi_system_dic,
            csv_file_path
        ], check=True)

        print(f"Sudachi dictionary compiled to: {dict_output_path}")

        return dict_output_path

##--------------------start-of-assemble_nlp_object()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def assemble_nlp_object(self) -> Language:
        
        """
        
        Assembles the nlp object.

        Parameters:
        self (object - sudachiHandler) : the sudachiHandler object.

        Returns:
        nlp (object - Language) : the nlp object.


        """

        nlp = spacy.load("ja_core_news_lg")
        temp_path = self.generate_temporary_sudachi_config_file()
        nlp.tokenizer = CustomSudachiTokenizer(nlp, temp_path, self.katakana_handler)
        self._delete_temporary_sudachi_config_file(temp_path)  # Ensure this is called to clean up
        return nlp

        

    def generate_temporary_sudachi_config_file(self):

        sudachi_config = {
            "userDict": [self.compiled_dict_path],
            "oovProviderPlugin": [
                {
                    "class": "com.worksap.nlp.sudachi.MeCabOovPlugin",
                    "charDef": "char.def",
                    "unkDef": "unk.def"
                },
                {
                    "class": "com.worksap.nlp.sudachi.SimpleOovPlugin",
                    "oovPOS": ["補助記号", "一般", "*", "*", "*", "*"],
                    "leftId": 5968,
                    "rightId": 5968,
                    "cost": 3857
                }
            ]
        }

        with NamedTemporaryFile(mode="w", delete=False) as config_file:
            config_file.write(json.dumps(sudachi_config))

        config_path = config_file.name

        return config_path
    

    def _delete_temporary_sudachi_config_file(self, filepath):
        if os.path.exists(filepath):
            os.remove(filepath)
