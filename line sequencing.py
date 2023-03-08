import deepl
import string
import os
import time

from time import sleep
from deepl.exceptions import QuotaExceededException

'''
Unnamed prototype for automated deepL translation.

This is still very much a work in progress and is by no means efficient at all, so please don't criticize me too much.

Known issues and limitations:
punctuation spacing is not always accurate
capitalization is an issue in sentences that have multiple parts
Since this is being translated one sentence at a time, the translation is typically less accurate compared to translating in bulk, however, doing it one line at a time seems to completely eliminate sentence duplications and additions.
Script requires Kudasai to be ran first or KudasaiOutput folder to be present on desktop
paths are currently hardcoded for ease of testing
'''


#-------------------start of initalize()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def initalize(debugPath,jePath): ## creates translator object and handles some files related for output (keep in mind this script will not function without kudasai being run first or the KudasaiOutput folder isn't present)

        with open(debugPath, 'a+', encoding='utf-8') as file: 
                file.truncate(0)

        with open(jePath, 'a+', encoding='utf-8') as file: 
                file.truncate(0)
        
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
                           key = open(r'C:\ProgramData\Kudasai\apiKey.txt', "w+",encoding="utf8")
                           key.write(apiKey)
                           key.close()

                        sleep(0.25)
                   
                except: ## if invalid exit
                     
                        os.system('cls')
                        
                        print("Error with creating translator object, please double check your api key\n")
                        os.system('pause')
                        
                        exit()

        return translator

#-------------------start of seperate()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 
def seperate(sentence): ## seperates sentences based of puncutation

        sentenceParts = []
        sentencePunc = []
        specialPunc = []

        i = 0

        buildString = ""
        
        if('"' in sentence): ## if "" are present in a line they are removed ahead of time and added back later.
            sentence = sentence.replace('"', '') 
            specialPunc.append(True)
        else:
            specialPunc.append(False)

        if('~' in sentence): 
            specialPunc.append(True)
        else:
            specialPunc.append(False)

        while(i < len(sentence)):

            if(sentence[i] == "\n"): ## skip newlines
                    break
                
            if(sentence[i] in [".","!","?","-"]): ## if current character is a puncuation, run a bunch of if's)
                if(sentence[i] == '!' and sentence[i+1] =='?'): ## if next punc is "!?"
                        sentenceParts.append(buildString)
                        sentencePunc.append(sentence[i] + sentence[i+1])
                        i+=1
                        buildString = ""
                elif(i+3 < len(sentence) and sentence[i] == "." and sentence[i+1] == "." and sentence[i+2] == "." and sentence[i+3] == "!"): ## if next punc is "...!"
                        sentenceParts.append(buildString)
                        sentencePunc.append(sentence[i] + sentence[i+1] + sentence[i+2] + sentence[i+3])
                        i+=3
                        buildString = ""
                elif(i+3 < len(sentence) and sentence[i] == "." and sentence[i+1] == "." and sentence[i+2] == "." and sentence[i+3] == "?"): ## if next punc is "...?"
                        sentenceParts.append(buildString)
                        sentencePunc.append(sentence[i] + sentence[i+1] + sentence[i+2] + sentence[i+3])
                        i+=3
                        buildString = ""
                elif(i+3 < len(sentence) and sentence[i] == "-" and sentence[i+1] == "-" and sentence[i+2] == "-" and sentence[i+3] == "."): ## if next punc is "---."
                        sentenceParts.append(buildString)
                        sentencePunc.append(sentence[i] + sentence[i+1] + sentence[i+2] + sentence[i+3])
                        i+=2
                        buildString = ""
                elif(i+2 < len(sentence) and sentence[i] == "-" and sentence[i+1] == "-" and sentence[i+2] == "-"): ## if next punc is "---"
                        sentenceParts.append(buildString)
                        sentencePunc.append(sentence[i] + sentence[i+1] + sentence[i+2])
                        i+=2
                        buildString = ""
                elif(i+2 < len(sentence) and sentence[i] == "." and sentence[i+1] == "." and sentence[i+2] == "."): ## if next punc is "..."
                        sentenceParts.append(buildString)
                        sentencePunc.append(sentence[i] + sentence[i+1] + sentence[i+2])
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

        debugWrite(r"C:\Users\Tetra\Desktop\KudasaiOutput\tlDebug.txt","Fragmented Setence Parts " + str(sentenceParts))
        debugWrite(r"C:\Users\Tetra\Desktop\KudasaiOutput\tlDebug.txt","Sentence Punctuation " + str(sentencePunc))
        debugWrite(r"C:\Users\Tetra\Desktop\KudasaiOutput\tlDebug.txt","Does Sentence Have Special Punc : " + str(specialPunc))

        return sentenceParts,sentencePunc,specialPunc

#-------------------start of translate()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def translate(translator,sentenceParts,sentencePunc): ## for translating each part of a sentence

        i = 0
        ii = 0

        finalSentence = ""
        tildeActive = False
        singleQuoteActive = False

        while(i < len(sentenceParts)):

                if("~" in sentenceParts[i]): ## if tilde is present in part, delete it and set tidle active to true, so we can add it in a bit
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
                        
                except: ## this will trigger if deepL tries to translate an empty string or an extra line
                        finalSentence += ""
                
                i+=1

        return finalSentence

#-------------------start of output()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def output(path, results):

    results = list(map(lambda x: x + '\n', results))

    with open(path, 'w+', encoding='utf-8') as f:
        f.writelines(results)

#-------------------start of debugWrite()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def debugWrite(debugPath, sentence):

    with open(debugPath, 'a+', encoding='utf-8') as file: 
        file.write(sentence + "\n")

#-------------------start of debugWrite()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def jeWrite(jePath, sentence):

    with open(jePath, 'a+', encoding='utf-8') as file: 
        file.write(sentence + "\n")
        
#-------------------start of main()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

translator = initalize(r"C:\Users\Tetra\Desktop\KudasaiOutput\tlDebug.txt",r"C:\Users\Tetra\Desktop\KudasaiOutput\jeCheck.txt")

testFile = r"C:\Users\Tetra\Desktop\test.txt"

with open(testFile, 'r', encoding='utf-8') as file: 
        japaneseText = file.readlines()

sentenceParts = []
sentencePunc = []
specialPunc = [] ## [0] = "" [1] = ~
finalSentence = []

i,ii = 0,0

timeStart = time.time()

while(i < len(japaneseText)):
        sentence = japaneseText[i]
        
        debugWrite(r"C:\Users\Tetra\Desktop\KudasaiOutput\tlDebug.txt","Inital Sentence : " + sentence)
        
        sentenceParts,sentencePunc,specialPunc = seperate(sentence)

        finalSentence.append(translate(translator,sentenceParts,sentencePunc))

        if(len(finalSentence[i]) > 0 and finalSentence[i] != "" and finalSentence[i][-2] not in string.punctuation and sentencePunc[-1] == None): ## this is for adding a period if it's missing 
                finalSentence[i] = finalSentence[i] + "."
        
        if(specialPunc[0] == True): ## re-adds quotes
              finalSentence[i] =  '"' + finalSentence[i] + '"'
        elif('"' in finalSentence[i]):
                finalSentence[i] = finalSentence[i].replace('"',"'")

        debugWrite(r"C:\Users\Tetra\Desktop\KudasaiOutput\tlDebug.txt","\nTranslated and Reassembled Sentence : " + finalSentence[i])
        debugWrite(r"C:\Users\Tetra\Desktop\KudasaiOutput\tlDebug.txt","-----------------------------------------------\n")


        jeWrite(r"C:\Users\Tetra\Desktop\KudasaiOutput\jeCheck.txt",str(i+1) + ": " + sentence +  "   " +  finalSentence[i] + "\n")
        
        i+=1
        
        os.system('cls')
        sleep(.2)
        print(str(i) + "/" + str(len(japaneseText)) + " completed.")

              
output(r"C:\Users\Tetra\Desktop\KudasaiOutput\translatedText.txt",finalSentence)
              
timeEnd = time.time()

print("Minutes Elapsed : " + str(round((timeEnd - timeStart)/ 60,2)))
os.system('pause')
