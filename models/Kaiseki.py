## built-in libraries
from __future__ import annotations ## used for cheating the circular import issue that occurs when i need to type check some things

import string
import typing
import os
import time
import re
import base64
import time

## third party modules
import deepl

## custom modules
if(typing.TYPE_CHECKING): ## used for cheating the circular import issue that occurs when i need to type check some things
    from modules.preloader import preloader

##-------------------start-of-Kaiseki--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Kaiseki:

    """

    Kaiseki is a secondary class that is used to interact with the deepl API and translate Japanese text sentence by sentence.\n

    Kaiseki is considered Inferior to Kijiku, please consider using Kijiku instead.\n
    
    """

##-------------------start-of-__init__()--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, inc_text_to_translate:str, inc_preloader:preloader) -> None:

        """

        Constructor for the Kaiseki Class.\n

        Parameters:\n
        inc_text_to_translate (str) : the path to the text file to translate.\n
        inc_preloader (object - preloader) : the preloader object.\n

        Returns:\n
        None.\n

        """

        self.preloader = inc_preloader

        ##---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        ## the text to translate
        self.text_to_translate =  [line for line in inc_text_to_translate.split('\n')]

        ## the translated text
        self.translated_text = []

        ## the text for j-e checking
        self.je_check_text = []

        ## the text for errors that occur during translation (if any)
        self.error_text = []

        ## the print result for the translation
        self.translation_print_result = ""
        
        ##---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        ## parts of the self.current_sentence
        self.sentence_parts = []

        ## if the self.current_sentence contains special punctuation
        self.special_punctuation = [] ## [0] = "" [1] = ~ [2] = '' in self.current_sentence but not entire self.current_sentence [3] = '' but entire self.current_sentence [3] if () in self.current_sentence

        ## the current self.current_sentence being translated
        self.current_sentence = ""

        ## the current translated self.current_sentence
        self.translated_sentence = ""

        ##---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        ## the path to the deepl api key
        self.deepl_api_key_path = os.path.join(self.preloader.file_handler.config_dir, "DeeplApiKey.txt")
        
##-------------------start-of-translate()--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def translate(self):

        """

        Translates the text given to the Kaiseki object.\n

        Parameters:\n
        self (object - Kaiseki) : the Kaiseki object.\n

        Returns:\n
        None.\n

        """

        self.time_start = time.time() ## start time

        try:

            self.initialize() ## initialize the Kaiseki object

            self.time_start = time.time() ## offset time

            self.commence_translation() ## commence the translation

        except Exception as e:
            
            self.translation_print_result += "An error has occurred, outputting results so far..."

            self.preloader.file_handler.handle_critical_exception(e)

        finally:

            self.time_end = time.time() ## end time

            self.assemble_results() ## assemble the results

##-------------------start-of-initialize()--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def initialize(self) -> None:
        
        """

        Initializes the Kaiseki class by getting the api key and creating the translator object.\n

        Parameters:\n
        self (object - Kaiseki) : the Kaiseki object.\n

        Returns:\n
        None.\n

        """
        
        ## get saved api key if exists
        try:

            with open(self.deepl_api_key_path, 'r', encoding='utf-8') as file:
                api_key = base64.b64decode((file.read()).encode('utf-8')).decode('utf-8')

            self.translator = deepl.Translator(api_key)

            print("Used saved api key in " + self.deepl_api_key_path)
            self.preloader.file_handler.logger.log_action("Used saved api key in " + self.deepl_api_key_path)

        ## else try to get api key manually
        except Exception as e: 

            api_key = input("DO NOT DELETE YOUR COPY OF THE API KEY\n\nPlease enter the deepL api key you have : ")

            ## if valid save the api key
            try: 

                self.translator = deepl.Translator(api_key)

                time.sleep(.1)
                    
                self.preloader.file_handler.standard_overwrite_file(self.deepl_api_key_path, base64.b64encode(api_key.encode('utf-8')).decode('utf-8'))

                time.sleep(.1)
                
            ## if invalid key exit
            except deepl.exceptions.AuthorizationException: 
                    
                self.preloader.toolkit.clear_console()
                    
                print("Authorization error with creating translator object, please double check your api key as it appears to be incorrect.\nKaiseki will now exit.\n")
                
                self.preloader.toolkit.pause_console()
                    
                raise e

            ## other error, alert user and raise it
            except Exception as e: 
                
                self.preloader.toolkit.clear_console()
                    
                print("Unknown error with creating translator object, The error is as follows " + str(e)  + "\nKaiseki will now exit.\n")
                
                self.preloader.toolkit.pause_console()

                raise e

        self.preloader.toolkit.clear_console()

##-------------------start-of-commence_translation()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def commence_translation(self) -> None:

        """
        
        Commences the translation process using all the functions in the Kaiseki class.\n

        Parameters:\n
        self (object - Kaiseki) : the Kaiseki object.\n

        Returns:\n 
        None.\n

        """

        i = 0 

        while(i < len(self.text_to_translate)):
                
            self.current_sentence = self.text_to_translate[i]
            
            self.preloader.file_handler.logger.log_action("Initial Sentence : " + self.current_sentence)

            if(any(char in self.current_sentence for char in ["▼", "△", "◇"])):
                self.translated_text.append(self.current_sentence + '\n')
                self.preloader.file_handler.logger.log_action("Sentence : " + self.current_sentence + ", Sentence is a pov change... leaving intact.\n")

            elif("part" in self.current_sentence.lower() or all(char in ["１","２","３","４","５","６","７","８","９", " "] for char in self.current_sentence) and not all(char in [" "] for char in self.current_sentence) and self.current_sentence != '"..."' and self.current_sentence != "..."):
                self.translated_text.append(self.current_sentence + '\n') 
                self.preloader.file_handler.logger.log_action("Sentence : " + self.current_sentence + ", Sentence is part marker... leaving intact.\n")

            elif bool(re.match(r'^[\W_\s\n-]+$', self.current_sentence)) and not any(char in self.current_sentence for char in ["」", "「", "«", "»"]):
                self.preloader.file_handler.logger.log_action("Sentence : " + self.current_sentence + ", Sentence is punctuation... skipping.\n")
                self.translated_text.append(self.current_sentence + "\n")

            elif(bool(re.match(r'^[A-Za-z0-9\s\.,\'\?!]+\n*$', self.current_sentence))):
                self.preloader.file_handler.logger.log_action("Sentence : " + self.current_sentence + ", Sentence is english... skipping translation.\n")
                self.translated_text.append(self.current_sentence + "\n")

            elif(len(self.current_sentence) == 0 or self.current_sentence.isspace() == True):
                self.preloader.file_handler.logger.log_action("Sentence is empty... skipping translation.\n")
                self.translated_text.append(self.current_sentence + "\n") 

            else:
        
                self.separate_sentence()

                self.translate_sentence()

                ## this is for adding a period if it's missing 
                if(len(self.translated_text[i]) > 0 and self.translated_text[i] != "" and self.translated_text[i][-2] not in string.punctuation and self.sentence_punctuation[-1] == None): 
                    self.translated_text[i] = self.translated_text[i] + "."
                
                ## re-adds quotes
                if(self.special_punctuation[0] == True): 
                    self.translated_text[i] =  '"' + self.translated_text[i] + '"'

                ## replaces quotes because deepL messes up quotes
                elif('"' in self.translated_text[i]): 
                    self.translated_text[i] = self.translated_text[i].replace('"',"'")

                ## re-adds single quotes
                if(self.special_punctuation[3] == True): 
                    self.translated_text[i] =  "'" + self.translated_text[i] + "'"

                ## re-adds parentheses
                if(self.special_punctuation[4] == True): 
                    self.translated_text[i] =  "(" + self.translated_text[i] + ")"

                self.translated_text[i] += "\n"

                self.preloader.file_handler.logger.log_action("Translated and Reassembled Sentence : " + self.translated_text[i])

                self.je_check_text.append(str(i+1) + ": " + self.current_sentence +  "\n   " +  self.translated_text[i] + "\n")
            
            i+=1
            
            self.preloader.toolkit.clear_console()
            
            print(str(i) + "/" + str(len(self.text_to_translate)) + " completed.")

##-------------------start-of-separate_sentence()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    def separate_sentence(self) -> None: 

        """

        This function separates the sentence into parts and punctuation.\n

        Parameters:\n
        self (object - Kaiseki) : The Kaiseki object.\n

        Returns:\n
        None.\n
        
        """

        ## resets variables for current_sentence
        self.sentence_parts = [] 
        self.sentence_punctuation = []
        self.special_punctuation = [False,False,False,False,False] 

        i = 0

        buildString = ""

        ## checks if quotes are in the sentence and removes them
        if('"' in self.current_sentence):
            self.current_sentence = self.current_sentence.replace('"', '')
            self.special_punctuation[0] = True

        ## checks if tildes are in the sentence
        if('~' in self.current_sentence):
            self.special_punctuation[1] = True

        ## checks if apostrophes are in the sentence but not at the beginning or end
        if(self.current_sentence.count("'") == 2 and (self.current_sentence[0] != "'" and self.current_sentence[-1] != "'")):
            self.special_punctuation[2] = True

        ## checks if apostrophes are in the sentence and removes them
        elif(self.current_sentence.count("'") == 2):
            self.special_punctuation[3] = True
            self.current_sentence = self.current_sentence.replace("'", "")

        ## checks if parentheses are in the sentence and removes them
        if("(" in self.current_sentence and ")" in self.current_sentence):
            self.special_punctuation[4] = True
            self.current_sentence= self.current_sentence.replace("(","")
            self.current_sentence= self.current_sentence.replace(")","")

        while(i < len(self.current_sentence)):
                
            if(self.current_sentence[i] in [".","!","?","-"]): 

                if(i+5 < len(self.current_sentence) and self.current_sentence[i:i+6] in ["......"]):

                    if(i+6 < len(self.current_sentence) and self.current_sentence[i:i+7] in ["......'"]):
                        buildString += "'"
                        i+=1

                    if(buildString != ""):
                        self.sentence_parts.append(buildString)

                    self.sentence_punctuation.append(self.current_sentence[i:i+6])
                    i+=5
                    buildString = ""
                    
                if(i+4 < len(self.current_sentence) and self.current_sentence[i:i+5] in [".....","...!?"]):

                    if(i+5 < len(self.current_sentence) and self.current_sentence[i:i+6] in [".....'","...!?'"]):
                        buildString += "'"
                        i+=1

                    if(buildString != ""):
                        self.sentence_parts.append(buildString)

                    self.sentence_punctuation.append(self.current_sentence[i:i+5])
                    i+=4
                    buildString = ""
                                            
                elif(i+3 < len(self.current_sentence) and self.current_sentence[i:i+4] in ["...!","...?","---.","....","!..."]):

                    if(i+4 < len(self.current_sentence) and self.current_sentence[i:i+5] in ["...!'","...?'","---.'","....'","!...'"]):
                        buildString += "'"
                        i+=1

                    if(buildString != ""):
                        self.sentence_parts.append(buildString)

                    self.sentence_punctuation.append(self.current_sentence[i:i+4])
                    i+=3
                    buildString = ""
                        
                elif(i+2 < len(self.current_sentence) and self.current_sentence[i:i+3] in ["---","..."]):

                    if(i+3 < len(self.current_sentence) and self.current_sentence[i:i+4] in ["---'","...'"]):
                        buildString += "'"
                        i+=1

                    if(buildString != ""):
                        self.sentence_parts.append(buildString)

                    self.sentence_punctuation.append(self.current_sentence[i:i+3])
                    i+=2
                    buildString = ""

                elif(i+1 < len(self.current_sentence) and self.current_sentence[i:i+2] == '!?'):

                    if(i+2 < len(self.current_sentence) and self.current_sentence[i:i+3] == "!?'"):
                        buildString += "'"
                        i+=1

                    if(buildString != ""):
                        self.sentence_parts.append(buildString)

                    self.sentence_punctuation.append(self.current_sentence[i:i+2])
                    i+=1
                    buildString = ""
                        
                ## if punctuation that was found is not a hyphen then just follow normal punctuation separation rules
                elif(self.current_sentence[i] != "-"):

                    if(i+1 < len(self.current_sentence) and self.current_sentence[i+1] == "'"):
                        buildString += "'"

                    if(buildString != ""):
                        self.sentence_parts.append(buildString)

                    self.sentence_punctuation.append(self.current_sentence[i])
                    buildString = ""

                ## if it is just a singular hyphen, do not consider it punctuation as they are used in honorifics
                else:
                    buildString += self.current_sentence[i]
            else:
                buildString += self.current_sentence[i] 

            i += 1
                
        ## if end of line, add none punctuation which means a period needs to be added later
        if(buildString): 
            self.sentence_parts.append(buildString)
            self.sentence_punctuation.append(None)

        self.preloader.file_handler.logger.log_action("Fragmented Sentence Parts " + str(self.sentence_parts))
        self.preloader.file_handler.logger.log_action("Sentence Punctuation " + str(self.sentence_punctuation))
        self.preloader.file_handler.logger.log_action("Does Sentence Have Special Punctuation : " + str(self.special_punctuation))

        ## strip the sentence parts
        self.sentence_parts = [part.strip() for part in self.sentence_parts] 

##-------------------start-of-translate_sentence()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def translate_sentence(self) -> None:

        """

        This function translates each part of a sentence.\n

        Parameters:\n
        self (object - Kaiseki) : the Kaiseki object.\n

        Returns:\n
        None.\n

        """

        i = 0
        ii = 0

        quote = ""
        error = ""
        
        tilde_active = False
        single_quote_active = False

        while(i < len(self.sentence_parts)):

            ## if tilde is present in part, delete it and set tilde active to true, so we can add it back in a bit
            if(self.special_punctuation[1] == True and "~" in self.sentence_parts[i]): 
                self.sentence_parts[i] = self.sentence_parts[i].replace("~","")
                tilde_active = True

            ## a quote is present in the sentence, but not enclosing the sentence, we need to isolate it
            if(self.special_punctuation[2] == True and "'" in self.sentence_parts[i] and (self.sentence_parts[i][0] != "'" and self.sentence_parts[i][-1] != "'")): ## isolates the quote in the sentence
                
                sentence = self.sentence_parts[i]
                substring_start = sentence.index("'")
                substring_end = 0
                quote = ""

                ii = substring_start
                while(ii < len(sentence)):
                    if(sentence[ii] == "'"):
                        substring_end = ii
                    ii+=1
                    
                quote = sentence[substring_start+1:substring_end]
                self.sentence_parts[i] = sentence[:substring_start+1] + "quote" + sentence[substring_end:]

                single_quote_active = True
                
            try:
                results = str(self.translator.translate_text(self.sentence_parts[i], source_lang= "JA", target_lang="EN-US")) 

                translated_part = results.rstrip(''.join(c for c in string.punctuation if c not in "'\""))
                translated_part = translated_part.rstrip() 

                ## here we re-add the tilde, (note not always accurate but mostly is)
                if(tilde_active == True): 
                    translated_part += "~"
                    tilde_active = False

                ## translates the quote and readds it back to the sentence part
                if(single_quote_active == True): 
                    quote = str(self.translator.translate_text(quote, source_lang= "JA", target_lang="EN-US")) ## translates part to english-us
                    
                    quote = quote.rstrip(''.join(c for c in string.punctuation if c not in "'\""))
                    quote = quote.rstrip() 

                    translated_part = translated_part.replace("'quote'","'" + quote + "'",1)

                ## if punctuation appears first and before any text, add the punctuation and remove it form the list.
                if(len(self.sentence_punctuation) > len(self.sentence_parts)): 
                    self.translated_sentence += self.sentence_punctuation[0]
                    self.sentence_punctuation.pop(0)

                if(self.sentence_punctuation[i] != None):
                    self.translated_sentence += translated_part + self.sentence_punctuation[i] 
                else:
                    self.translated_sentence += translated_part 

                if(i != len(self.sentence_punctuation)-1):
                    self.translated_sentence += " "
                        
            except deepl.exceptions.QuotaExceededException as e:

                print("\nDeepL API quota exceeded\n")
                self.preloader.file_handler.logger.log_action("DeepL API quota exceeded\n")

                self.preloader.toolkit.pause_console()
                
                raise e
                    
            except ValueError as e:

                if(str(e) == "Text must not be empty."):
                    self.translated_sentence += ""
                else:
                    self.translated_sentence += "ERROR"
                    error = str(e)

                    self.preloader.file_handler.logger.log_action("Error is : " + error)
                    self.error_text.append("Error is : " + error)

            i+=1

        self.translated_text.append(self.translated_sentence)
        self.translated_sentence = ""

##-------------------start-of-assemble_results()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    def assemble_results(self) -> None:

        '''

        Prepares the results of the translation for printing.\n

        Parameters:\n
        self (object - Kaiseki) : the Kaiseki object.\n

        Returns:\n
        None.\n

        '''
        
        self.translation_print_result += "Time Elapsed : " + self.preloader.toolkit.get_elapsed_time(self.time_start, self.time_end)

        self.translation_print_result += "\n\nDebug text have been written to : " + os.path.join(self.preloader.file_handler.output_dir, "debug log.txt")
        self.translation_print_result += "\nJ->E text have been written to : " + os.path.join(self.preloader.file_handler.output_dir, "jeCheck.txt")
        self.translation_print_result += "\nTranslated text has been written to : " + os.path.join(self.preloader.file_handler.output_dir, "translatedText.txt")
        self.translation_print_result += "\nErrors have been written to : " + os.path.join(self.preloader.file_handler.output_dir, "error log.txt") + "\n"