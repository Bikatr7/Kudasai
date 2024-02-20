## built-in libraries
import json
import typing

## custom modules
from modules.common.file_ensurer import FileEnsurer
from modules.common.logger import Logger
from modules.common.toolkit import Toolkit

##-------------------start-of-JsonHandler---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class JsonHandler:

    """
    
    Handles the Kijiku Rules.json file and interactions with it.

    """

    current_kijiku_rules = dict()

    kijiku_settings_message = """
    See https://platform.openai.com/docs/api-reference/chat/create for further details
    ----------------------------------------------------------------------------------
    model : ID of the model to use. As of right now, Kijiku only works with 'chat' models.

    system_message : Instructions to the model. Basically tells the model what to do.

    temp : What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. Lower values are typically better for translation.

    top_p : An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. I generally recommend altering this or temperature but not both.

    n : How many chat completion choices to generate for each input message. Do not change this.

    stream : If set, partial message deltas will be sent, like in ChatGPT. Tokens will be sent as data-only server-sent events as they become available, with the stream terminated by a data: [DONE] message. See the OpenAI python library on GitHub for example code. Do not change this.

    stop : Up to 4 sequences where the API will stop generating further tokens. Do not change this.

    logit_bias : Modifies the likelihood of specified tokens appearing in the completion. Do not change this.

    max_tokens :  The maximum number of tokens to generate in the chat completion. The total length of input tokens and generated tokens is limited by the model's context length. I wouldn't recommend changing this.

    presence_penalty : Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics. While negative values encourage repetition. Should leave this at 0.0.

    frequency_penalty : Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim. Negative values encourage repetition. Should leave this at 0.0.

    message_mode : 1 or 2. 1 means the system message will actually be treated as a system message. 2 means it'll be treated as a user message. 1 is recommend for gpt-4 otherwise either works.

    num_lines : The number of lines to be built into a prompt at once. Theoretically, more lines would be more cost effective, but other complications may occur with higher lines. So far been tested up to 48.

    sentence_fragmenter_mode : 1 or 2 or 3 (1 - via regex and other nonsense, 2 - NLP via spacy (depreciated, will default to 3 if you select 2), 3 - None (Takes formatting and text directly from API return)) the API can sometimes return a result on a single line, so this determines the way Kijiku fragments the sentences if at all. Use 3 for gpt-4.

    je_check_mode : 1 or 2, 1 will print out the jap then the english below separated by ---, 2 will attempt to pair the english and jap sentences, placing the jap above the eng. If it cannot, it will default to 1. Use 2 for gpt-4.

    num_malformed_batch_retries : How many times Kijiku will attempt to mend a malformed batch, only for gpt4. Be careful with increasing as cost increases at (cost * length * n) at worst case.

    batch_retry_timeout : How long Kijiku will try to translate a batch in seconds, if a requests exceeds this duration, Kijiku will leave it untranslated.

    num_concurrent_batches : How many translations batches Kijiku will send to OpenAI at a time.
    ----------------------------------------------------------------------------------
    Please note that while logit_bias and max_tokens can be changed, Kijiku does not currently do anything with them.
    """

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

        validation_rules = {
            "model": lambda x: x in FileEnsurer.allowed_models,
            "system_message": lambda x: x not in ["", "None", None],
            "temp": lambda x: 0 <= x <= 2,
            "top_p": lambda x: 0 <= x <= 2,
            "n": lambda x: x == 1,
            "stream": lambda x: x is False,
            "max_tokens": lambda x: 0 <= x <= 9223372036854775807,
            "presence_penalty": lambda x: -2 <= x <= 2,
            "message_mode": lambda x: 1 <= x <= 2,
            "sentence_fragmenter_mode": lambda x: 1 <= x <= 3,
            "je_check_mode": lambda x: 1 <= x <= 2,
        }

        try:

            ## ensure category is present
            assert "open ai settings" in JsonHandler.current_kijiku_rules

            ## assign to a variable to reduce repetitive access
            settings = JsonHandler.current_kijiku_rules["open ai settings"]

            ## ensure all keys are present
            assert all(key in settings for key in keys_list)

            ## validate each key using the validation rules
            for key, validate in validation_rules.items():
                if(not validate(settings[key])):
                    raise ValueError(f"Invalid value for {key}")

            ## force stop/logit_bias into None
            settings["stop"] = None
            settings["logit_bias"] = None

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

            settings_print_message = JsonHandler.kijiku_settings_message + SettingsChanger.generate_settings_change_menu()

            action = input(settings_print_message).lower()

            if(action == 'q'):
                break

            ## loads a custom json directly
            if(action == "c"):
                SettingsChanger.load_custom_json()

            elif(action == "d"):
                print("Resetting to default settings.")
                JsonHandler.reset_kijiku_rules_to_default()

            elif(action in JsonHandler.current_kijiku_rules["open ai settings"]):
                SettingsChanger.change_setting(action)

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
            "model": {"type": str, "constraints": lambda x: x.lower() in FileEnsurer.allowed_models},
            "system_message": {"type": str},
            "temp": {"type": float, "constraints": lambda x: 0 <= x <= 2},
            "top_p": {"type": float, "constraints": lambda x: 0 <= x <= 2},
            "n": {"type": int, "constraints": lambda x: x == 1},
            "stream": {"type": bool, "constraints": lambda x: x is False},
            "stop": {"type": None},
            "logit_bias": {"type": None},
            "max_tokens": {"type": int, "constraints": lambda x: 0 <= x <= 9223372036854775807},
            "presence_penalty": {"type": float, "constraints": lambda x: -2 <= x <= 2},
            "frequency_penalty": {"type": float, "constraints": lambda x: -2 <= x <= 2},
            "message_mode": {"type": int, "constraints": lambda x: 1 <= x <= 2},
            "num_lines": {"type": int},
            "sentence_fragmenter_mode": {"type": int, "constraints": lambda x: 1 <= x <= 3},
            "je_check_mode": {"type": int, "constraints": lambda x: 1 <= x <= 2},
            "num_malformed_batch_retries": {"type": int},
            "batch_retry_timeout": {"type": int},
            "num_concurrent_batches": {"type": int}
        }

        if(setting_name not in type_expectations):
            raise ValueError("Invalid setting name")

        setting_info = type_expectations[setting_name]
        converted_value = setting_info["type"](value)

        if("constraints" in setting_info and not setting_info["constraints"](converted_value)):
            raise ValueError(f"{setting_name} out of range")

        return converted_value
    
##-------------------start-of-SettingsChanger---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
class SettingsChanger:

    """
    
    Handles changing the settings of the Kijiku Rules.json file.

    """

##-------------------start-of-generate_settings_change_menu()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def generate_settings_change_menu() -> str:

        """

        Generates the settings change menu.

        Returns:
        menu (str) : The settings change menu.

        """

        menu = """
        
        
        Current settings:
        ----------------------------------------------------------------

        """

        for key, value in JsonHandler.current_kijiku_rules["open ai settings"].items():
            menu += f"{key} : {json.dumps(value)}\n"

        menu += """
        It is recommended that you maximize the console window for this. You will have to to see the settings above.

        Enter the name of the setting you want to change, type d to reset to default, type c to load an external/custom json directly, or type 'q' to quit settings change : 
        """

        return menu
    
##-------------------start-of-load_custom_json()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def load_custom_json() -> None:

        """

        Loads a custom json into the Kijiku Rules.json file.

        """

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

##-------------------start-of-change_setting()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
    @staticmethod
    def change_setting(setting_name:str) -> None:

        """

        Changes the setting of the Kijiku Rules.json file.

        Parameters:
        setting_name (str) : The name of the setting to change.

        """

        new_value = input(f"\nEnter a new value for {setting_name}: ")

        try:
            converted_value = JsonHandler.convert_to_correct_type(setting_name, new_value)

            JsonHandler.current_kijiku_rules["open ai settings"][setting_name] = converted_value
            print(f"Updated {setting_name} to {converted_value}.")
        
        except:
            print("Invalid input. No changes made.")