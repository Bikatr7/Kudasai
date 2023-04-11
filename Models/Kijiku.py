import re
import os
import base64
import openai
import backoff
import tiktoken
import time
import json

from time import sleep

'''
Kijiku.py

Original Author: Seinu#7854

'''

#-------------------start of change_settings()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def change_settings(kijikuRules):
     
    while(True):

        os.system('cls')

        print("See https://platform.openai.com/docs/api-reference/chat/create for further details\n")

        print("model : ID of the model to use")
        print("\ntemperature : What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. Lower Values are typically better for translation")
        print("\ntop_p : An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. I generally recommend altering this or temperature but not both.")
        print("\nn : How many chat completion choices to generate for each input message. Do not change this.")
        print("\nstream : If set, partial message deltas will be sent, like in ChatGPT. Tokens will be sent as data-only server-sent events as they become available, with the stream terminated by a data: [DONE] message. See the OpenAI Cookbook for example code. Do not change this.")
        print("\nstop : Up to 4 sequences where the API will stop generating further tokens. Do not change this.")
        print("\nmax_tokens :  The maximum number of tokens to generate in the chat completion. The total length of input tokens and generated tokens is limited by the model's context length. I wouldn't recommend changing this")
        print("\npresence_penalty : Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.")
        print("\nfrequency_penalty : Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.")
        print("\nlogit_bias : Modify the likelihood of specified tokens appearing in the completion. Do not change this.")
        print("\n\nCurrent settings:\n\n")

        print(kijikuRules)

        action = input("\nEnter the name of the setting you want to change, or type 'q' to quit: ").lower()

        if(action == "q"):
            break

        if action not in kijikuRules["open ai settings"]:
            print("Invalid setting name. Please try again.")
            sleep(1)
            continue


        newValue = input("Enter a new value for " + action + " : ")

        kijikuRules[action] = newValue

    with open(r'C:\\ProgramData\\Kudasai\\Kijiku Rules.json', 'w+', encoding='utf-8') as file:
        json.dump(kijikuRules, file)

#-------------------start of initialize_text()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def initialize_text(textToTranslate):

    """
    Set the open api key and create a list full of the sentences we need to translate.
    

    Parameters:
    textToTranslate (string) : file path of txt file provided to Kudasai
    
    Returns:
    text (list) a list of lines to be translated
    """
        
    try:
        with open(r'C:\\ProgramData\\Kudasai\\GPTApiKey.txt', 'r', encoding='utf-8') as file:  ## get saved api key if exists
            apiKey = base64.b64decode((file.read()).encode('utf-8')).decode('utf-8')

        openai.api_key = apiKey

        print("Used saved api key in C:\\ProgramData\\Kudasai\\GPTApiKey.txt")

    except (FileNotFoundError,openai.error.AuthenticationError): ## else try to get api key manually
                
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
                text = [line.strip() for line in file.readlines()]

    try:

        with open(r'C:\\ProgramData\\Kudasai\\Kijiku Rules.json', 'r', encoding='utf-8') as file:
            kijikuRules = json.load(file) 

        return text, kijikuRules

    except:

        default = {
        "open ai settings": 
        {
            "model":"gpt-3.5-turbo",
            "temp":1,
            "top_p":1,
            "n":1,
            "stream":False,
            "stop":None,
            "max_tokens":9223372036854775807,
            "presence_penalty":0,
            "frequency_penalty":0,
            "logit_bias":None
        }
        }

        with open(r'C:\\ProgramData\\Kudasai\\Kijiku Rules.json', 'w+', encoding='utf-8') as file:
            json.dump(default,file)

        with open(r'C:\\ProgramData\\Kudasai\\Kijiku Rules.json', 'r', encoding='utf-8') as file:
            kijikuRules = json.load(file) 

        return text, kijikuRules

#-------------------start-of-output_results()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def output_results():
        
        '''
        outputs results
        '''

        global debugText,jeCheckText,resultText,errorText
        
        debugPath = str(os.getcwd()) + "\\Desktop\\KudasaiOutput\\tlDebug.txt"
        jePath = str(os.getcwd()) + "\\Desktop\\KudasaiOutput\\jeCheck.txt"
        errorPath = str(os.getcwd()) + "\\Desktop\\KudasaiOutput\\errors.txt"
        resultsPath = str(os.getcwd()) + "\\Desktop\\KudasaiOutput\\translatedText.txt"

        with open(debugPath, 'w+', encoding='utf-8') as file:
                file.writelines(debugText)

        with open(jePath, 'w+', encoding='utf-8') as file: 
                file.writelines(jeCheckText)

        with open(resultsPath, 'w+', encoding='utf-8') as file:
                file.writelines(resultText)

        with open(errorPath, 'w+', encoding='utf-8') as file:
                file.writelines(errorText)

        print("\n\nDebug text have been written to : " + debugPath)
        print("\nJ->E text have been written to : " + jePath)
        print("\nTranslated text has been written to : " + resultsPath)
        print("\nError Text has been written to : " + errorPath)

#-------------------start-of-generate_prompt()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def generate_prompt(index):

    '''
    generates prompts but skips punctuation or plain english
    '''

    global text

    prompt = []

    while(index < len(text)):
        sentence = text[index]

        if(len(prompt) < 13):

            if(bool(re.match(r'^[\W_\s\n-]+$', sentence))):
                debugText.append("\n-----------------------------------------------\nSentence : " + sentence + "\nSentence is punctuation... skipping translation\n-----------------------------------------------\n\n")
           
            elif(bool(re.match(r'^[A-Za-z0-9\s\.,\'\?!]+\n*$', sentence))):
                debugText.append("\n-----------------------------------------------\nSentence : " + sentence + "\nSentence is english... skipping translation\n-----------------------------------------------\n\n")
            
            else:
                prompt.append(sentence)
  
        else:
            return prompt, index
        
        index += 1

    return prompt, index

#-------------------start-of-translate()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

import backoff
import openai

@backoff.on_exception(backoff.expo, (openai.error.ServiceUnavailableError, openai.error.RateLimitError, openai.error.Timeout, openai.error.APIError, openai.error.APIConnectionError))
def translate(systemMessage,userMessage,MODEL):

    '''
    translates system and user message
    '''

    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            systemMessage,
            userMessage,
        ],
        temperature=0,
    )

    output = response['choices'][0]['message']['content']
         
    return output


#-------------------start-of-redistribute()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def redistribute(translatedText):

    '''
    puts translated text back into text file
    '''

    global resultText
    
    sentences = translatedText.split(". ")
    for sentence in sentences:
        resultText.append(sentence + ".")

    resultText[-1] = resultText[-1][:-1]

#-------------------start-of-buildMessages()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def buildMessages(systemMessage):

    global text

    '''
    builds messages dict for ai
    '''

    i = 0
    messages = []

    while i < len(text):
        prompt, i = generate_prompt(i)

        prompt = ''.join(prompt)

        system_msg = {}
        system_msg["role"] = "system"
        system_msg["content"] = systemMessage

        messages.append(system_msg)

        model_msg = {}
        model_msg["role"] = "user"
        model_msg["content"] = prompt

        messages.append(model_msg)

    return messages
     
#-------------------start-of-redistribute()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def estimate_cost(messages, model="gpt-3.5-turbo-0301"):

    '''
    attempts to estimate cost, (no idea how accurate)
    '''
    
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")

    if(model == "gpt-3.5-turbo"):
        print("Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301.")
        return estimate_cost(messages, model="gpt-3.5-turbo-0301")
    
    elif(model == "gpt-4"):
        print("Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-0314.")
        return estimate_cost(messages, model="gpt-4-0314")
    
    elif(model == "gpt-3.5-turbo-0301"):
        costPer1000Tokens = 0.002
        tokensPerMessage = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokensPerName = -1  # if there's a name, the role is omitted

    elif(model == "gpt-4-0314"):
        tokensPerMessage = 3
        tokensPerName = 1

    else:
        raise NotImplementedError(f"""numTokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
    
    numTokens = 0

    for message in messages:

        numTokens += tokensPerMessage

        for key, value in message.items():

            numTokens += len(encoding.encode(value))

            if(key == "name"):
                numTokens += tokensPerName

    numTokens += 3  # every reply is primed with <|start|>assistant<|message|>
    minCost = (float(numTokens) / 1000.00) * costPer1000Tokens

    return numTokens,minCost

#-------------------start-of-main()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def commence_translation(japaneseText):

    try:
     
        global debugText,jeCheckText,errorText,resultText,text
        debugText,jeCheckText,errorText,resultText,text = [],[],[],[],japaneseText

        i = 0

        MODEL = "gpt-3.5-turbo"
        systemMessage= "You are a Japanese To English translator. Please remember that you need to translate the narration into English simple past. Try to keep the original formatting and punctuation as well. "

        timeStart = time.time()

        os.system('cls')

        messages = buildMessages(systemMessage)

        numTokens,minCost = estimate_cost(messages,MODEL)

        print("\nEstimated Number of Tokens in Text : " + str(numTokens))
        print("Estimated Minimum Cost of Translation : " + str(minCost) + "\n")

        os.system('pause /P "Press any key to continue with translation..."')

        while(i+2 <= len(messages)):

            os.system('cls')

            print("Trying " + str(i+2) + " of " + str(len(messages)))
            translatedText = translate(messages[i],messages[i+1],MODEL)

            redistribute(translatedText.strip())
            i+=2

        resultText = list(map(lambda x: x + '\n', resultText))

        output_results()

        timeEnd = time.time()

        print("\nMinutes Elapsed : " + str(round((timeEnd - timeStart)/ 60,2)) + "\n")

    except Exception as e:
        print("\nUncaught error has been raised in Kijiku, error is as follows : " + str(e) + "\nOutputting incomplete results\n")
        output_results()


