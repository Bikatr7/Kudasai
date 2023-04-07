import re
import os
import base64
import openai

from time import sleep

#-------------------start of initialize_text()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def initialize_text(textToTranslate):

        """
        Set the open api key and create a list full of the sentences we need to translate.
        """
        
        try:
                with open(r'C:\\ProgramData\\Kudasai\\GPTApiKey.txt', 'r', encoding='utf-8') as file:  ## get saved api key if exists
                    apiKey = base64.b64decode((file.read()).encode('utf-8')).decode('utf-8')

                openai.api_key = apiKey

                print("Used saved api key in C:\\ProgramData\\Kudasai\\GPTApiKey.txt")

        except: ## else try to get api key manually
                
                apiKey = input("Please enter the openai api key you have : ")

                try: ## if valid save the api key
 
                        openai.api_key = apiKey

                        if(os.path.isdir(r'C:\\ProgramData\\Kudasai') == False):
                            os.mkdir('C:\\ProgramData\\Kudasai', 0o666)
                            print("r'C:\\ProgramData\\Kudasai' created due to lack of the folder")

                        sleep(.1)
                            
                        if(os.path.exists(r'C:\\ProgramData\\Kudasai\\GPTApiKey.txt') == False):
                           print("r'C:\\ProgramData\\Kudasai\\GPTApiKey.txt' was created due to lack of the file")

                           with open(r'C:\\ProgramData\\Kudasai\\GPTApiKey.txt', 'w+', encoding='utf-8') as key: 
                                    key.write(base64.b64encode(apiKey.encode('utf-8')).decode('utf-8'))

                        sleep(.1)
                   
                except openai.error.AuthenticationError: ## if invalid key exit
                     
                        os.system('cls')
                        
                        print("Authorization error with creating translator object, please double check your api key as it appears to be incorrect.\n")
                        os.system('pause')
                        
                        exit()

                except Exception as e: ## other error, alert user and raise it
                        os.system('cls')
                        
                        print("Unknown error with creating translator object, The error is as follows " + str(e)  + "\nThe exception will now be raised.\n")
                        os.system('pause')

                        raise e
                
        with open(textToTranslate, 'r', encoding='utf-8') as file:  ## strips each line of the text to translate
                japaneseText = [line.strip() for line in file.readlines()]

        return japaneseText

#-------------------start-of-output_results()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def output_results():

        global debugText,jeCheckText,japaneseText,errorText
        
        debugPath = str(os.getcwd()) + "\\Desktop\\KudasaiOutput\\tlDebug.txt"
        jePath = str(os.getcwd()) + "\\Desktop\\KudasaiOutput\\jeCheck.txt"
        errorPath = str(os.getcwd()) + "\\Desktop\\KudasaiOutput\\errors.txt"
        resultsPath = str(os.getcwd()) + "\\Desktop\\KudasaiOutput\\translatedText.txt"

        with open(debugPath, 'w+', encoding='utf-8') as file:
                file.writelines(debugText)

        with open(jePath, 'w+', encoding='utf-8') as file: 
                file.writelines(jeCheckText)

        with open(resultsPath, 'w+', encoding='utf-8') as file:
                file.writelines(japaneseText)

        with open(errorPath, 'w+', encoding='utf-8') as file:
                file.writelines(errorText)

        print("\n\nDebug text have been written to : " + debugPath)
        print("\nJ->E text have been written to : " + jePath)
        print("\nTranslated text has been written to : " + resultsPath + "\n")


#-------------------start-of-generate_prompt()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def generate_prompt(index, text):

    prompt = []
    promptLocation = []

    while(index < len(text)):
        sentence = text[index]

        if(len(prompt) < 13):

            if(bool(re.match(r'^[\W_\s\n-]+$', sentence))):
                debugText.append("\n-----------------------------------------------\nSentence : " + sentence + "\nSentence is punctuation... skipping translation\n-----------------------------------------------\n\n")
           
            elif(bool(re.match(r'^[A-Za-z0-9\s\.,\'\?!]+\n*$', sentence))):
                debugText.append("\n-----------------------------------------------\nSentence : " + sentence + "\nSentence is english... skipping translation\n-----------------------------------------------\n\n")
            
            else:
                prompt.append(sentence)
                promptLocation.append(index)
        else:
            return prompt, promptLocation, index
        
        index += 1

    return prompt, promptLocation, index

#-------------------start-of-translate()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def translate():

    MODEL = "gpt-3.5-turbo"

    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": "Do you read me?"},
        ],
        temperature=0,
    )

    output = response['choices'][0]['message']['content']

    print(output)

#-------------------start-of-redistribute()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def redistribute(results,prompt,resultLocations,japaneseText):

    i = 0

    resultList = results.splitlines(True)

    length1 = len(resultList)
    length2 = len(resultLocations)

    if(length1 > length2):
        
        if(length1 > length2 + 2 or (length1 > length2 + 1 and (resultList[0] == resultList[-1]) == False) or (length1 > length2 + 1 and (resultList[0] == "\n" and resultList[-1] == "\n") == False)):
            errorText.append("\n-----------------------------------------------\nA confirmed error has occurred.\nAffected Prompt : " + str(prompt) + "\nPrompt Locations : " + str(resultLocations) + "\n-----------------------------------------------\n\n")
        
        elif(length1 > length2 + 1 and resultList[0] == "\n" and resultList[-1] == "\n"):
            resultList.pop(0)
            resultList.pop(-1)
            errorText.append("\n-----------------------------------------------\nA possible error has occurred.\nAffected Prompt : " + str(prompt) + "\nPrompt Locations : " + str(resultLocations) + "\n-----------------------------------------------\n\n")

        elif(length1 > length2 and resultList[0] == "\n" and resultList[-1] != "\n"):
            resultList.pop(0)

        elif(length1 > length2 and resultList[0] != "\n" and resultList[-1] == "\n"):
            resultList.pop(-1)

        else:
            errorText.append("\n-----------------------------------------------\nA confirmed error has occurred.\nAffected Prompt : " + str(prompt) + "\nPrompt Locations : " + str(resultLocations) + "\n-----------------------------------------------\n\n")

    else:
        pass

    for location in resultLocations:
        japaneseText[location] = resultList[i]
        i+=1

    japaneseText = list(map(lambda s: s if '\n' in s else s + '\n', japaneseText))

    return japaneseText

#-------------------start-of-main()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

global debugText,jeCheckText,errorText
debugText,jeCheckText,errorText = [],[],[]

japaneseText = initialize_text(r'C:\\Users\\Tetra\Desktop\\test.txt')

i = 0

testTranslatedText = '''
Ayanokoji Atsuomi's Monologue:

Rich or poor. The disparity between poverty and wealth.
High education or low education. Education inequality.
City or countryside. Regional inequality.
Underprivileged youth or privileged elderly. Generational inequality.
This Japan is a society of disparity.
What I've mentioned is just a small part, but it truly represents heaven and hell.
The important thing is that many things are not something that cannot be changed. Poor people can rise up and become wealthy, and wealthy people can fall and become poor.
If you hate regional inequality, you can move to the city.
Although I understood the logic, I had nothing.
Born in the countryside, extremely poor, and without education to the point of pity.
I was not physically strong, nor blessed with patience or hardworking nature, even though I understood the reasoning.
'''

while(i < len(japaneseText)):
    prompt, promptLocation, i = generate_prompt(i,japaneseText)

    japaneseText = redistribute(testTranslatedText,prompt,promptLocation,japaneseText)

output_results()