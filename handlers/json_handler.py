## built-in libraries
import json
import typing

## custom modules
from modules.file_ensurer import FileEnsurer
from modules.logger import Logger
from modules.toolkit import Toolkit

class JsonHandler:

    """
    
    This class is used to handle the Kijiku Rules json file.

    """

    current_kijiku_rules = dict()

    default_kijiku_rules = {
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
        "sentence_fragmenter_mode":3,
        "je_check_mode":2,
        "num_malformed_batch_retries":1,
        "batch_retry_timeout":300
    }
    }

##-------------------start-of-validate_json()--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def validate_json():

        """

        Validates the Kijiku Rules.json file.

        """

        keys_list = [
        "model",
        "temp",
        "top_p",
        "n",
        "stream",
        "stop",
        "max_tokens",
        "presence_penalty",
        "frequency_penalty",
        "logit_bias",
        "system_message",
        "message_mode",
        "num_lines",
        "sentence_fragmenter_mode",
        "je_check_mode",
        "num_malformed_batch_retries",
        "batch_retry_timeout"
         ]
        

        ## json is fucked, reset it
        if("open ai settings" not in JsonHandler.current_kijiku_rules):
            JsonHandler.reset_kijiku_rules_to_default()

        if(all(key in JsonHandler.current_kijiku_rules["open ai settings"] for key in keys_list)):
            Logger.log_action("Kijiku Rules.json is valid")
        
        ## if not valid, reset it
        else:
            Logger.log_action("Kijiku Rules.json is not valid, resetting...")
            Logger.log_action(str(JsonHandler.current_kijiku_rules))
            JsonHandler.reset_kijiku_rules_to_default()

##-------------------start-of-reset_kijiku_rules_to_default()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def reset_kijiku_rules_to_default() -> None:

        """

        Resets the kijiku_rules json to default.

        """

        JsonHandler.current_kijiku_rules = JsonHandler.default_kijiku_rules
        

        JsonHandler.dump_kijiku_rules()

        JsonHandler.load_kijiku_rules()

##-------------------start-of-dump_kijiku_rules()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def dump_kijiku_rules() -> None:

        """

        Dumps the Kijiku Rules.json file.

        """

        with open(FileEnsurer.config_kijiku_rules_path, 'w+', encoding='utf-8') as file:
            json.dump(JsonHandler.current_kijiku_rules, file)

##-------------------start-of-load_kijiku_rules()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def load_kijiku_rules() -> None:

        """

        Loads the Kijiku Rules.json file.

        """

        with open(FileEnsurer.config_kijiku_rules_path, 'r', encoding='utf-8') as file:
            JsonHandler.current_kijiku_rules = json.load(file)


##-------------------start-of-change_kijiku_settings()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def change_kijiku_settings() -> None:

        """

        Allows the user to change the settings of the Kijiku Rules.json file

        """
        

        while(True):

            Toolkit.clear_console()

            settings_print_message = "See https://platform.openai.com/docs/api-reference/chat/create for further details"
            settings_print_message = "----------------------------------------------------------------------------------"

            settings_print_message += "\n\nmodel : ID of the model to use. As of right now, Kijiku only works with 'chat' models."
            settings_print_message += "\n\ntemperature : What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. Lower Values are typically better for translation"
            settings_print_message += "\n\ntop_p : An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. I generally recommend altering this or temperature but not both."
            settings_print_message += "\n\nn : How many chat completion choices to generate for each input message. Do not change this."
            settings_print_message += "\n\nstream : If set, partial message deltas will be sent, like in ChatGPT. Tokens will be sent as data-only server-sent events as they become available, with the stream terminated by a data: [DONE] message. See the OpenAI Cookbook for example code. Do not change this."
            settings_print_message += "\n\nstop : Up to 4 sequences where the API will stop generating further tokens. Do not change this."
            settings_print_message += "\n\nmax_tokens :  The maximum number of tokens to generate in the chat completion. The total length of input tokens and generated tokens is limited by the model's context length. I wouldn't recommend changing this"
            settings_print_message += "\n\npresence_penalty : Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics."
            settings_print_message += "\n\nfrequency_penalty : Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim."
            settings_print_message += "\n\nlogit_bias : Modify the likelihood of specified tokens appearing in the completion. Do not change this."
            settings_print_message += "\n\nsystem_message : Instructions to the model. Do not change this unless you know what you're doing."
            settings_print_message += "\n\nmessage_mode : 1 or 2. 1 means the system message will actually be treated as a system message. 2 means it'll be treating as a user message. 1 is recommend for gpt-4 otherwise either works."
            settings_print_message += "\n\nnum_lines : the number of lines to be built into a prompt at once. Theoretically, more lines would be more cost effective, but other complications may occur with higher lines."
            settings_print_message += "\n\nsentence_fragmenter_mode : 1 or 2 or 3 (1 - via regex and other nonsense, 2 - NLP via spacy, 3 - None (Takes formatting and text directly from ai return)) the api can sometimes return a result on a single line, so this determines the way Kijiku fragments the sentences if at all."
            settings_print_message += "\n\nje_check_mode : 1 or 2, 1 will print out the 'num_lines' amount of jap then the english below separated by ---, 2 will attempt to pair the english and jap sentences, placing the jap above the eng. If it cannot, it will do 1."
            settings_print_message += "\n\nnum_malformed_batch_retries : How many times Kudasai will attempt to mend a malformed batch, only for gpt4. Defaults to 1, careful with increasing as cost increases at (cost * length * n) at worst case."
            settings_print_message += "\n\nbatch_retry_timeout : How long Kudasai will try to attempt to requery a translation batch in seconds, if a requests exceeds this duration, Kudasai will leave it untranslated."

            settings_print_message += "\n\nPlease note that while logit_bias and max_tokens can be changed, Kijiku does not currently do anything with them."

            settings_print_message += "\n\nCurrent settings:\n\n----------------------------------------------------------------\n\n"

            for key, value in JsonHandler.current_kijiku_rules["open ai settings"].items():
                settings_print_message += f"{key} : {json.dumps(value)}\n"

            settings_print_message += "\nIt is recommended that you maximize the console window for this.\n"

            settings_print_message += "\n\nEnter the name of the setting you want to change, type d to reset to default, type c to load an external/custom json directly, or type 'q' to quit settings change : "
            action = input(settings_print_message).lower()

            if(action == 'q'):
                break

            ## loads a custom json directly
            if(action == "c"):
                Toolkit.clear_console()

                ## saves old rules in case on invalid json
                old_kijiku_rules = JsonHandler.current_kijiku_rules

                try:

                    ## loads the custom json file
                    with open(FileEnsurer.external_kijiku_rules_path, 'r', encoding='utf-8') as file:
                        JsonHandler.current_kijiku_rules = json.load(file) 

                    JsonHandler.validate_json()

                    ## validate_json() sets a dict to default if it's invalid, so if it's still default, it's invalid
                    assert JsonHandler.current_kijiku_rules != JsonHandler.default_kijiku_rules 
                    
                    JsonHandler.dump_kijiku_rules()

                    print("Settings loaded successfully.")
                
                except AssertionError:
                    print("Invalid JSON file. Please try again.")
                    JsonHandler.current_kijiku_rules = old_kijiku_rules


                except FileNotFoundError:
                    print("Missing JSON file. Make sure you have a json in the same directory as kudasai.py and that the json is named \"kijiku_rules.json\". Please try again.")
                    JsonHandler.current_kijiku_rules = old_kijiku_rules

            elif(action == "d"):
                JsonHandler.reset_kijiku_rules_to_default()

            elif(action in JsonHandler.current_kijiku_rules["open ai settings"]):

                new_value = input(f"\nEnter a new value for {action}: ")

                converted_value = JsonHandler.convert_to_correct_type(action, new_value)

                if(converted_value is not None):
                    JsonHandler.current_kijiku_rules["open ai settings"][action] = converted_value
                    print(f"Updated {action} to {converted_value}.")

                else:
                    print("Invalid input. No changes made.")
            else:
                print("Invalid setting name. Please try again.")


            Toolkit.pause_console()

        ## Attempt to save the changes.
        try:
            JsonHandler.dump_kijiku_rules()
            print("Settings saved successfully.")

        except Exception as e:
            print(f"Failed to save settings: {e}")

##-------------------start-of-convert_to_correct_type()-------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def convert_to_correct_type(setting_name:str, value:str) -> typing.Any:

        """

        Converts the input string to the correct type based on the setting name.

        Parameters:
        setting_name (str): The name of the setting to convert.
        value (str): The value to convert.

        Returns:
        The value converted to the correct type, or None if the input is invalid.

        """
        
        type_expectations = {
            "model": str,
            "temp": float,
            "top_p": float,
            "n": int,
            "stream": bool,
            "stop": list,
            "max_tokens": int,
            "presence_penalty": float,
            "frequency_penalty": float,
            "logit_bias": dict,
            "system_message": str,
            "message_mode": int,
            "num_lines": int,
            "sentence_fragmenter_mode": int,
            "je_check_mode": int,
            "num_malformed_batch_retries": int,
            "batch_retry_timeout": int
        }

        # Special cases for None or complex types
        if(setting_name in ["stop", "logit_bias"] and value.lower() == "none"):
            return None

        ## Check if the setting requires a specific type
        if(setting_name in type_expectations):
            try:

                if(setting_name == "max_tokens"):
                    int_value = int(value)

                    if(int_value < 0 or int_value > 5000):
                        raise ValueError("max_tokens out of range")
                    
                    return int_value

                return type_expectations[setting_name](value)
            
            except ValueError:
                return None
        else:
            return value