## Basically Deprecated, use Kijiku instead. Currently only maintained for backwards compatibility.
##---------------------------------------
## built-in libraries
import string
import time
import re
import base64
import time

## third party modules
from deepl.translator import Translator
from deepl.exceptions import AuthorizationException, QuotaExceededException

## custom modules
from modules.common.toolkit import Toolkit
from modules.common.file_ensurer import FileEnsurer
from modules.common.logger import Logger

##-------------------start-of-Kaiseki--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Kaiseki:

    """

    Kaiseki is a secondary class that is used to interact with the Deepl API and translate Japanese text sentence by sentence.

    Kaiseki is considered inferior to Kijiku, please consider using Kijiku instead.
    
    """

    ##---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    translator:Translator

    ##---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    text_to_translate = []

    translated_text = []

    je_check_text = []

    error_text = []

    translation_print_result = ""
    
    ##---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    sentence_parts = []

    sentence_punctuation = []

    ## [0] = "" [1] = ~ [2] = '' in Kaiseki.current_sentence but not entire Kaiseki.current_sentence [3] = '' but entire Kaiseki.current_sentence [3] if () in Kaiseki.current_sentence
    special_punctuation = [] 

    current_sentence = ""

    translated_sentence = ""

    ##---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
##-------------------start-of-translate()--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def translate() -> None:

        """

        Translates the text.

        """

        Logger.clear_batch()

        time_start = time.time()

        try:

            Kaiseki.initialize() 

            ## offset time, for if the user doesn't get through Kaiseki.initialize() before the translation starts.
            time_start = time.time()

            Kaiseki.commence_translation()

        except Exception as e:
            
            Kaiseki.translation_print_result += "An error has occurred, outputting results so far..."

            FileEnsurer.handle_critical_exception(e)

        finally:

            time_end = time.time()

            Kaiseki.assemble_results(time_start, time_end)

##-------------------start-of-initialize()--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def initialize() -> None:
        
        """

        Initializes the Kaiseki class by getting the API key and creating the translator object.

        """
        
        ## get saved api key if exists
        try:

            with open(FileEnsurer.deepl_api_key_path, 'r', encoding='utf-8') as file:
                api_key = base64.b64decode((file.read()).encode('utf-8')).decode('utf-8')

            Kaiseki.setup_api_key(api_key)

            Logger.log_action("Used saved api key in " + FileEnsurer.deepl_api_key_path, output=True)

        ## else try to get api key manually
        except Exception as e: 

            api_key = input("DO NOT DELETE YOUR COPY OF THE API KEY\n\nPlease enter the deepL api key you have : ")

            ## if valid save the api key
            try: 

                Kaiseki.setup_api_key(api_key)

                time.sleep(.1)
                    
                FileEnsurer.standard_overwrite_file(FileEnsurer.deepl_api_key_path, base64.b64encode(api_key.encode('utf-8')).decode('utf-8'), omit=True)

                time.sleep(.1)
                
            ## if invalid key exit
            except AuthorizationException: 
                    
                Toolkit.clear_console()
                    
                Logger.log_action("Authorization error with creating translator object, please double check your api key as it appears to be incorrect.\nKaiseki will now exit.", output=True)
                
                Toolkit.pause_console()
                    
                raise e

            ## other error, alert user and raise it
            except Exception as e: 
                
                Toolkit.clear_console()
                    
                Logger.log_action("Unknown error with creating translator object, The error is as follows " + str(e)  + "\nKaiseki will now exit.", output=True)
                
                Toolkit.pause_console()

                raise e

        Toolkit.clear_console()
        Logger.log_barrier()

##-------------------start-of-setup_api_key()--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def setup_api_key(api_key:str) -> None:

        """

        Sets up the api key for the Kaiseki class.

        Parameters:
        api_key (str) : the api key to use.

        """

        Kaiseki.translator = Translator(api_key)

        ## perform a test translation to see if the api key is valid
        try:
            Kaiseki.translator.translate_text("test", target_lang="JA")

            Logger.log_action("API key is valid.", output=True)
        
        except AuthorizationException as e:
            raise e
        
##-------------------start-of-reset_static_variables()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def reset_static_variables() -> None:

        """

        Resets the static variables of the Kaiseki class.
        For when running multiple translations in a row through webgui.

        """

        Logger.clear_batch()

        Kaiseki.text_to_translate = []
        Kaiseki.translated_text = []
        Kaiseki.je_check_text = []
        Kaiseki.error_text = []
        Kaiseki.translation_print_result = ""
        Kaiseki.sentence_parts = []
        Kaiseki.sentence_punctuation = []
        Kaiseki.special_punctuation = []
        Kaiseki.current_sentence = ""
        Kaiseki.translated_sentence = ""

##-------------------start-of-commence_translation()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def commence_translation() -> None:

        """
        
        Commences the translation process using all the functions in the Kaiseki class.

        """

        i = 0 

        while(i < len(Kaiseki.text_to_translate)):

            ## for webgui, if the user presses the clear button, raise an exception to stop the translation
            if(FileEnsurer.do_interrupt == True):
                raise Exception("Interrupted by user.")

            Kaiseki.current_sentence = Kaiseki.text_to_translate[i]
            
            Logger.log_action("Initial Sentence : " + Kaiseki.current_sentence)

            ## Kaiseki is an in-place translation, so it'll build the translated text into Kaiseki.translated_text as it goes.
            if(any(char in Kaiseki.current_sentence for char in ["▼", "△", "◇"])):
                Kaiseki.translated_text.append(Kaiseki.current_sentence + '\n')
                Logger.log_action("Sentence : " + Kaiseki.current_sentence + ", Sentence is a pov change... leaving intact.")

            elif("part" in Kaiseki.current_sentence.lower() or all(char in ["１","２","３","４","５","６","７","８","９", " "] for char in Kaiseki.current_sentence) and not all(char in [" "] for char in Kaiseki.current_sentence) and Kaiseki.current_sentence != '"..."' and Kaiseki.current_sentence != "..."):
                Kaiseki.translated_text.append(Kaiseki.current_sentence + '\n') 
                Logger.log_action("Sentence : " + Kaiseki.current_sentence + ", Sentence is part marker... leaving intact.")

            elif bool(re.match(r'^[\W_\s\n-]+$', Kaiseki.current_sentence)) and not any(char in Kaiseki.current_sentence for char in ["」", "「", "«", "»"]):
                Logger.log_action("Sentence : " + Kaiseki.current_sentence + ", Sentence is punctuation... skipping.")
                Kaiseki.translated_text.append(Kaiseki.current_sentence + "\n")

            elif(bool(re.match(r'^[A-Za-z0-9\s\.,\'\?!]+\n*$', Kaiseki.current_sentence))):
                Logger.log_action("Sentence : " + Kaiseki.current_sentence + ", Sentence is english... skipping translation.")
                Kaiseki.translated_text.append(Kaiseki.current_sentence + "\n")

            elif(len(Kaiseki.current_sentence) == 0 or Kaiseki.current_sentence.isspace() == True):
                Logger.log_action("Sentence is empty... skipping translation.\n")
                Kaiseki.translated_text.append(Kaiseki.current_sentence + "\n") 

            else:
        
                Kaiseki.separate_sentence()

                Kaiseki.translate_sentence()

                ## this is for adding a period if it's missing 
                if(len(Kaiseki.translated_text[i]) > 0 and Kaiseki.translated_text[i] != "" and Kaiseki.translated_text[i][-2] not in string.punctuation and Kaiseki.sentence_punctuation[-1] == None): 
                    Kaiseki.translated_text[i] = Kaiseki.translated_text[i] + "."
                
                ## re-adds quotes
                if(Kaiseki.special_punctuation[0] == True): 
                    Kaiseki.translated_text[i] =  '"' + Kaiseki.translated_text[i] + '"'

                ## replaces quotes because deepL messes up quotes
                elif('"' in Kaiseki.translated_text[i]): 
                    Kaiseki.translated_text[i] = Kaiseki.translated_text[i].replace('"',"'")

                ## re-adds single quotes
                if(Kaiseki.special_punctuation[3] == True): 
                    Kaiseki.translated_text[i] =  "'" + Kaiseki.translated_text[i] + "'"

                ## re-adds parentheses
                if(Kaiseki.special_punctuation[4] == True): 
                    Kaiseki.translated_text[i] =  "(" + Kaiseki.translated_text[i] + ")"

                Logger.log_action("Translated and Reassembled Sentence : " + Kaiseki.translated_text[i])

                Kaiseki.translated_text[i] += "\n"

                Kaiseki.je_check_text.append(str(i+1) + ": " + Kaiseki.current_sentence +  "\n   " +  Kaiseki.translated_text[i] + "\n")
            
            i+=1
            
            Toolkit.clear_console()
            
            Logger.log_action(str(i) + "/" + str(len(Kaiseki.text_to_translate)) + " completed.", output=True)
            Logger.log_barrier()

##-------------------start-of-separate_sentence()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def separate_sentence() -> None: 

        """

        This function separates the sentence into parts and punctuation.
        
        """

        ## resets variables for current_sentence
        Kaiseki.sentence_parts = [] 
        Kaiseki.sentence_punctuation = []
        Kaiseki.special_punctuation = [False,False,False,False,False] 

        i = 0

        buildString = ""

        ## checks if quotes are in the sentence and removes them
        if('"' in Kaiseki.current_sentence):
            Kaiseki.current_sentence = Kaiseki.current_sentence.replace('"', '')
            Kaiseki.special_punctuation[0] = True

        ## checks if tildes are in the sentence
        if('~' in Kaiseki.current_sentence):
            Kaiseki.special_punctuation[1] = True

        ## checks if apostrophes are in the sentence but not at the beginning or end
        if(Kaiseki.current_sentence.count("'") == 2 and (Kaiseki.current_sentence[0] != "'" and Kaiseki.current_sentence[-1] != "'")):
            Kaiseki.special_punctuation[2] = True

        ## checks if apostrophes are in the sentence and removes them
        elif(Kaiseki.current_sentence.count("'") == 2):
            Kaiseki.special_punctuation[3] = True
            Kaiseki.current_sentence = Kaiseki.current_sentence.replace("'", "")

        ## checks if parentheses are in the sentence and removes them
        if("(" in Kaiseki.current_sentence and ")" in Kaiseki.current_sentence):
            Kaiseki.special_punctuation[4] = True
            Kaiseki.current_sentence= Kaiseki.current_sentence.replace("(","")
            Kaiseki.current_sentence= Kaiseki.current_sentence.replace(")","")

        while(i < len(Kaiseki.current_sentence)):
                
            if(Kaiseki.current_sentence[i] in [".","!","?","-"]): 

                if(i+5 < len(Kaiseki.current_sentence) and Kaiseki.current_sentence[i:i+6] in ["......"]):

                    if(i+6 < len(Kaiseki.current_sentence) and Kaiseki.current_sentence[i:i+7] in ["......'"]):
                        buildString += "'"
                        i+=1

                    if(buildString != ""):
                        Kaiseki.sentence_parts.append(buildString)

                    Kaiseki.sentence_punctuation.append(Kaiseki.current_sentence[i:i+6])
                    i+=5
                    buildString = ""
                    
                if(i+4 < len(Kaiseki.current_sentence) and Kaiseki.current_sentence[i:i+5] in [".....","...!?"]):

                    if(i+5 < len(Kaiseki.current_sentence) and Kaiseki.current_sentence[i:i+6] in [".....'","...!?'"]):
                        buildString += "'"
                        i+=1

                    if(buildString != ""):
                        Kaiseki.sentence_parts.append(buildString)

                    Kaiseki.sentence_punctuation.append(Kaiseki.current_sentence[i:i+5])
                    i+=4
                    buildString = ""
                                            
                elif(i+3 < len(Kaiseki.current_sentence) and Kaiseki.current_sentence[i:i+4] in ["...!","...?","---.","....","!..."]):

                    if(i+4 < len(Kaiseki.current_sentence) and Kaiseki.current_sentence[i:i+5] in ["...!'","...?'","---.'","....'","!...'"]):
                        buildString += "'"
                        i+=1

                    if(buildString != ""):
                        Kaiseki.sentence_parts.append(buildString)

                    Kaiseki.sentence_punctuation.append(Kaiseki.current_sentence[i:i+4])
                    i+=3
                    buildString = ""
                        
                elif(i+2 < len(Kaiseki.current_sentence) and Kaiseki.current_sentence[i:i+3] in ["---","..."]):

                    if(i+3 < len(Kaiseki.current_sentence) and Kaiseki.current_sentence[i:i+4] in ["---'","...'"]):
                        buildString += "'"
                        i+=1

                    if(buildString != ""):
                        Kaiseki.sentence_parts.append(buildString)

                    Kaiseki.sentence_punctuation.append(Kaiseki.current_sentence[i:i+3])
                    i+=2
                    buildString = ""

                elif(i+1 < len(Kaiseki.current_sentence) and Kaiseki.current_sentence[i:i+2] == '!?'):

                    if(i+2 < len(Kaiseki.current_sentence) and Kaiseki.current_sentence[i:i+3] == "!?'"):
                        buildString += "'"
                        i+=1

                    if(buildString != ""):
                        Kaiseki.sentence_parts.append(buildString)

                    Kaiseki.sentence_punctuation.append(Kaiseki.current_sentence[i:i+2])
                    i+=1
                    buildString = ""
                        
                ## if punctuation that was found is not a hyphen then just follow normal punctuation separation rules
                elif(Kaiseki.current_sentence[i] != "-"):

                    if(i+1 < len(Kaiseki.current_sentence) and Kaiseki.current_sentence[i+1] == "'"):
                        buildString += "'"

                    if(buildString != ""):
                        Kaiseki.sentence_parts.append(buildString)

                    Kaiseki.sentence_punctuation.append(Kaiseki.current_sentence[i])
                    buildString = ""

                ## if it is just a singular hyphen, do not consider it punctuation as they are used in honorifics
                else:
                    buildString += Kaiseki.current_sentence[i]
            else:
                buildString += Kaiseki.current_sentence[i] 

            i += 1
                
        ## if end of line, add none punctuation which means a period needs to be added later
        if(buildString): 
            Kaiseki.sentence_parts.append(buildString)
            Kaiseki.sentence_punctuation.append(None)

        Logger.log_action("Fragmented Sentence Parts " + str(Kaiseki.sentence_parts))
        Logger.log_action("Sentence Punctuation " + str(Kaiseki.sentence_punctuation))
        Logger.log_action("Does Sentence Have Special Punctuation : " + str(Kaiseki.special_punctuation))

        ## strip the sentence parts
        Kaiseki.sentence_parts = [part.strip() for part in Kaiseki.sentence_parts] 

##-------------------start-of-translate_sentence()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def translate_sentence() -> None:

        """

        This function translates each part of a sentence.

        """

        i = 0
        ii = 0

        quote = ""
        error = ""
        
        tilde_active = False
        single_quote_active = False

        while(i < len(Kaiseki.sentence_parts)):

            ## if tilde is present in part, delete it and set tilde active to true, so we can add it back in a bit
            if(Kaiseki.special_punctuation[1] == True and "~" in Kaiseki.sentence_parts[i]): 
                Kaiseki.sentence_parts[i] = Kaiseki.sentence_parts[i].replace("~","")
                tilde_active = True

            ## a quote is present in the sentence, but not enclosing the sentence, we need to isolate it
            if(Kaiseki.special_punctuation[2] == True and "'" in Kaiseki.sentence_parts[i] and (Kaiseki.sentence_parts[i][0] != "'" and Kaiseki.sentence_parts[i][-1] != "'")):
                
                sentence = Kaiseki.sentence_parts[i]
                substring_start = sentence.index("'")
                substring_end = 0
                quote = ""

                ii = substring_start
                while(ii < len(sentence)):
                    if(sentence[ii] == "'"):
                        substring_end = ii
                    ii+=1
                    
                quote = sentence[substring_start+1:substring_end]
                Kaiseki.sentence_parts[i] = sentence[:substring_start+1] + "quote" + sentence[substring_end:]

                single_quote_active = True
                
            try:
                results = str(Kaiseki.translator.translate_text(Kaiseki.sentence_parts[i], source_lang= "JA", target_lang="EN-US")) 

                translated_part = results.rstrip(''.join(c for c in string.punctuation if c not in "'\""))
                translated_part = translated_part.rstrip() 

                ## here we re-add the tilde, (note not always accurate but mostly is)
                if(tilde_active == True): 
                    translated_part += "~"
                    tilde_active = False

                ## translates the quote and re-adds it back to the sentence part
                if(single_quote_active == True): 
                    quote = str(Kaiseki.translator.translate_text(quote, source_lang= "JA", target_lang="EN-US")) ## translates part to english-us
                    
                    quote = quote.rstrip(''.join(c for c in string.punctuation if c not in "'\""))
                    quote = quote.rstrip() 

                    translated_part = translated_part.replace("'quote'","'" + quote + "'",1)

                ## if punctuation appears first and before any text, add the punctuation and remove it form the list.
                if(len(Kaiseki.sentence_punctuation) > len(Kaiseki.sentence_parts)): 
                    Kaiseki.translated_sentence += Kaiseki.sentence_punctuation[0]
                    Kaiseki.sentence_punctuation.pop(0)

                if(Kaiseki.sentence_punctuation[i] != None):
                    Kaiseki.translated_sentence += translated_part + Kaiseki.sentence_punctuation[i] 
                else:
                    Kaiseki.translated_sentence += translated_part 

                if(i != len(Kaiseki.sentence_punctuation)-1):
                    Kaiseki.translated_sentence += " "
                        
            except QuotaExceededException as e:

                Logger.log_action("DeepL API quota exceeded.", output=True)

                Toolkit.pause_console()
                
                raise e
                    
            except ValueError as e:

                if(str(e) == "Text must not be empty."):
                    Kaiseki.translated_sentence += ""
                else:
                    Kaiseki.translated_sentence += "ERROR"
                    error = str(e)

                    Logger.log_action("Error is : " + error)
                    Kaiseki.error_text.append("Error is : " + error)

            i+=1

        Kaiseki.translated_text.append(Kaiseki.translated_sentence)
        Kaiseki.translated_sentence = ""

##-------------------start-of-assemble_results()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def assemble_results(time_start:float, time_end:float) -> None:

        """

        Prepares the results of the translation for printing.

        Parameters:
        time_start (float) : the time the translation started.
        time_end (float) : the time the translation ended.

        """
        
        Kaiseki.translation_print_result += "Time Elapsed : " + Toolkit.get_elapsed_time(time_start, time_end)

        Kaiseki.translation_print_result += "\n\nDebug text have been written to : " + FileEnsurer.debug_log_path
        Kaiseki.translation_print_result += "\nJ->E text have been written to : " + FileEnsurer.je_check_path
        Kaiseki.translation_print_result += "\nTranslated text has been written to : " + FileEnsurer.translated_text_path
        Kaiseki.translation_print_result += "\nErrors have been written to : " + FileEnsurer.error_log_path + "\n"

##-------------------start-of-write_kaiseki_results()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def write_kaiseki_results() -> None:

        """

        This function is called to write the results of the Kaiseki translation module to the output directory.

        """

        ## ensures the output directory exists, cause it could get moved or fucked with.
        FileEnsurer.standard_create_directory(FileEnsurer.output_dir)

        with open(FileEnsurer.error_log_path, 'a+', encoding='utf-8') as file:
            file.writelines(Kaiseki.error_text)

        with open(FileEnsurer.je_check_path, 'w', encoding='utf-8') as file:
            file.writelines(Kaiseki.je_check_text) 

        with open(FileEnsurer.translated_text_path, 'w', encoding='utf-8') as file:
            file.writelines(Kaiseki.translated_text)

        ## Instructions to create a copy of the output for archival
        FileEnsurer.standard_create_directory(FileEnsurer.archive_dir)

        timestamp = Toolkit.get_timestamp(is_archival=True)

        list_of_result_tuples = [('kaiseki_translated_text', Kaiseki.translated_text),
                                 ('kaiseki_je_check_text', Kaiseki.je_check_text),
                                 ('kaiseki_error_log', Kaiseki.error_text),
                                 ('debug_log', Logger.log_file_path)]

        FileEnsurer.archive_results(list_of_result_tuples, 
                                    module='kaiseki', timestamp=timestamp)

        ## pushes the tl debug log to the file without clearing the file
        Logger.push_batch()
