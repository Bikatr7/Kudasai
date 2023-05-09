import string
import os
import time
import re
import base64


from time import sleep
from typing import List

from deepl.exceptions import QuotaExceededException
from deepl.exceptions import AuthorizationException
from deepl import Translator


from Util import associated_functions

'''
Kaiseki.py

Original Author: Seinu#7854

'''

#-------------------start-of-initialize_translator()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def initialize_translator(textToTranslate:str, configDir:str) -> tuple[Translator, List[str]]:

        """

        Initializes the translator object and gets the text to translate.\n

        Parameters:\n
        textToTranslate (string) the path to the text file to translate\n
        configDir (string) the path to the config folder\n

        Returns:\n
        translator (object - Translator) the translator object\n
        japaneseText (list - string) a list of the text to translate\n
        
        """
        
        try:
                with open(os.path.join(configDir,'DeeplApiKey.txt'), 'r', encoding='utf-8') as file:  ## get saved api key if exists
                    apiKey = base64.b64decode((file.read()).encode('utf-8')).decode('utf-8')

                translator = Translator(apiKey)

                print("Used saved api key in " + os.path.join(configDir,'DeeplApiKey.txt'))

        except Exception as e: ## else try to get api key manually

                if(os.path.isfile("C:\\ProgramData\\Kudasai\\DeeplApiKey.txt") == True):
                        os.remove("C:\\ProgramData\\Kudasai\\DeeplApiKey.txt")
                        print("r'C:\\ProgramData\\Kudasai\\DeeplApiKey.txt' was deleted due to Kudasai switching to user storage\n\n")

                apiKey = input("DO NOT DELETE YOUR COPY OF THE API KEY\n\nPlease enter the deepL api key you have : ")

                try: ## if valid save the api key
 
                        translator = Translator(apiKey)

                        if(os.path.isdir(configDir) == False):
                            os.mkdir(configDir, 0o666)
                            print(configDir + " was created due to lack of the folder")

                        sleep(.1)
                            
                        if(os.path.exists(os.path.join(configDir,'DeeplApiKey.txt')) == False):
                           print(os.path.join(configDir,'DeeplApiKey.txt') + " was created due to lack of the file")

                           with open(os.path.join(configDir,'DeeplApiKey.txt'), 'w+', encoding='utf-8') as key: 
                                    key.write(base64.b64encode(apiKey.encode('utf-8')).decode('utf-8'))

                        sleep(.1)
                   
                except AuthorizationException: ## if invalid key exit
                     
                        associated_functions.clear_console()
                        
                        print("Authorization error with creating translator object, please double check your api key as it appears to be incorrect.\nKudasai will now exit.\n")
                        associated_functions.pause_console()
                        
                        exit()

                except Exception as e: ## other error, alert user and raise it
                        associated_functions.clear_console()
                        
                        print("Unknown error with creating translator object, The error is as follows " + str(e)  + "\nKudasai will now exit.\n")
                        associated_functions.pause_console()

                        exit()

        with open(textToTranslate, 'r', encoding='utf-8') as file:  ## strips each line of the text to translate
                japaneseText = [line.strip() for line in file.readlines()]

        return translator,japaneseText

#-------------------start-of-separate()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 
def separate(sentence) -> tuple[List[str], List[str], List[bool]]: 

        """
        
        Separates a sentence into parts based of punctuation.\n

        Parameters:\n
        sentence (string) a sentence(line) of japanese text\n

        Returns:\n
        sentenceParts (list - string) a list of parts of text which is derived from sentence\n
        sentencePunctuation (list - string) a list of punctuation found in sentence\n
        specialPunctuation (list - boolean) a list of booleans indicating whether "special" punctuation exist in the sentence\n

        """

        sentenceParts = []
        sentencePunctuation = []
        specialPunctuation = [False,False,False,False,False] ## [0] = "" [1] = ~ [2] = '' in sentence but not entire sentence [3] = '' but entire sentence [4] = enclosing entire sentence
 
        i = 0

        buildString = ""
 
        if('"' in sentence):
                sentence = sentence.replace('"', '')
                specialPunctuation[0] = True

        if('~' in sentence):
                specialPunctuation[1] = True

        if(sentence.count("'") == 2 and (sentence[0] != "'" and sentence[-1] != "'")):
                specialPunctuation[2] = True

        elif(sentence.count("'") == 2):
               specialPunctuation[3] = True
               sentence = sentence.replace("'", "")

        if("(" in sentence and ")" in sentence):
               specialPunctuation[4] = True
               sentence= sentence.replace("(","")
               sentence= sentence.replace(")","")

        while(i < len(sentence)):
                
            if(sentence[i] in [".","!","?","-"]): 

                if(i+5 < len(sentence) and sentence[i:i+6] in ["......"]):

                        if(i+6 < len(sentence) and sentence[i:i+7] in ["......'"]):
                               buildString += "'"
                               i+=1

                        if(buildString != ""):
                               sentenceParts.append(buildString)

                        sentencePunctuation.append(sentence[i:i+6])
                        i+=5
                        buildString = ""
                    
                if(i+4 < len(sentence) and sentence[i:i+5] in [".....","...!?"]):

                        if(i+5 < len(sentence) and sentence[i:i+6] in [".....'","...!?'"]):
                               buildString += "'"
                               i+=1

                        if(buildString != ""):
                               sentenceParts.append(buildString)

                        sentencePunctuation.append(sentence[i:i+5])
                        i+=4
                        buildString = ""
                                            
                elif(i+3 < len(sentence) and sentence[i:i+4] in ["...!","...?","---.","....","!..."]):

                        if(i+4 < len(sentence) and sentence[i:i+5] in ["...!'","...?'","---.'","....'","!...'"]):
                               buildString += "'"
                               i+=1

                        if(buildString != ""):
                               sentenceParts.append(buildString)

                        sentencePunctuation.append(sentence[i:i+4])
                        i+=3
                        buildString = ""
                        
                elif(i+2 < len(sentence) and sentence[i:i+3] in ["---","..."]):

                        if(i+3 < len(sentence) and sentence[i:i+4] in ["---'","...'"]):
                               buildString += "'"
                               i+=1

                        if(buildString != ""):
                               sentenceParts.append(buildString)

                        sentencePunctuation.append(sentence[i:i+3])
                        i+=2
                        buildString = ""

                elif(i+1 < len(sentence) and sentence[i:i+2] == '!?'):

                        if(i+2 < len(sentence) and sentence[i:i+3] == "!?'"):
                               buildString += "'"
                               i+=1

                        if(buildString != ""):
                               sentenceParts.append(buildString)

                        sentencePunctuation.append(sentence[i:i+2])
                        i+=1
                        buildString = ""
                        
                elif(sentence[i] != "-"):  ## if punctuation that was found is not a hyphen then just follow normal punctuation separation rules

                        if(i+1 < len(sentence) and sentence[i+1] == "'"):
                               buildString += "'"

                        if(buildString != ""):
                               sentenceParts.append(buildString)

                        sentencePunctuation.append(sentence[i])
                        buildString = ""

                else:
                        buildString += sentence[i] ## if it is just a singular hyphen, do not consider it punctuation as they are used in honorifics
            else:
                buildString += sentence[i] 

            i += 1
                
        
        if(buildString): ## if end of line, add none punctuation which means a period needs to be added later
            sentenceParts.append(buildString)
            sentencePunctuation.append(None)

        debugText.append("\nFragmented Sentence Parts " + str(sentenceParts))
        debugText.append("\nSentence Punctuation " + str(sentencePunctuation))
        debugText.append("\nDoes Sentence Have Special Punctuation : " + str(specialPunctuation))

        sentenceParts = [part.strip() for part in sentenceParts] ## strip the parts as well

        return sentenceParts,sentencePunctuation,specialPunctuation

#-------------------start-of-translate()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def translate(translator,sentenceParts,sentencePunctuation,specialPunctuation,scriptDir): ## for translating each part of a sentence

        """

        Translates individual sentence parts and quotes

        Parameters:
        translator (object - deepL.Translator) a deepL translator object
        sentenceParts (list - string) a list of parts of text which is derived from sentence
        sentencePunctuation (list - string) a list of punctuation found in sentence
        specialPunctuation (list - boolean) a list of booleans indicating whether "special" punctuation exist in the sentence
        scriptDir (string) the directory of the script

        Returns:
        finalSentence (string) a fully translated and reassembled version of sentence

        """

        i = 0
        ii = 0

        finalSentence = ""
        quote = ""
        error = ""
        
        errorActive = False
        tildeActive = False
        singleQuoteActive = False

        ## [0] = "" [1] = ~ [2] = '' in sentence but not entire sentence [3] = '' but entire sentence

        while(i < len(sentenceParts)):

                if(specialPunctuation[1] == True and "~" in sentenceParts[i]): ## if tilde is present in part, delete it and set tilde active to true, so we can add it in a bit
                        sentenceParts[i] = sentenceParts[i].replace("~","")
                        tildeActive = True

                if(specialPunctuation[2] == True and "'" in sentenceParts[i] and (sentenceParts[i][0] != "'" and sentenceParts[i][-1] != "'")): ## isolates the quote in the sentence
                      
                      Str = sentenceParts[i]
                      subStart = Str.index("'")
                      subEnd = 0
                      quote = ""

                      ii = subStart
                      while(ii < len(Str)):
                            if(Str[ii] == "'"):
                                  subEnd = ii
                            ii+=1
                        
                      quote = Str[subStart+1:subEnd]
                      sentenceParts[i] = Str[:subStart+1] + "quote" + Str[subEnd:]

                      singleQuoteActive = True
                      
                try:
                        results = str(translator.translate_text(sentenceParts[i], source_lang= "JA", target_lang="EN-US")) 

                        translatedPart = results.rstrip(''.join(c for c in string.punctuation if c not in "'\""))
                        translatedPart = translatedPart.rstrip() 
       

                        if(tildeActive == True): ## here we re-add the tilde, (note not always accurate but mostly is)
                              translatedPart += "~"
                              tildeActive = False

                        if(singleQuoteActive == True): ## translates the quote and readds it back to the sentence part
                                quote = str(translator.translate_text(quote, source_lang= "JA", target_lang="EN-US")) ## translates part to english-us
                                
                                quote = quote.rstrip(''.join(c for c in string.punctuation if c not in "'\""))
                                quote = quote.rstrip() 

                                translatedPart = translatedPart.replace("'quote'","'" + quote + "'",1)

                        if(len(sentencePunctuation) > len(sentenceParts)): ## if punctuation appears first and before any text, add the punctuation and remove it form the list.
                               finalSentence += sentencePunctuation[0]
                               sentencePunctuation.pop(0)

                        if(sentencePunctuation[i] != None):
                                finalSentence += translatedPart + sentencePunctuation[i] 
                        else:
                                finalSentence += translatedPart 

                        if(i != len(sentencePunctuation)-1):
                               finalSentence += " "
                               
                except QuotaExceededException:

                        print("\nDeepL API quota exceeded\n")

                        associated_functions.pause_console()

                        associated_functions.output_results(scriptDir,debugText,jeCheckText,finalText,errorText)
                        exit()
                        
                except ValueError as e:

                        if(str(e) == "Text must not be empty."):
                                finalSentence += ""
                        else:
                                finalSentence += "ERROR"
                                errorActive = True
                                error = str(e)

                i+=1

        if(errorActive == True):
                debugText.append("\nError is : " + error)
                errorText.append("\nError is : " + error)
               
        return finalSentence

#-------------------start-of-commence_translation()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def commence_translation(translator:Translator, japaneseText:List[str],scriptDir:str) -> None:

        """
        
        Uses all the other functions to translate the text provided

        Parameters:
        translator (object - deepL.translator) a deepL translator object
        japaneseText (list - string) a list of japanese lines to translate
        scriptDir (string) the path of the directory that holds Kudasai.py

        Returns: 
        None

        """

        try:
                sentenceParts = []
                sentencePunctuation = []
                specialPunctuation = [] ## [0] = "" [1] = ~ [2] = '' in sentence but not entire sentence [3] = '' but entire sentence

                global debugText,jeCheckText,finalText,errorText
                debugText,jeCheckText,finalText,errorText = [],[],[],[]

                i = 0

                timeStart = time.time()

                while(i < len(japaneseText)):
                        
                        sentence = japaneseText[i]
                        
                        debugText.append("Initial Sentence : " + sentence)

                        if("△▼△▼△▼△" in sentence):
                                finalText.append(sentence + "\n")
                                debugText.append("\n-----------------------------------------------\nSentence : " + sentence + "\nSentence is a pov change... leaving intact\n-----------------------------------------------\n\n")

                        elif bool(re.match(r'^[\W_\s\n-]+$', sentence)) and not any(char in sentence for char in ["」", "「", "«", "»"]):
                                debugText.append("\n-----------------------------------------------\nSentence : " + sentence + "\nSentence is punctuation... skipping\n-----------------------------------------------\n\n")
                                finalText.append(sentence + "\n")

                        elif(bool(re.match(r'^[A-Za-z0-9\s\.,\'\?!]+\n*$', sentence))):
                                debugText.append("\n-----------------------------------------------\nSentence : " + sentence + "\nSentence is english... skipping\n-----------------------------------------------\n\n")
                                finalText.append(sentence + "\n")

                        elif(len(sentence) == 0 or sentence.isspace() == True):
                                debugText.append("\nSentence is empty... skipping translation\n-----------------------------------------------\n\n")
                                finalText.append(sentence + "\n")  

                        else:
                        
                                sentenceParts,sentencePunctuation,specialPunctuation = separate(sentence)

                                finalText.append(translate(translator,sentenceParts,sentencePunctuation,specialPunctuation,scriptDir))

                                if(len(finalText[i]) > 0 and finalText[i] != "" and finalText[i][-2] not in string.punctuation and sentencePunctuation[-1] == None): ## this is for adding a period if it's missing 
                                        finalText[i] = finalText[i] + "."
                                
                                if(specialPunctuation[0] == True): ## re-adds quotes
                                        finalText[i] =  '"' + finalText[i] + '"'

                                elif('"' in finalText[i]): ## replaces quotes because deepL adds them sometimes
                                        finalText[i] = finalText[i].replace('"',"'")

                                if(specialPunctuation[3] == True): ## re-adds single quotes
                                        finalText[i] =  "'" + finalText[i] + "'"

                                if(specialPunctuation[4] == True): ## re-adds parentheses quotes
                                        finalText[i] =  "(" + finalText[i] + ")"

                                finalText[i] += "\n"

                                debugText.append("\nTranslated and Reassembled Sentence : " + finalText[i] + "\n-----------------------------------------------\n\n")

                                jeCheckText.append(str(i+1) + ": " + sentence +  "\n   " +  finalText[i] + "\n")
                        
                        i+=1
                        
                        associated_functions.clear_console()
                        
                        print(str(i) + "/" + str(len(japaneseText)) + " completed.")


                associated_functions.output_results(scriptDir,debugText,jeCheckText,finalText,errorText)

                timeEnd = time.time()

                print("\nTime Elapsed : " + associated_functions.get_elapsed_time(timeStart, timeEnd))

                associated_functions.pause_console()
                
        except Exception as e:
               print("\nUncaught error has been raised in Kaiseki, error is as follows : " + str(e) + "\nOutputting incomplete results\n")
               associated_functions.output_results(scriptDir,debugText,jeCheckText,finalText,errorText)
