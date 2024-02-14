## built-in libraries
import json
import typing

## custom modules
from modules.common.file_ensurer import FileEnsurer
from modules.common.logger import Logger
from modules.common.toolkit import Toolkit

class JsonHandler:

    """
    
    Handles the Kijiku Rules.json file and interactions with it.

    """

    current_kijiku_rules = dict()

##-------------------start-of-validate_json()--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def validate_json() -> None:

        """

        Validates the Kijiku Rules.json file.

        """

        keys_list = [
        "model",
        "system_message",
        "temp",
        "top_p",
        "n",
        "stream",
        "stop",
        "logit_bias",
        "max_tokens",
        "presence_penalty",
        "frequency_penalty",
        "message_mode",
        "num_lines",
        "sentence_fragmenter_mode",
        "je_check_mode",
        "num_malformed_batch_retries",
        "batch_retry_timeout",
        "num_concurrent_batches"
         ]
        

        try:

            ## ensure category is present
            assert "open ai settings" in JsonHandler.current_kijiku_rules

            ## ensure all keys are present
            assert all(key in JsonHandler.current_kijiku_rules["open ai settings"] for key in keys_list)

            if(JsonHandler.current_kijiku_rules["open ai settings"]["model"] not in FileEnsurer.allowed_models):
                raise ValueError("Invalid model")
            
            ## Doesn't happen often, but just in case
            assert JsonHandler.current_kijiku_rules["open ai settings"]["system_message"] not in ["", "None", None]

            if(JsonHandler.current_kijiku_rules["open ai settings"]["temp"] < 0 or JsonHandler.current_kijiku_rules["open ai settings"]["top_p"] > 2):
                raise ValueError("temp or top_p out of range, must be between 0 and 2")
            
            if(JsonHandler.current_kijiku_rules["open ai settings"]["n"] != 1):
                raise ValueError("n must be 1")
            
            if(JsonHandler.current_kijiku_rules["open ai settings"]["stream"] != False):
                raise ValueError("stream must be false")

            ## force stop/logit_bias into None
            JsonHandler.current_kijiku_rules["open ai settings"]["stop"] = None
            JsonHandler.current_kijiku_rules["open ai settings"]["logit_bias"] = None

            if(JsonHandler.current_kijiku_rules["open ai settings"]["max_tokens"] < 0 or JsonHandler.current_kijiku_rules["open ai settings"]["max_tokens"] > 9223372036854775807):
                raise ValueError("max_tokens out of range, must be between 0 and 9223372036854775807")
            
            if(JsonHandler.current_kijiku_rules["open ai settings"]["presence_penalty"] < -2 or JsonHandler.current_kijiku_rules["open ai settings"]["presence_penalty"] > 2):
                raise ValueError("presence_penalty out of range, must be between -2 and 2")
            
            if(JsonHandler.current_kijiku_rules["open ai settings"]["message_mode"] < 1 or JsonHandler.current_kijiku_rules["open ai settings"]["message_mode"] > 2):
                raise ValueError("message_mode out of range, must be 1 or 2")
            
            if(JsonHandler.current_kijiku_rules["open ai settings"]["sentence_fragmenter_mode"] < 1 or JsonHandler.current_kijiku_rules["open ai settings"]["sentence_fragmenter_mode"] > 3):
                raise ValueError("sentence_fragmenter_mode out of range, must be 1, 2, or 3")
            
            if(JsonHandler.current_kijiku_rules["open ai settings"]["je_check_mode"] < 1 or JsonHandler.current_kijiku_rules["open ai settings"]["je_check_mode"] > 2):
                raise ValueError("je_check_mode out of range, must be 1 or 2")
            
        except Exception:

            Logger.log_action("Kijiku Rules.json is not valid, setting to invalid_placeholder, current:")
            Logger.log_action(str(JsonHandler.current_kijiku_rules))
            
            JsonHandler.current_kijiku_rules = FileEnsurer.invalid_kijiku_rules_placeholder

        Logger.log_action("Kijiku Rules.json is valid, current:")
        Logger.log_action(str(JsonHandler.current_kijiku_rules))

##-------------------start-of-reset_kijiku_rules_to_default()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def reset_kijiku_rules_to_default() -> None:

        """

        Resets the kijiku_rules json to default.

        """

        JsonHandler.current_kijiku_rules = FileEnsurer.default_kijiku_rules
        
        JsonHandler.dump_kijiku_rules()

        JsonHandler.load_kijiku_rules()

##-------------------start-of-dump_kijiku_rules()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def dump_kijiku_rules() -> None:

        """

        Dumps the Kijiku Rules.json file to disk.

        """

        with open(FileEnsurer.config_kijiku_rules_path, 'w+', encoding='utf-8') as file:
            json.dump(JsonHandler.current_kijiku_rules, file)

##-------------------start-of-load_kijiku_rules()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def load_kijiku_rules() -> None:

        """

        Loads the Kijiku Rules.json file into memory.

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
            settings_print_message += "\n\nsystem_message : Instructions to the model. Basically tells the model what to do."
            settings_print_message += "\n\ntemp : What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. Lower values are typically better for translation."
            settings_print_message += "\n\ntop_p : An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. I generally recommend altering this or temperature but not both."
            settings_print_message += "\n\nn : How many chat completion choices to generate for each input message. Do not change this."
            settings_print_message += "\n\nstream : If set, partial message deltas will be sent, like in ChatGPT. Tokens will be sent as data-only server-sent events as they become available, with the stream terminated by a data: [DONE] message. See the OpenAI python library on GitHub for example code. Do not change this."
            settings_print_message += "\n\nstop : Up to 4 sequences where the API will stop generating further tokens. Do not change this."
            settings_print_message += "\n\nlogit_bias : Modifies the likelihood of specified tokens appearing in the completion. Do not change this."
            settings_print_message += "\n\nmax_tokens :  The maximum number of tokens to generate in the chat completion. The total length of input tokens and generated tokens is limited by the model's context length. I wouldn't recommend changing this."
            settings_print_message += "\n\npresence_penalty : Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics. While negative values encourage repetition. Should leave this at 0.0."
            settings_print_message += "\n\nfrequency_penalty : Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim. Negative values encourage repetition. Should leave this at 0.0."
            settings_print_message += "\n\nmessage_mode : 1 or 2. 1 means the system message will actually be treated as a system message. 2 means it'll be treated as a user message. 1 is recommend for gpt-4 otherwise either works."
            settings_print_message += "\n\nnum_lines : The number of lines to be built into a prompt at once. Theoretically, more lines would be more cost effective, but other complications may occur with higher lines. So far been tested up to 36."
            settings_print_message += "\n\nsentence_fragmenter_mode : 1 or 2 or 3 (1 - via regex and other nonsense, 2 - NLP via spacy (depreciated, will default to None if you select 2), 3 - None (Takes formatting and text directly from API return)) the API can sometimes return a result on a single line, so this determines the way Kijiku fragments the sentences if at all. Use 3 for gpt-4."
            settings_print_message += "\n\nje_check_mode : 1 or 2, 1 will print out the jap then the english below separated by ---, 2 will attempt to pair the english and jap sentences, placing the jap above the eng. If it cannot, it will default to 1. Use 2 for gpt-4."
            settings_print_message += "\n\nnum_malformed_batch_retries : How many times Kijiku will attempt to mend a malformed batch, only for gpt4. Be careful with increasing as cost increases at (cost * length * n) at worst case."
            settings_print_message += "\n\nbatch_retry_timeout : How long Kijiku will try to translate a batch in seconds, if a requests exceeds this duration, Kijiku will leave it untranslated."
            settings_print_message += "\n\nnum_concurrent_batches : How many translations batches Kijiku will send to OpenAI at a time."

            settings_print_message += "\n\nPlease note that while logit_bias can be changed, Kijiku does not currently do anything with them."

            settings_print_message += "\n\nCurrent settings:\n\n----------------------------------------------------------------\n\n"

            for key, value in JsonHandler.current_kijiku_rules["open ai settings"].items():
                settings_print_message += f"{key} : {json.dumps(value)}\n"

            settings_print_message += "\nIt is recommended that you maximize the console window for this. You will have to to see the settings above.\n"

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

                    ## validate_json() sets a dict to the invalid placeholder if it's invalid, so if it's that, it's invalid
                    assert JsonHandler.current_kijiku_rules != FileEnsurer.invalid_kijiku_rules_placeholder
                    
                    JsonHandler.dump_kijiku_rules()

                    print("Settings loaded successfully.")
                
                except AssertionError:
                    print("Invalid JSON file. Please try again.")
                    JsonHandler.current_kijiku_rules = old_kijiku_rules

                except FileNotFoundError:
                    print("Missing JSON file. Make sure you have a json in the same directory as kudasai.py and that the json is named \"kijiku_rules.json\". Please try again.")
                    JsonHandler.current_kijiku_rules = old_kijiku_rules

            elif(action == "d"):
                print("Resetting to default settings.")
                JsonHandler.reset_kijiku_rules_to_default()

            elif(action in JsonHandler.current_kijiku_rules["open ai settings"]):

                new_value = input(f"\nEnter a new value for {action}: ")

                try:
                    converted_value = JsonHandler.convert_to_correct_type(action, new_value)

                    JsonHandler.current_kijiku_rules["open ai settings"][action] = converted_value
                    print(f"Updated {action} to {converted_value}.")
                
                except:
                    print("Invalid input. No changes made.")
            else:
                print("Invalid setting name. Please try again.")


            Toolkit.pause_console("\nPress enter to continue.")

        JsonHandler.dump_kijiku_rules()
        
##-------------------start-of-convert_to_correct_type()-------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def convert_to_correct_type(setting_name:str, value:str) -> typing.Any:

        """

        Converts the input string to the correct type based on the setting name.

        Parameters:
        setting_name (str) : The name of the setting to convert.
        value (str) : The value to convert.

        Returns:
        (typing.Any) : The converted value.

        """
        
        type_expectations = {
            "model": str,
            "system_message": str,
            "temp": float,
            "top_p": float,
            "n": int,
            "stream": bool,
            "stop": None,
            "logit_bias": None,
            "max_tokens": int,
            "presence_penalty": float,
            "frequency_penalty": float,
            "message_mode": int,
            "num_lines": int,
            "sentence_fragmenter_mode": int,
            "je_check_mode": int,
            "num_malformed_batch_retries": int,
            "batch_retry_timeout": int,
            "num_concurrent_batches": int
        }

        if(setting_name == "model"):
            if(value.lower() in FileEnsurer.allowed_models):
                return value.lower()
            else:
                raise ValueError("Invalid model")
            
        ## just return the value for system_message since it can be whatever.
        if(setting_name == "system_message"):
            return str(value)

        ## Coerce stop and logit_bias into None
        if(setting_name in ["stop", "logit_bias"]):
            return None

        ## do type checks for everything else
        if(setting_name in type_expectations):

            if(setting_name in ["temp", "top_p"]):
                float_value = float(value)

                if(float_value < 0 or float_value > 2):
                    raise ValueError(f"{setting_name} out of range")

                return float_value
            
            ## coerce n into 1
            if(setting_name == "n"):
                return 1
            
            ## coerce stream into False
            if(setting_name == "stream"):
                return False
            
            if(setting_name == "max_tokens"):
                int_value = int(value)

                if(int_value < 0 or int_value > 9223372036854775807):
                    raise ValueError("max_tokens out of range")
                
                return int_value
            
            if(setting_name in ["presence_penalty", "frequency_penalty"]):
                float_value = float(value)

                if(float_value < -2 or float_value > 2):
                    raise ValueError(f"{setting_name} out of range")

                return float_value
            
            if(setting_name == "message_mode"):
                int_value = int(value)

                if(int_value < 1 or int_value > 2):
                    raise ValueError("message_mode out of range")

                return int_value
            
            if(setting_name == "num_lines"):
                int_value = int(value)

                return int_value
            
            if(setting_name == "sentence_fragmenter_mode"):
                int_value = int(value)

                if(int_value < 1 or int_value > 3):
                    raise ValueError("sentence_fragmenter_mode out of range")

                return int_value
            
            if(setting_name == "je_check_mode"):
                int_value = int(value)

                if(int_value < 1 or int_value > 2):
                    raise ValueError("je_check_mode out of range")

                return int_value
            
            if(setting_name == "num_malformed_batch_retries"):
                int_value = int(value)

                return int_value
            
            if(setting_name == "batch_retry_timeout"):
                int_value = int(value)

                return int_value

            if(setting_name == "num_concurrent_batches"):
                int_value = int(value)

                return int_value
        
        else:
            raise ValueError("Invalid setting name")