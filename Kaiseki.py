import deepl
import string
import os
import time


from time import sleep
from deepl.exceptions import QuotaExceededException
from deepl.exceptions import AuthorizationException

'''
Kaiseki.py

Orginal Author: Seinu#7854

Known issues and limitations:
punctuation spacing is not always accurate
capitalization is an issue in sentences that have multiple parts
Since this is being translated one sentence at a time, the translation is typically less accurate compared to translating in bulk, however, doing it one line at a time seems to completely eliminate sentence duplications and additions.
'''


#-------------------start of initalize_translator()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def initalize_translator(textToTranslate): ## creates translator object and sets up some text
        
        try:
                with open(r'C:\ProgramData\Kudasai\apiKey.txt', 'r', encoding='utf-8') as file:  ## get saved api key if exists
                    apiKey = file.read()

                translator = deepl.Translator(apiKey)

                print("Used saved api key in C:\ProgramData\Kudasai\apiKey.txt")

        except: ## else try to get api key manually
                apikey = input("Please enter the deepL api key you have :  ")

                try: ## if valid save the api key

                        translator = deepl.Translator(apiKey)

                        if(os.path.isdir(r'C:\ProgramData\Kudasai') == False):
                            os.mkdir('C:\ProgramData\Kudasai', 0o666)
                            print("r'C:\ProgramData\Kudasai' created due to lack of the folder")

                        sleep(0.1)
                            
                        if(os.path.exists(r'C:\ProgramData\Kudasai\apiKey.txt') == False):
                           print("r'C:\ProgramData\Kudasai\apiKey.txt' was created due to lack of the file")

                           with open(r'C:\ProgramData\Kudasai\apiKey.txt', 'w+', encoding='utf-8') as key: 
                                    key.write(apiKey)

                        sleep(0.25)
                   
                except AuthorizationException: ## if invalid key exit
                     
                        os.system('cls')
                        
                        print("Authorization Error with creating translator object, please double check your api key as it is incorrect.\n")
                        os.system('pause')
                        
                        exit()

                except Exception as e: ## other error, alert user and raise it
                        os.system('cls')
                        
                        print("Unknown Error with creating translator object, exception will now be raised.\n")
                        os.system('pause')

                        raise e
                
        with open(textToTranslate, 'r', encoding='utf-8') as file: 
                japaneseText = file.readlines()

        return translator,japaneseText

#-------------------start of seperate()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 
def seperate(sentence): ## seperates sentences based of puncutation

        sentenceParts = []
        sentencePunc = []
        specialPunc = [False,False,False]

        i = 0

        buildString = ""
        
        if('"' in sentence):
                sentence = sentence.replace('"', '')
                specialPunc[0] = True

        if('~' in sentence):
                specialPunc[1] = True

        if("'" in sentence):
                specialPunc[2] = True

        while(i < len(sentence)):

            if(sentence[i] == "\n"): ## skip newlines
                    break
                
            if(sentence[i] in [".","!","?","-"]): ## if current character is a puncuation, run a bunch of if's)
                    
                if(sentence[i:i+2] == '!?'):
                        sentenceParts.append(buildString)
                        sentencePunc.append(sentence[i:i+2])
                        i+=1
                        buildString = ""
                                            
                elif(i+3 < len(sentence) and sentence[i:i+4] in ["...!","...?","---.","...."]):
                        sentenceParts.append(buildString)
                        sentencePunc.append(sentence[i:i+4])
                        i+=3
                        buildString = ""
                        
                elif(i+2 < len(sentence) and sentence[i:i+3] in ["---","..."]):
                        sentenceParts.append(buildString)
                        sentencePunc.append(sentence[i:i+3])
                        i+=2
                        buildString = ""
                        
                elif(sentence[i] != "-"):  ## if punc that was found is not a hyphen then just follow normal puncutation seperations
                        sentenceParts.append(buildString)
                        sentencePunc.append(sentence[i])
                        buildString = ""
                else:
                        buildString += sentence[i] ## if it is just a singular hypen, do not consider it puncuation as they are used in honorifics
            else:
                buildString += sentence[i] 

            i += 1
                
        
        if(buildString): ## if end of line, add none puncuation
            sentenceParts.append(buildString)
            sentencePunc.append(None)

        debugText.append("Fragmented Setence Parts " + str(sentenceParts))
        debugText.append("\nSentence Punctuation " + str(sentencePunc))
        debugText.append("\nDoes Sentence Have Special Punc : " + str(specialPunc))

        return sentenceParts,sentencePunc,specialPunc

#-------------------start of translate()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def translate(translator,sentenceParts,sentencePunc): ## for translating each part of a sentence
        
        i = 0
        ii = 0

        finalSentence = ""
        tildeActive = False
        singleQuoteActive = False

        while(i < len(sentenceParts)):

                if("~" in sentenceParts[i]): ## if tilde is present in part, delete it and set tilde active to true, so we can add it in a bit
                        sentenceParts[i] = sentenceParts[i].replace("~","")
                        tildeActive = True

                if("'" in sentenceParts[i]):
                      
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
                        results = str(translator.translate_text(sentenceParts[i], source_lang= "JA", target_lang="EN-US")) ## translates part to english-us

                        translatedPart = results.rstrip(''.join(c for c in string.punctuation if c not in "'\"")) ## basically removes all puncuation  because we are (trying) to handle that ourselves
                        translatedPart = translatedPart.rstrip(' ') ## basically removes all puncuation  because we are (trying) to handle that ourselves


                        if(tildeActive == True): ## here we re-add the tilde, (note not always accurate but mostly is)
                              translatedPart += "~"
                              tildeActive = False

                        if(singleQuoteActive == True):
                                quote = str(translator.translate_text(quote, source_lang= "JA", target_lang="EN-US")) ## translates part to english-us
                                
                                quote = quote.rstrip(''.join(c for c in string.punctuation if c not in "'\"")) ## basically removes all puncuation  because we are (trying) to handle that ourselves
                                quote = quote.rstrip(' ') ## basically removes all puncuation  because we are (trying) to handle that ourselves

                                if(quote[-2] not in string.punctuation and sentencePunc[-1] == None): ## this is for adding a period if it's missing 
                                        quote += "."
                                        
                                translatedPart = translatedPart.replace("'quote'","'" + quote + "'",1)
                        
                        if(sentencePunc[i] != None): ## typically when a sentencePunc is none, it's almost always supposed to be a period
                                finalSentence +=  translatedPart + sentencePunc[i]
                                if(sentencePunc[i] == "." and len(sentencePunc) > 1): ## for spacing (not accurate at all outside of periods)
                                        finalSentence += " "
                        else:
                                finalSentence +=  translatedPart

                except QuotaExceededException:
                        print("\nDeepL API quota exceeeded\n")

                        os.system('pause')
                        exit()
                        
                except ValueError: ## this will trigger if deepL tries to translate an empty string or an extra line
                        finalSentence += ""
                
                i+=1

        return finalSentence

#-------------------start of outputResults()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def output_results():

        global debugText,jeCheckText,finalText
        
        debugPath = r"C:\Users\Tetra\Desktop\KudasaiOutput\tlDebug.txt"
        jePath = r"C:\Users\Tetra\Desktop\KudasaiOutput\jeCheck.txt"
        resultsPath = r"C:\Users\Tetra\Desktop\KudasaiOutput\translatedText.txt"

        with open(debugPath, 'w+', encoding='utf-8') as file:
                file.writelines(debugText)

        with open(jePath, 'w+', encoding='utf-8') as file: 
                file.writelines(jeCheckText)

        with open(resultsPath, 'w+', encoding='utf-8') as file:
                file.writelines(finalText)

        print("\n\nDebug text have been written to : " + debugPath)
        print("\nJ->E text have been written to : " + jePath)
        print("\nTranslated text has been written to : " + resultsPath + "\n")

#-------------------start of commenceTranslation()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def commence_translation(translator,japaneseText):

        try:
                sentenceParts = []
                sentencePunc = []
                specialPunc = [] ## [0] = "" [1] = ~ [3] = ''

                global debugText,jeCheckText,finalText
                debugText,jeCheckText,finalText = [],[],[]

                i = 0

                timeStart = time.time()

                while(i < len(japaneseText)):
                        
                        sentence = japaneseText[i]
                        
                        debugText.append("Inital Sentence : " + sentence)
                        
                        sentenceParts,sentencePunc,specialPunc = seperate(sentence)

                        finalText.append(translate(translator,sentenceParts,sentencePunc))

                        if(len(finalText[i]) > 0 and finalText[i] != "" and finalText[i][-2] not in string.punctuation and sentencePunc[-1] == None): ## this is for adding a period if it's missing 
                                finalText[i] = finalText[i] + "."
                        
                        if(specialPunc[0] == True): ## re-adds quotes
                                finalText[i] =  '"' + finalText[i] + '"'
                        elif('"' in finalText[i]):
                                finalText[i] = finalText[i].replace('"',"'")

                        finalText[i] += "\n"

                        debugText.append("\nTranslated and Reassembled Sentence : " + finalText[i] + "\n-----------------------------------------------\n\n")

                        jeCheckText.append(str(i+1) + ": " + sentence +  "   " +  finalText[i] + "\n")
                        
                        i+=1
                        
                        os.system('cls')
                        sleep(.2)
                        
                        print(str(i) + "/" + str(len(japaneseText)) + " completed.")


                output_results()

                timeEnd = time.time()

                print("Minutes Elapsed : " + str(round((timeEnd - timeStart)/ 60,2)) + "\n")

                os.system('pause')
                
        except:
               output_results()
