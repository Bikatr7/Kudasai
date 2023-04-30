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

from openai.error import APIConnectionError, APIError, AuthenticationError, ServiceUnavailableError, RateLimitError, Timeout

'''
Kijiku.py

Original Author: Seinu#7854

'''

#-------------------start of change_settings()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def change_settings(kijikuRules,configDir):

    """

    Allows the user to change the settings of the KijikuRules.json file

    Parameters:
    kijikuRules (dict - string) a dictionary of the rules kijiku will follow
    configDir (string) the path to the config directory

    Returns:
    None

    """
     
    while(True):

        os.system('cls')

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
        print("\nnum_lines : the number of lines to be built into a prompt at once. Theoretically, more lines would be more cost effective, but other complications occur with higher lines.")
        print("\nsentence_fragmenter_mode : 1 or 2 (1 - via regex and other nonsense, 2 - via spacy ) the api returns a result on a single line, so this determines the way Kijiku fragments the sentences.")
        print("\n\nCurrent settings:\n\n")

        for key,value in kijikuRules["open ai settings"].items(): ## print out the current settings
             print(key + " : " + str(value))

        action = input("\nEnter the name of the setting you want to change, type d to reset to default, or type 'q' to continue: ").lower()

        if(action == "q"): ## if the user wants to quit, do so
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

#-------------------start of reset_kijiku_rules()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def reset_kijiku_rules(configDir):

    """

    resets the kijikuRules json to default

    Parameters:
    None

    Returns:
    None

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

    os.system('cls')
     
#-------------------start of initialize_text()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def initialize_text(textToTranslate,configDir):

    """

    Set the open api key and create a list full of the sentences we need to translate.
    
    Parameters:
    textToTranslate (string) a path to the text kijiku will translate
    configDir (string) a path to the config directory
    
    Returns:
    text (list - string) a list of japanese lines we need to translate

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

    os.system('cls')

    try:

        if(os.path.isfile(r'C:\\ProgramData\\Kudasai\\Kijiku Rules.json') == True): ## if the kijiku rules are in the old location, copy them to the new one and delete the old one
            shutil.copyfile(r'C:\\ProgramData\\Kudasai\\Kijiku Rules.json', os.path.join(configDir,'Kijiku Rules.json'))

            os.remove(r'C:\\ProgramData\\Kudasai\\Kijiku Rules.json')
            print("r'C:\\ProgramData\\Kudasai\\Kijiku Rules.json' was deleted due to Kudasai switching to user storage\n\nYour settings have been copied to " + configDir + "\n\n")
            sleep(1)
            os.system('cls')

        with open(os.path.join(configDir,'Kijiku Rules.json'), 'r', encoding='utf-8') as file:
            kijikuRules = json.load(file) 

        return text, kijikuRules

    except:
         
        reset_kijiku_rules(configDir)

        with open(os.path.join(configDir,'Kijiku Rules.json'), 'r', encoding='utf-8') as file:
            kijikuRules = json.load(file) 

        return text, kijikuRules

#-------------------start-of-output_results()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def output_results(scriptDir):
        
    '''

    Outputs results to several txt files

    Parameters:
    scriptDir (string) the path of the directory that holds Kudasai.py

    Returns:
    None

    '''

    global debugText,jeCheckText,resultText,errorText
        
    outputDir = os.path.join(scriptDir, "KudasaiOutput")

    if(not os.path.join(outputDir)):
        os.mkdir(outputDir)

    debugPath = os.path.join(outputDir, "tlDebug.txt")
    jePath = os.path.join(outputDir, "jeCheck.txt")
    errorPath = os.path.join(outputDir, "errors.txt")
    resultsPath = os.path.join(outputDir, "translatedText.txt")
    
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

def generate_prompt(index,promptSize):

    '''

    generates prompts but skips punctuation or plain english

    Parameters:
    index (int) an int representing where we currently are in the text file
    promptSize (int) an int representing how many lines the prompt will have

    Returns:
    prompt (list - string) a list of japanese lines that will be assembled into messages
    index (int) an updated int representing where we currently are in the text file

    '''

    global text

    prompt = []

    while(index < len(text)):
        sentence = text[index]

        if(len(prompt) < promptSize):

            if(bool(re.match(r'^[\W_\s\n-]+$', sentence))):
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
def translate(systemMessage,userMessage,MODEL,kijikuRules):

    '''

    translates system and user message

    Parameters:
    systemMessage (string) a string that gives instructions to the gpt chat model
    userMessage (string) a string that gpt will alter based on the systemMessage
    MODEL (string) a constant that represents which model we will be using
    kijikuRules (dict - string) a dictionary of rules that kijiku follows as it translates

    Returns:
    output (string) a string that gpt gives to us

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

    debugText.append("\nResponse from GPT was : \n" + output)
         
    jeCheckText.append("\n-------------------------\n"+ str(userMessage["content"]) + "\n\n")
    
    return output

#-------------------start-of-redistribute()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def redistribute(translatedText,sentence_fragmenter_mode):

    '''

    puts translated text back into text file

    Parameters:
    translatedText (string) a string that gpt gives to us
    sentence_fragmenter_mode (int) an int (1 or 2) representing which mode of sentence fragmenting will be done

    Returns:
    None

    '''
    global resultText

    if(sentence_fragmenter_mode == 1):

        sentences = re.findall(r"(.+?(?:\"|\'|-|~|!|\?|%|\(|\)|\.\.\.|\.|---))(?:\s|$)", translatedText)

        patched_sentences = []
        built_string = None

        for sentence in sentences:
            if(sentence.startswith("\"") and not sentence.endswith("\"") and built_string is None):
                built_string = sentence
                continue
            elif(not sentence.startswith("\"") and sentence.endswith("\"") and built_string is not None):
                built_string += f" {sentence}"
                patched_sentences.append(built_string)
                built_string = None
                continue
            elif(built_string is not None):
                built_string += f" {sentence}"
                continue

            resultText.append(sentence)
            jeCheckText.append(sentence + '\n')
    
    else:

        nlp = spacy.load("en_core_web_lg")

        doc = nlp(translatedText)
        sentences = [sent.text.strip() for sent in doc.sents]
        
        for sentence in sentences:
            resultText.append(sentence)
            jeCheckText.append(sentence + '\n')

#-------------------start-of-buildMessages()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def buildMessages(systemMessage,message_mode,promptSize):

    '''
    builds messages dict for ai

    Parameters:
    systemMessage (string) a string that gives instructions to the gpt chat model
    mode (int) the method of assembling the messages

    Returns:
    messages (dict - string) the assembled messages that will be given to the model
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

    debugText.append("Messages : \n\n")

    i = 0

    for message in messages:

        i+=1

        if(i % 2 == 0):

            debugText.append(str(message) + "\n\n")
      
        else:

            debugText.append(str(message) + "\n")



    return messages
     
#-------------------start-of-estimated_cost()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def estimate_cost(messages, model):

    '''

    attempts to estimate cost, (no idea how accurate)
 
    Parameters:
    messages (dict - string) the assembled messages that will be given to the model
    model (string) a constant that represents which model we will be using

    Returns:
    numTokens (int) the estimated number of tokens in the messages
    cost (double) the estimated cost of translating messages

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
    minCost = (float(numTokens) / 1000.00) * costPer1000Tokens

    debugText.append("\nEstimated Tokens in Messages : " + str(numTokens))
    debugText.append("\nEstimated Minimum Cost : " + str(minCost) + '\n')

    return numTokens,minCost

#-------------------start-of-main()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def commence_translation(japaneseText,scriptDir,configDir):

    """
        
    Uses all the other functions to translate the text provided

    Parameters:
    japaneseText (list - string) a list of japanese lines that we need to translate
    scriptDir (string) the path of the directory that holds Kudasai.py

    Returns: 
    None

    """

    try:
     
        global debugText,jeCheckText,errorText,resultText,text
        debugText,jeCheckText,errorText,resultText,text = [],[],[],[],japaneseText

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

        os.system('cls')

        debugText.append("\nStarting\n-------------------------\n")

        messages = buildMessages(systemMessage,message_mode,promptSize)

        numTokens,minCost = estimate_cost(messages,MODEL)

        print("\nEstimated Number of Tokens in Text : " + str(numTokens))
        print("Estimated Minimum Cost of Translation : " + str(minCost) + "\n")

        os.system('pause /P "Press any key to continue with translation..."')

        while(i+2 <= len(messages)):

            os.system('cls')

            print("Trying " + str(i+2) + " of " + str(len(messages)))
            debugText.append("\n\n-------------------------\nTrying " + str(i+2) + " of " + str(len(messages)) + "\n-------------------------\n")

            translatedText = translate(messages[i],messages[i+1],MODEL,kijikuRules)

            redistribute(translatedText.strip(),sentence_fragmenter_mode)

            i+=2

        resultText = list(map(lambda x: x + '\n', resultText))

        output_results(scriptDir)

        timeEnd = time.time()

        print("\nMinutes Elapsed : " + str(round((timeEnd - timeStart)/ 60,2)) + "\n")

    except Exception as e:
        print("\nUncaught error has been raised in Kijiku, error is as follows : " + str(e) + "\nOutputting incomplete results\n")
        output_results(scriptDir)


