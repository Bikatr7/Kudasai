import re
import os
import base64
import openai
import backoff
import tiktoken
import time
import json
import spacy
import shutil

from time import sleep
from typing import List
from openai.error import APIConnectionError, APIError, AuthenticationError, ServiceUnavailableError, RateLimitError, Timeout

from Util import associated_functions

'''
Kijiku.py

Original Author: Seinu#7854

'''

#-------------------start-of-change_settings()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def change_settings(kijikuRules:dict ,configDir:str) -> None:

    """

    Allows the user to change the settings of the KijikuRules.json file\n

    Parameters:\n
    kijikuRules (dict - string) a dictionary of the rules kijiku will follow\n
    configDir (string) the path to the config directory\n

    Returns:\n
    None\n

    """
     
    while(True):

        associated_functions.clear_console()

        print("See https://platform.openai.com/docs/api-reference/chat/create for further details\n")

        print("\nmodel : ID of the model to use. As of right now, Kijiku only works with 'chat' models.")
        print("\ntemperature : What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. Lower Values are typically better for translation")
        print("\ntop_p : An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. I generally recommend altering this or temperature but not both.")
        print("\nn : How many chat completion choices to generate for each input message. Do not change this.")
        print("\nstream : If set, partial message deltas will be sent, like in ChatGPT. Tokens will be sent as data-only server-sent events as they become available, with the stream terminated by a data: [DONE] message. See the OpenAI Cookbook for example code. Do not change this.")
        print("\nstop : Up to 4 sequences where the API will stop generating further tokens. Do not change this.")
        print("\nmax_tokens :  The maximum number of tokens to generate in the chat completion. The total length of input tokens and generated tokens is limited by the model's context length. I wouldn't recommend changing this")
        print("\npresence_penalty : Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.")
        print("\nfrequency_penalty : Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.")
        print("\nlogit_bias : Modify the likelihood of specified tokens appearing in the completion. Do not change this.")
        print("\nsystem_message : Instructions to the model. Do not change this unless you know what you're doing.")
        print("\nmessage_mode : 1 or 2. 1 means the system message will actually be treated as a system message. 2 means it'll be treating as a user message. 1 is recommend for gpt-4 otherwise either works.")
        print("\nnum_lines : the number of lines to be built into a prompt at once. Theoretically, more lines would be more cost effective, but other complications may occur with higher lines.")
        print("\nsentence_fragmenter_mode : 1 or 2 or 3 (1 - via regex and other nonsense, 2 - NLP via spacy, 3 - None (Takes formatting and text directly from ai return)) the api can sometimes return a result on a single line, so this determines the way Kijiku fragments the sentences if at all.")
        
        print("\n\nPlease note that while logit_bias and max_tokens can be changed, Kijiku does not currently do anything with them.")

        print("\n\nCurrent settings:\n\n")

        for key,value in kijikuRules["open ai settings"].items(): ## print out the current settings
             print(key + " : " + str(value))

        action = input("\nEnter the name of the setting you want to change, type d to reset to default, or type 'q' to continue: ").lower()

        if(action == "q"): ## if the user wants to continue, do so
            break

        elif(action == "d"): ## if the user wants to reset to default, do so
            reset_kijiku_rules(configDir)

            with open(os.path.join(configDir,'Kijiku Rules.json'), 'r', encoding='utf-8') as file:
                kijikuRules = json.load(file) 


        elif(action not in kijikuRules["open ai settings"]):
            print("Invalid setting name. Please try again.")
            sleep(1)
            continue

        else:

            newValue = input("\nEnter a new value for " + action + " : ")

            kijikuRules["open ai settings"][action] = newValue

    with open(os.path.join(configDir,'Kijiku Rules.json'), 'w+', encoding='utf-8') as file:
        json.dump(kijikuRules, file)

#-------------------start-of-reset_kijiku_rules()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def reset_kijiku_rules(configDir:str) -> None:

    """

    resets the kijikuRules json to default\n

    Parameters:\n
    configDir (string) the path to the config directory\n

    Returns:\n
    None\n

    """
     
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
        "logit_bias":None,
        "system_message":"You are a Japanese To English translator. Please remember that you need to translate the narration into English simple past. Try to keep the original formatting and punctuation as well. ",
        "message_mode":1,
        "num_lines":13,
        "sentence_fragmenter_mode":1
    }
    }

    with open(os.path.join(configDir,'Kijiku Rules.json'), 'w+', encoding='utf-8') as file:
        json.dump(default,file)

    associated_functions.clear_console()
     
#-------------------start-of-initialize_text()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def initialize_text(textToTranslate:str, configDir:str) -> tuple[List[str],dict]: 

    """

    Set the open api key and create a list full of the sentences we need to translate.\n
    
    Parameters:\n
    textToTranslate (string) a path to the text kijiku will translate\n
    configDir (string) a path to the config directory\n
    
    Returns:\n
    text (list - string) a list of japanese lines we need to translate\n
    kijikuRules (dict) a dictionary of the rules for kijiku\n

    """

    try:
        with open(os.path.join(configDir,'GPTApiKey.txt'), 'r', encoding='utf-8') as file:  ## get saved api key if exists
            apiKey = base64.b64decode((file.read()).encode('utf-8')).decode('utf-8')

        openai.api_key = apiKey

        print("Used saved api key in " + os.path.join(configDir,'GPTApiKey.txt')) ## if valid save the api key

    except (FileNotFoundError,AuthenticationError): ## else try to get api key manually
            
            if(os.path.isfile("C:\\ProgramData\\Kudasai\\GPTApiKey.txt") == True): ## if the api key is in the old location, delete it
                os.remove("C:\\ProgramData\\Kudasai\\GPTApiKey.txt")
                print("r'C:\\ProgramData\\Kudasai\\GPTApiKey.txt' was deleted due to Kudasai switching to user storage\n")
                
            apiKey = input("DO NOT DELETE YOUR COPY OF THE API KEY\n\nPlease enter the openapi key you have : ")

            try: ## if valid save the api key
 
                openai.api_key = apiKey

                if(os.path.isdir(configDir) == False):
                    os.mkdir(configDir, 0o666)
                    print(configDir + " created due to lack of the folder")

                    sleep(.1)
                            
                if(os.path.isfile(os.path.join(configDir,'GPTApiKey.txt')) == False):
                    print(os.path.join(configDir,'GPTApiKey.txt') + " was created due to lack of the file")

                    with open(os.path.join(configDir,'GPTApiKey.txt'), 'w+', encoding='utf-8') as key: 
                        key.write(base64.b64encode(apiKey.encode('utf-8')).decode('utf-8'))

                    sleep(.1)
                   
            except AuthenticationError: ## if invalid key exit
                     
                associated_functions.clear_console()
                        
                print("Authorization error with creating translator object, please double check your api key as it appears to be incorrect.\n")
                associated_functions.pause_console()
                        
                exit()

            except Exception as e: ## other error, alert user and raise it

                associated_functions.clear_console()
                        
                print("Unknown error with creating translator object, The error is as follows " + str(e)  + "\nThe exception will now be raised.\n")
                associated_functions.pause_console()

                raise e
                
    with open(textToTranslate, 'r', encoding='utf-8') as file:  ## strips each line of the text to translate
                text = [line.strip() for line in file.readlines()]

    associated_functions.clear_console()

    try: ## try to load the kijiku rules

        if(os.path.isfile(r'C:\\ProgramData\\Kudasai\\Kijiku Rules.json') == True): ## if the kijiku rules are in the old location, copy them to the new one and delete the old one
            shutil.copyfile(r'C:\\ProgramData\\Kudasai\\Kijiku Rules.json', os.path.join(configDir,'Kijiku Rules.json'))

            os.remove(r'C:\\ProgramData\\Kudasai\\Kijiku Rules.json')
            print("r'C:\\ProgramData\\Kudasai\\Kijiku Rules.json' was deleted due to Kudasai switching to user storage\n\nYour settings have been copied to " + configDir + "\n\n")
            sleep(1)
            associated_functions.clear_console()

        with open(os.path.join(configDir,'Kijiku Rules.json'), 'r', encoding='utf-8') as file:
            kijikuRules = json.load(file) 

        return text, kijikuRules

    except: ## if the kijiku rules don't exist, create them
         
        reset_kijiku_rules(configDir)

        with open(os.path.join(configDir,'Kijiku Rules.json'), 'r', encoding='utf-8') as file:
            kijikuRules = json.load(file) 

        return text, kijikuRules

#-------------------start-of-generate_prompt()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def generate_prompt(index:int, promptSize:int) -> tuple[List[str],int]:

    '''

    generates prompts but skips punctuation or plain english\n

    Parameters:\n
    index (int) an int representing where we currently are in the text file\n
    promptSize (int) an int representing how many lines the prompt will have\n

    Returns:\n
    prompt (list - string) a list of japanese lines that will be assembled into messages\n
    index (int) an updated int representing where we currently are in the text file\n

    '''

    global text

    prompt = []

    while(index < len(text)):
        sentence = text[index]

        if(len(prompt) < promptSize):

            if(any(char in sentence for char in ["▼", "△", "◇"])):
                prompt.append(sentence + '\n')
                debugText.append("\n-----------------------------------------------\nSentence : " + sentence + "\nSentence is a pov change... leaving intact\n-----------------------------------------------\n\n")

            elif bool(re.match(r'^[\W_\s\n-]+$', sentence)) and not any(char in sentence for char in ["」", "「", "«", "»"]):
                debugText.append("\n-----------------------------------------------\nSentence : " + sentence + "\nSentence is punctuation... skipping\n-----------------------------------------------\n\n")
           
            elif(bool(re.match(r'^[A-Za-z0-9\s\.,\'\?!]+\n*$', sentence))):
                debugText.append("\n-----------------------------------------------\nSentence : " + sentence + "\nSentence is english... skipping\n-----------------------------------------------\n\n")

            else:
                prompt.append(sentence + "\n")
  
        else:
            return prompt, index
        
        index += 1

    return prompt, index

#-------------------start-of-translate()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@backoff.on_exception(backoff.expo, (ServiceUnavailableError, RateLimitError, Timeout, APIError, APIConnectionError))
def translate(systemMessage:dict, userMessage:dict, MODEL:str,kijikuRules:dict) -> str:

    '''

    translates system and user message\n

    Parameters:\n
    systemMessage (dict - string) a dictionary that contains the system message\n
    userMessage (dict - string) a dictionary that contains the user message\n
    MODEL (string) a constant that represents which model we will be using\n
    kijikuRules (dict - string) a dictionary of rules that kijiku follows as it translates\n

    Returns:\n
    output (string) a string that gpt gives to us\n

    '''

    ## max_tokens and logit bias are currently excluded due to a lack of need, and the fact that i am lazy

    global debugText,jeCheckText

    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            systemMessage,
            userMessage,
        ],

        temperature = float(kijikuRules["open ai settings"]["temp"]),
        top_p = float(kijikuRules["open ai settings"]["top_p"]),
        n = int(kijikuRules["open ai settings"]["top_p"]),
        stream = kijikuRules["open ai settings"]["stream"],
        stop = kijikuRules["open ai settings"]["stop"],
        presence_penalty = float(kijikuRules["open ai settings"]["presence_penalty"]),
        frequency_penalty = float(kijikuRules["open ai settings"]["frequency_penalty"]),

    )

    ## note, pylance flags this as a 'GeneralTypeIssue', however i see nothing wrong with it, and it works fine
    output = response['choices'][0]['message']['content'] # type: ignore

    debugText.append("\nPrompt was : \n" + userMessage["content"] + "\n")

    debugText.append("-------------------------\nResponse from GPT was : \n\n" + output + "\n")
         
    jeCheckText.append("\n-------------------------\n"+ str(userMessage["content"]) + "\n\n")
    
    return output

#-------------------start-of-redistribute()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def redistribute(translatedText:str, sentence_fragmenter_mode:int) -> None:

    '''

    puts translated text back into text file

    Parameters:
    translatedText (string) a string that is the result of gpt's translation
    sentence_fragmenter_mode (int) 1, 2, or 3 representing the mode of sentence fragmenter

    Returns:
    None

    '''
    global resultText,jeCheckText,debugText

    if(sentence_fragmenter_mode == 1): # mode 1 is the default mode, uses regex and other nonsense to split sentences

        sentences = re.findall(r"(.*?(?:(?:\"|\'|-|~|!|\?|%|\(|\)|\.\.\.|\.|---|\[|\])))(?:\s|$)", translatedText)

        patched_sentences = []
        buildString = None

        debugText.append("\n-------------------------\nDistributed result was : \n\n")

        for sentence in sentences:
            if(sentence.startswith("\"") and not sentence.endswith("\"") and buildString is None):
                buildString = sentence
                continue
            elif(not sentence.startswith("\"") and sentence.endswith("\"") and buildString is not None):
                buildString += f" {sentence}"
                patched_sentences.append(buildString)
                buildString = None
                continue
            elif(buildString is not None):
                buildString += f" {sentence}"
                continue

            resultText.append(sentence + '\n')
            jeCheckText.append(sentence + '\n')
            debugText.append(sentence + '\n')

        for i in range(len(resultText)):
            if resultText[i] in patched_sentences:
                index = patched_sentences.index(resultText[i])
                resultText[i] = patched_sentences[index]

    elif(sentence_fragmenter_mode == 2): # mode 2 uses spacy to split sentences

        nlp = spacy.load("en_core_web_lg")

        doc = nlp(translatedText)
        sentences = [sent.text for sent in doc.sents]
        
        debugText.append("\n-------------------------\nDistributed result was : \n\n")

        for sentence in sentences:
            resultText.append(sentence + '\n')
            jeCheckText.append(sentence + '\n')
            debugText.append(sentence + '\n')

    elif(sentence_fragmenter_mode == 3): # mode 3 just assumes gpt formatted it properly
        
        resultText.append(translatedText + '\n')
        jeCheckText.append(translatedText + '\n')

#-------------------start-of-buildMessages()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def buildMessages(systemMessage:str, message_mode:int, promptSize:int) -> List[dict]:

    '''

    builds messages dict for ai

    Parameters:
    systemMessage (string) a string that gives instructions to the gpt chat model
    message_mode (int) the method of assembling the messages
    promptSize (int) the size of the prompt that will be given to the model

    Returns:
    messages (list - dict - string) the assembled messages that will be given to the model, it's a list of dicts that contain strings

    '''

    global text,debugText

    i = 0
    messages = []

    while i < len(text):
        prompt, i = generate_prompt(i,promptSize)

        prompt = ''.join(prompt)

        if(message_mode == 1):
            system_msg = {}
            system_msg["role"] = "system"
            system_msg["content"] = systemMessage

        else:
            system_msg = {}
            system_msg["role"] = "user"
            system_msg["content"] = systemMessage

        messages.append(system_msg)

        model_msg = {}
        model_msg["role"] = "user"
        model_msg["content"] = prompt

        messages.append(model_msg)

    debugText.append("\nMessages\n-------------------------\n\n")

    i = 0

    for message in messages:

        i+=1

        if(i % 2 == 0):

            debugText.append(str(message) + "\n\n")
      
        else:

            debugText.append(str(message) + "\n")

    return messages
     
#-------------------start-of-estimated_cost()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def estimate_cost(messages, model,configDir) -> None:

    '''

    attempts to estimate cost.\n
 
    Parameters:\n
    messages (dict - string) the assembled messages that will be given to the model\n
    model (string) a constant that represents which model we will be using\n
    configDir (string) the directory of the config file\n

    Returns:\n
    None\n

    '''

    global fromGui
    
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")

    if(model == "gpt-3.5-turbo"):
        print("Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301.")
        return estimate_cost(messages, model="gpt-3.5-turbo-0301",configDir=configDir)
    
    elif(model == "gpt-4"):
        print("Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-0314.")
        return estimate_cost(messages, model="gpt-4-0314",configDir=configDir)
    
    elif(model == "gpt-3.5-turbo-0301"):
        costPer1000Tokens = 0.002
        tokensPerMessage = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokensPerName = -1  # if there's a name, the role is omitted

    elif(model == "gpt-4-0314"):
        costPer1000Tokens = 0.006
        tokensPerMessage = 3
        tokensPerName = 1

    else:
        raise NotImplementedError(f"""Kudasai does not support : {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
    
    numTokens = 0

    for message in messages:

        numTokens += tokensPerMessage

        for key, value in message.items():

            numTokens += len(encoding.encode(value))

            if(key == "name"):
                numTokens += tokensPerName

    numTokens += 3  # every reply is primed with <|start|>assistant<|message|>
    minCost = round((float(numTokens) / 1000.00) * costPer1000Tokens, 5)

    debugText.append("\nEstimated Tokens in Messages : " + str(numTokens))
    debugText.append("\nEstimated Minimum Cost : " + str(minCost) + '\n')

    if(not fromGui):
        print("\nEstimated Number of Tokens in Text : " + str(numTokens))
        print("Estimated Minimum Cost of Translation : " + str(minCost) + "\n")
    else:
        with open(os.path.join(configDir,"guiTempTranslationLog.txt"), "a+", encoding="utf-8") as file: # Write the text to a temporary file
            file.write("\nEstimated Number of Tokens in Text : " + str(numTokens) + "\n")
            file.write("\nEstimated Minimum Cost of Translation : " + str(minCost) + "\n\n")


#-------------------start-of-main()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def commence_translation(japaneseText,scriptDir,configDir,isGui) -> None:

    """
        
    Uses all the other functions to translate the text provided by Kudasai\n

    Parameters:\n
    japaneseText (list - string) a list of japanese lines that we need to translate\n
    scriptDir (string) the path of the directory that holds Kudasai.py\n
    configDir (string) the path of the directory that holds Kijiku Rules.json\n
    
    Returns:\n
    None\n

    """
    
    try:
     
        global debugText,jeCheckText,errorText,resultText,text,fromGui
        debugText,jeCheckText,errorText,resultText,text,fromGui = [],[],[],[],japaneseText,isGui

        i = 0

        debugText.append("Kijiku Activated\n\n")
        debugText.append("Settings are as follows : \n\n")

        with open(os.path.join(configDir,'Kijiku Rules.json'), 'r', encoding='utf-8') as file:
            kijikuRules = json.load(file) 

        for key,value in kijikuRules["open ai settings"].items():
            debugText.append(key + " : " + str(value) +'\n')
            
        MODEL = kijikuRules["open ai settings"]["model"]
        systemMessage = kijikuRules["open ai settings"]["system_message"]
        message_mode = int(kijikuRules["open ai settings"]["message_mode"])
        promptSize = int(kijikuRules["open ai settings"]["num_lines"])
        sentence_fragmenter_mode = int(kijikuRules["open ai settings"]["sentence_fragmenter_mode"])

        timeStart = time.time()

        associated_functions.clear_console()

        debugText.append("\nStarting Prompt Building\n-------------------------\n")

        messages = buildMessages(systemMessage,message_mode,promptSize)

        estimate_cost(messages,MODEL,configDir)

        if(fromGui == False):
            associated_functions.pause_console("Press any key to continue with translation...")

        debugText.append("\nStarting Translation\n-------------------------")

        while(i+2 <= len(messages)):

            associated_functions.clear_console()

            print("Trying " + str(i+2) + " of " + str(len(messages)))
            debugText.append("\n\n-------------------------\nTrying " + str(i+2) + " of " + str(len(messages)) + "\n-------------------------\n")

            translatedText = translate(messages[i],messages[i+1],MODEL,kijikuRules)

            redistribute(translatedText,sentence_fragmenter_mode)

            i+=2

        associated_functions.output_results(scriptDir,configDir,debugText,jeCheckText,resultText,errorText,fromGui)

        timeEnd = time.time()

        if(fromGui):
                with open(os.path.join(configDir,"guiTempTranslationLog.txt"), "a+", encoding="utf-8") as file: # Write the text to a temporary file
                        file.write("\nTime Elapsed : " + associated_functions.get_elapsed_time(timeStart, timeEnd) + "\n\n")
        
        else:
                print("\nTime Elapsed : " + associated_functions.get_elapsed_time(timeStart, timeEnd))

    except Exception as e: 

        print("\nUncaught error has been raised in Kijiku, error is as follows : " + str(e) + "\nOutputting incomplete results\n")

        errorText.append("\nUncaught error has been raised in Kijiku, error is as follows : " + str(e) + "\nOutputting incomplete results\n")

        if(fromGui):
            with open(os.path.join(configDir,"guiTempTranslationLog.txt"), "a+", encoding="utf-8") as file: # Write the text to a temporary file
                file.write("\nUncaught error has been raised in Kijiku, error is as follows : " + str(e) + "\nOutputting incomplete results\n")

        associated_functions.output_results(scriptDir,configDir,debugText,jeCheckText,resultText,errorText,fromGui)


