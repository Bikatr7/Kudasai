## built in modules
import base64
import json
import shutil
import re
import os
import time
import typing
import ctypes

## third party modules
import openai
import backoff
import tiktoken
import spacy

from openai.error import APIConnectionError, APIError, AuthenticationError, ServiceUnavailableError, RateLimitError, Timeout

## custom modules
from Modules.preloader import preloader

##-------------------start-of-Kijiku--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Kijiku:

    """
    
    Kijiku is a secondary class that is used to interact with the OpenAI API.
    
    """

##-------------------start-of-__init__()--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, inc_text_to_translate:str, inc_preloader:preloader) -> None:

        """

        Constructor for the Kijiku class.\n

        Parameters:\n
        inc_text_to_translate (string) : the path to the text file to translate.\n
        inc_preloader (preloader) : the preloader object.\n

        Returns:\n
        None.\n

        """

        ## the preloader object
        self.preloader = inc_preloader
        
        ## the text to translate
        self.text_to_translate =  [line for line in inc_text_to_translate.split('\n')]

        ## the translated text
        self.translated_text = []

        ## the text for j-e checking
        self.je_check_text = []

        ## the text for errors that occur during translation
        self.error_text = []

        ## the messages that will be sent to the api, contains a system message and a model message, system message is the instructions,
        ## model message is the text that will be translated  
        self.messages = []

##-------------------start-of-reset()--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def reset(self):
            
        """

        resets the Kijiku object\n

        Parameters:\n
        self (object - Kijiku) : the Kijiku object.\n

        Returns:\n
        None\n

        """

        self.japanese_text = []
        self.debug_text = []
        self.translated_text = []
        self.je_check_text = []
        self.error_text = []
        self.messages = []

##-------------------start-of-check-settings()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def check_settings(self):

        print("Are these settings okay? (1 for yes or 2 for no) : \n\n")

        for key, value in self.kijiku_rules["open ai settings"].items():
            print(key + " : " + str(value))

        if(input("\n") == "1"):
            pass
        else:
            self.change_settings()

        toolkit.clear_console()

##-------------------start-of-translate()--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def translate(self,text_to_translate:str) -> None:

        """

        Translate the text in the file at the path given.\n

        Parameters:\n
        self (object - Kijiku) : the Kijiku object.\n
        text_to_translate (string) : the path to the text file to translate.\n

        Returns:\n
        None\n

        """

        self.reset()
        
        self.initialize(text_to_translate)

        self.validate_json()

        if(not self.from_gui):
            self.check_settings()

        self.commence_translation()

##-------------------start-of-initialize()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def initialize(self,text_to_translate:str) -> None:

        """

        Sets the open api key and creates a list full of the sentences we need to translate.\n
        
        Parameters:\n
        self (object - Kijiku) : the Kijiku object.\n
        text_to_translate (string) a path to the text kijiku will translate\n
        
        Returns:\n
        None\n

        """

        try:
            with open(os.path.join(self.config_dir,'GPTApiKey.txt'), 'r', encoding='utf-8') as file:  ## get saved api key if exists
                api_key = base64.b64decode((file.read()).encode('utf-8')).decode('utf-8')

            openai.api_key = api_key
        
            print("Used saved api key in " + os.path.join(self.config_dir,'GPTApiKey.txt')) ## if valid save the api key
            time.sleep(.7)

        except (FileNotFoundError,AuthenticationError): ## else try to get api key manually
                
            if(os.path.isfile("C:\\ProgramData\\Kudasai\\GPTApiKey.txt") == True): ## if the api key is in the old location, delete it
                os.remove("C:\\ProgramData\\Kudasai\\GPTApiKey.txt")
                print("r'C:\\ProgramData\\Kudasai\\GPTApiKey.txt' was deleted due to Kudasai switching to user storage\n")
                
            api_key = input("DO NOT DELETE YOUR COPY OF THE API KEY\n\nPlease enter the openapi key you have : ")

            try: ## if valid save the api key

                openai.api_key = api_key

                if(os.path.isdir(self.config_dir) == False):
                    os.mkdir(self.config_dir, 0o666)
                    print(self.config_dir + " created due to lack of the folder")

                    time.sleep(.1)
                            
                if(os.path.isfile(os.path.join(self.config_dir,'GPTApiKey.txt')) == False):
                    print(os.path.join(self.config_dir,'GPTApiKey.txt') + " was created due to lack of the file")

                    with open(os.path.join(self.config_dir,'GPTApiKey.txt'), 'w+', encoding='utf-8') as key: 
                        key.write(base64.b64encode(api_key.encode('utf-8')).decode('utf-8'))

                    time.sleep(.1)
                
            except AuthenticationError: ## if invalid key exit
                    
                toolkit.clear_console()
                        
                print("Authorization error with creating translator object, please double check your api key as it appears to be incorrect.\n")
                toolkit.pause_console()
                        
                exit()

            except Exception as e: ## other error, alert user and raise it

                toolkit.clear_console()
                        
                print("Unknown error with creating translator object, The error is as follows " + str(e)  + "\nThe exception will now be raised.\n")
                toolkit.pause_console()

                raise e
                    
        with open(text_to_translate, 'r', encoding='utf-8') as file:  ## strips each line of the text to translate
            self.japanese_text = [line.strip() for line in file.readlines()]

        toolkit.clear_console()

        try: ## try to load the kijiku rules

            if(os.path.isfile(r'C:\\ProgramData\\Kudasai\\Kijiku Rules.json') == True): ## if the kijiku rules are in the old location, copy them to the new one and delete the old one
                shutil.copyfile(r'C:\\ProgramData\\Kudasai\\Kijiku Rules.json', os.path.join(self.config_dir,'Kijiku Rules.json'))

                os.remove(r'C:\\ProgramData\\Kudasai\\Kijiku Rules.json')
                print("r'C:\\ProgramData\\Kudasai\\Kijiku Rules.json' was deleted due to Kudasai switching to user storage\n\nYour settings have been copied to " + self.config_dir + "\n\n")
                time.sleep(1)
                toolkit.clear_console()

            with open(os.path.join(self.config_dir,'Kijiku Rules.json'), 'r+', encoding='utf-8') as file:
                self.kijiku_rules = json.load(file) 

        except: ## if the kijiku rules don't exist, create them
            
            self.reset_kijiku_rules()

            with open(os.path.join(self.config_dir,'Kijiku Rules.json'), 'r', encoding='utf-8') as file:
                self.kijiku_rules = json.load(file) 

##-------------------start-of-commence_translation()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def commence_translation(self) -> None:

        """
            
        Uses all the other functions to translate the text provided by Kudasai\n

        Parameters:\n
        self (object - Kijiku) : the Kijiku object.\n
        
        Returns:\n
        None\n

        """
        
        try:
        
            i = 0

            self.debug_text.append("Kijiku Activated\n\nSettings are as follows : \n\n")

            with open(os.path.join(self.config_dir,'Kijiku Rules.json'), 'r', encoding='utf-8') as file:
                self.kijiku_rules = json.load(file) 

            for key,value in self.kijiku_rules["open ai settings"].items():
                self.debug_text.append(key + " : " + str(value) +'\n')
                
            self.MODEL = self.kijiku_rules["open ai settings"]["model"]
            self.system_message = self.kijiku_rules["open ai settings"]["system_message"]
            self.message_mode = int(self.kijiku_rules["open ai settings"]["message_mode"])
            self.prompt_size = int(self.kijiku_rules["open ai settings"]["num_lines"])
            self.sentence_fragmenter_mode = int(self.kijiku_rules["open ai settings"]["sentence_fragmenter_mode"])
            self.je_check_mode = int(self.kijiku_rules["open ai settings"]["je_check_mode"])

            time_start = time.time()

            toolkit.clear_console()

            self.debug_text.append("\nStarting Prompt Building\n-------------------------\n")

            self.build_messages()

            self.estimate_cost()

            if(self.from_gui == False):
                toolkit.pause_console("Press any key to continue with translation...")

            self.debug_text.append("\nStarting Translation\n-------------------------")

            while(i+2 <= len(self.messages)):

                toolkit.clear_console()

                print("Trying " + str(i+2) + " of " + str(len(self.messages)))
                self.debug_text.append("\n\n-------------------------\nTrying " + str(i+2) + " of " + str(len(self.messages)) + "\n-------------------------\n")

                translated_message = self.translate_message(self.messages[i],self.messages[i+1])

                self.redistribute(translated_message)

                i+=2

            self.output_results()

            time_end = time.time()

            if(self.from_gui):
                with open(os.path.join(self.config_dir,"guiTempTranslationLog.txt"), "a+", encoding="utf-8") as file: ## Write the text to a temporary file
                    file.write("\nTime Elapsed : " + toolkit.get_elapsed_time(time_start, time_end) + "\n\n")
            
            else:
                print("\nTime Elapsed : " + toolkit.get_elapsed_time(time_start, time_end))
    
        except Exception as e: 

            print("\nUncaught error has been raised in Kijiku, error is as follows : " + str(e) + "\nOutputting incomplete results\n")

            self.error_text.append("\nUncaught error has been raised in Kijiku, error is as follows : " + str(e) + "\nOutputting incomplete results\n")

            if(self.from_gui):
                with open(os.path.join(self.config_dir,"guiTempTranslationLog.txt"), "a+", encoding="utf-8") as file: ## Write the text to a temporary file
                    file.write("\nUncaught error has been raised in Kijiku, error is as follows : " + str(e) + "\nOutputting incomplete results\n")

                toolkit.clear_console()

            self.output_results()

##-------------------start-of-build_messages()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def build_messages(self) -> None:

        '''

        builds messages dict for ai\n
        
        Parameters:\n
        self (object - Kijiku) : the Kijiku object.\n

        Returns:\n
        None\n

        '''

        i = 0

        while i < len(self.japanese_text):
            prompt, i = self.generate_prompt(i)

            prompt = ''.join(prompt)

            if(self.message_mode == 1):
                system_msg = {}
                system_msg["role"] = "system"
                system_msg["content"] = self.system_message

            else:
                system_msg = {}
                system_msg["role"] = "user"
                system_msg["content"] = self.system_message

            self.messages.append(system_msg)

            model_msg = {}
            model_msg["role"] = "user"
            model_msg["content"] = prompt

            self.messages.append(model_msg)

        self.debug_text.append("\nMessages\n-------------------------\n\n")

        i = 0

        for message in self.messages:

            i+=1

            if(i % 2 == 0):

                self.debug_text.append(str(message) + "\n\n")
        
            else:

                self.debug_text.append(str(message) + "\n")

##-------------------start-of-generate_prompt()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def generate_prompt(self, index:int) -> tuple[typing.List[str],int]:

        '''

        generates prompts for the messages meant for the ai\n

        Parameters:\n
        self (object - Kijiku) : the Kijiku object.\n
        index (int) an int representing where we currently are in the text file\n

        Returns:\n
        prompt (list - string) a list of japanese lines that will be assembled into messages\n
        index (int) an updated int representing where we currently are in the text file\n

        '''

        prompt = []

        while(index < len(self.japanese_text)):
            sentence = self.japanese_text[index]

            if(len(prompt) < self.prompt_size):

                if(any(char in sentence for char in ["▼", "△", "◇"])):
                    prompt.append(sentence + '\n')
                    self.debug_text.append("\n-----------------------------------------------\nSentence : " + sentence + "\nSentence is a pov change... leaving intact\n-----------------------------------------------\n\n")

                elif("part" in sentence.lower() or all(char in ["１","２","３","４","５","６","７","８","９", " "] for char in sentence) and not all(char in [" "] for char in sentence)):
                    prompt.append(sentence + '\n') 
                    self.debug_text.append("\n-----------------------------------------------\nSentence : " + sentence + "\nSentence is part marker... leaving intact\n-----------------------------------------------\n\n")
            
                elif(bool(re.match(r'^[\W_\s\n-]+$', sentence)) and not any(char in sentence for char in ["」", "「", "«", "»"]) and sentence != '"..."' and sentence != "..."):
                    self.debug_text.append("\n-----------------------------------------------\nSentence : " + sentence + "\nSentence is punctuation... skipping\n-----------------------------------------------\n\n")
            
                elif(bool(re.match(r'^[A-Za-z0-9\s\.,\'\?!]+\n*$', sentence) and "part" not in sentence.lower())):
                    self.debug_text.append("\n-----------------------------------------------\nSentence : " + sentence + "\nSentence is english... skipping\n-----------------------------------------------\n\n")

                else:
                    prompt.append(sentence + "\n")
    
            else:
                return prompt, index
            
            index += 1

        return prompt, index
    
##-------------------start-of-estimated_cost()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def estimate_cost(self) -> None:

        '''

        attempts to estimate cost.\n
    
        Parameters:\n
        self (object - Kijiku) : the Kijiku object.\n
        model (string) t represents which model we will be using\n

        Returns:\n
        None\n

        '''
        
        try:
            encoding = tiktoken.encoding_for_model(self.MODEL)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")

        if(self.MODEL == "gpt-3.5-turbo"):
            print("Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
            time.sleep(1)
            self.MODEL="gpt-3.5-turbo-0613"
            return self.estimate_cost()
        
        if(self.MODEL == "gpt-3.5-turbo-0301"):
            print("Warning: gpt-3.5-turbo-0301 is outdated. gpt-3.5-turbo-0301's support ended September 13, Returning num tokens assuming gpt-3.5-turbo-0613.")
            time.sleep(1)
            self.MODEL="gpt-3.5-turbo-0613"
            return self.estimate_cost()

        if(self.MODEL == "gpt-3.5-turbo-0613"):
            costPer1000Tokens = 0.0015
            tokensPerMessage = 4  ## every message follows <|start|>{role/name}\n{content}<|end|>\n
            tokensPerName = -1  ## if there's a name, the role is omitted

        elif(self.MODEL == "gpt-4"):
            print("Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-0613.")
            return self.estimate_cost(model="gpt-4-0613")
        
        elif(self.MODEL == "gpt-4-0314"):
            print("Warning: gpt-4-0314 is outdated. gpt-4-0314's support ended September 13, Returning num tokens assuming gpt-4-0613.")
            time.sleep(1)
            self.MODEL="gpt-4-0613"

        elif(self.MODEL == "gpt-4-0613"):
            costPer1000Tokens = 0.06
            tokensPerMessage = 3
            tokensPerName = 1

        else:
            raise NotImplementedError(f"""Kudasai does not support : {self.MODEL}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
        
        numTokens = 0

        for message in self.messages:

            numTokens += tokensPerMessage

            for key, value in message.items():

                numTokens += len(encoding.encode(value))

                if(key == "name"):
                    numTokens += tokensPerName

        numTokens += 3  ## every reply is primed with <|start|>assistant<|message|>
        minCost = round((float(numTokens) / 1000.00) * costPer1000Tokens, 5)

        self.debug_text.append("\nEstimated Tokens in Messages : " + str(numTokens))
        self.debug_text.append("\nEstimated Minimum Cost : " + str(minCost) + '\n')

        if(not self.from_gui):
            print("\nEstimated Number of Tokens in Text : " + str(numTokens))
            print("Estimated Minimum Cost of Translation : " + str(minCost) + "\n")
        else:
            with open(os.path.join(self.config_dir,"guiTempTranslationLog.txt"), "a+", encoding="utf-8") as file: ## Write the text to a temporary file
                file.write("\nEstimated Number of Tokens in Text : " + str(numTokens) + "\n")
                file.write("\nEstimated Minimum Cost of Translation : " + str(minCost) + "\n\n")

##-------------------start-of-translate_message()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    ## backoff wrapper for retrying on errors
    @backoff.on_exception(backoff.expo, (ServiceUnavailableError, RateLimitError, Timeout, APIError, APIConnectionError))
    def translate_message(self, system_message:dict, user_message:dict) -> str:

        '''

        translates system and user message\n

        Parameters:\n
        self (object - Kijiku) : the Kijiku object.\n
        system_message (dict) : the system message also known as the instructions\n
        user_message (dict) : the user message also known as the prompt\n

        Returns:\n
        output (string) a string that gpt gives to us also known as the translation\n

        '''

        ## max_tokens and logit bias are currently excluded due to a lack of need, and the fact that i am lazy

        response = openai.ChatCompletion.create(
            model=self.MODEL,
            messages=[
                system_message,
                user_message,
            ],

            temperature = float(self.kijiku_rules["open ai settings"]["temp"]),
            top_p = float(self.kijiku_rules["open ai settings"]["top_p"]),
            n = int(self.kijiku_rules["open ai settings"]["top_p"]),
            stream = self.kijiku_rules["open ai settings"]["stream"],
            stop = self.kijiku_rules["open ai settings"]["stop"],
            presence_penalty = float(self.kijiku_rules["open ai settings"]["presence_penalty"]),
            frequency_penalty = float(self.kijiku_rules["open ai settings"]["frequency_penalty"]),

        )

        ## note, pylance flags this as a 'GeneralTypeIssue', however i see nothing wrong with it, and it works fine
        output = response['choices'][0]['message']['content'] ## type: ignore

        self.debug_text.append("\nPrompt was : \n" + user_message["content"] + "\n")

        self.debug_text.append("-------------------------\nResponse from GPT was : \n\n" + output + "\n")

        if(self.je_check_mode == 1):
            self.je_check_text.append("\n-------------------------\n"+ str(user_message["content"]) + "\n\n")
        elif(self.je_check_mode == 2):
            self.je_check_text.append(str(user_message["content"]))
        
        return output

##-------------------start-of-redistribute()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def redistribute(self, translated_message:str) -> None:

        '''

        puts translated text back into text file

        Parameters:
        self (object - Kijiku) : the Kijiku object.
        translated_message (string) : the translated message

        Returns:
        None

        '''

        if(self.sentence_fragmenter_mode == 1): ## mode 1 is the default mode, uses regex and other nonsense to split sentences

            sentences = re.findall(r"(.*?(?:(?:\"|\'|-|~|!|\?|%|\(|\)|\.\.\.|\.|---|\[|\])))(?:\s|$)", translated_message)

            patched_sentences = []
            buildString = None

            self.debug_text.append("\n-------------------------\nDistributed result was : \n\n")

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

                self.translated_text.append(sentence + '\n')
                self.debug_text.append(sentence + '\n')

                if(self.je_check_mode == 1):
                    self.je_check_text.append(sentence+ '\n')
                elif(self.je_check_mode == 2):
                    self.je_check_text.append(sentence)

            for i in range(len(self.translated_text)):
                if self.translated_text[i] in patched_sentences:
                    index = patched_sentences.index(self.translated_text[i])
                    self.translated_text[i] = patched_sentences[index]

        elif(self.sentence_fragmenter_mode == 2): ## mode 2 uses spacy to split sentences

            nlp = spacy.load("en_core_web_lg")

            doc = nlp(translated_message)
            sentences = [sent.text for sent in doc.sents]
            
            self.debug_text.append("\n-------------------------\nDistributed result was : \n\n")

            for sentence in sentences:
                self.translated_text.append(sentence + '\n')
                self.debug_text.append(sentence + '\n')

                if(self.je_check_mode == 1):
                    self.je_check_text.append(sentence + '\n')
                elif(self.je_check_mode == 2):
                    self.je_check_text.append(sentence)

        elif(self.sentence_fragmenter_mode == 3): ## mode 3 just assumes gpt formatted it properly
            
            self.translated_text.append(translated_message + '\n\n')
            
            if(self.je_check_mode == 1):
                self.je_check_text.append(translated_message + '\n')
            elif(self.je_check_mode == 2):
                self.je_check_text.append(translated_message)

##-------------------start-of-output_results()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    def output_results(self) -> None:

        '''

        Outputs results to several txt files\n

        Parameters:\n
        self (object - Kijiku) : the Kijiku object.\n

        Returns:\n
        None\n

        '''

        self.output_dir = os.path.join(self.script_dir, "KudasaiOutput")
        
        if(not os.path.exists(self.output_dir)):
            os.mkdir(self.output_dir)

        debug_path = os.path.join(self.output_dir, "tlDebug.txt")
        je_path = os.path.join(self.output_dir, "jeCheck.txt")
        translated_path = os.path.join(self.output_dir, "translatedText.txt")
        error_path = os.path.join(self.output_dir, "errors.txt")

        if(self.je_check_mode == 2):
            self.je_check_text = self.fix_je()

        with open(debug_path, 'w+', encoding='utf-8') as file:
                file.writelines(self.debug_text)

        with open(je_path, 'w+', encoding='utf-8') as file: 
                file.writelines(self.je_check_text)

        with open(translated_path, 'w+', encoding='utf-8') as file:
                file.writelines(self.translated_text)

        with open(error_path, 'w+', encoding='utf-8') as file:
                file.writelines(self.error_text)


        if(self.from_gui):
            with open(os.path.join(self.config_dir,"guiTempTranslationLog.txt"), "a+", encoding="utf-8") as file: ## Write the text to a temporary file
                file.write("Debug text have been written to : " + debug_path + "\n\n")
                file.write("J->E text have been written to : " + je_path + "\n\n")
                file.write("Translated text has been written to : " + translated_path + "\n\n")
                file.write("Errors have been written to : " + error_path + "\n\n")

            return
        
        print("\n\nDebug text have been written to : " + debug_path)
        print("\nJ->E text have been written to : " + je_path)
        print("\nTranslated text has been written to : " + translated_path)
        print("\nErrors have been written to : " + error_path + "\n")

##-------------------start-of-fix_je()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def fix_je(self) -> typing.List[str]:

        '''

        Fixes the J->E text to be more j-e check friendly\n

        Note that fix_je() is not always accurate, and may use standard j-e formatting instead of the corrected formatting.\n

        Parameters:\n
        self (object - Kijiku) : the Kijiku object.\n

        Returns:\n
        final_list (list - str) : the fixed J->E text.\n

        '''
        
        i = 1
        final_list = []

        while i < len(self.je_check_text):
            jap = self.je_check_text[i-1].split('\n')
            eng = self.je_check_text[i].split('\n')

            jap = [line for line in jap if line.strip()]  ## Remove blank lines
            eng = [line for line in eng if line.strip()]  ## Remove blank lines    

            final_list.append("\n-------------------------\n")

            if(len(jap) == len(eng)):

                for jap_line,eng_line in zip(jap,eng):
                    if(jap_line and eng_line): ## check if jap_line and eng_line aren't blank
                        final_list.append(jap_line + '\n\n')
                        final_list.append(eng_line + '\n\n')

            else:

                final_list.append(self.je_check_text[i-1] + '\n\n')
                final_list.append(self.je_check_text[i] + '\n\n')

            i+=2

        return final_list