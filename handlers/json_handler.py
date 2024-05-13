## built-in libraries
import json
import typing
import logging

## third-party libraries
from easytl import ALLOWED_GEMINI_MODELS, ALLOWED_OPENAI_MODELS

## custom modules
from modules.common.file_ensurer import FileEnsurer
from modules.common.toolkit import Toolkit

##-------------------start-of-JsonHandler---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class JsonHandler:

    """
    
    Handles the translation_settings.json file and interactions with it.

    """

    current_translation_settings = dict()

    translation_settings_message = """
----------------------------------------------------------------------------------
Base Translation Settings:

prompt_assembly_mode : 1 or 2. 1 means the system message will actually be treated as a system message. 2 means it'll be treated as a user message. 1 is recommend for gpt-4 otherwise either works. For Gemini, this setting is ignored.

number_of_lines_per_batch : The number of lines to be built into a prompt at once. Theoretically, more lines would be more cost effective, but other complications may occur with higher lines. So far been tested up to 48.

sentence_fragmenter_mode : 1 or 2  (1 - via regex and other nonsense) 2 - None (Takes formatting and text directly from API return)) the API can sometimes return a result on a single line, so this determines the way Kudasai fragments the sentences if at all. Use 2 for newer models.

je_check_mode : 1 or 2, 1 will print out the jap then the english below separated by ---, 2 will attempt to pair the english and jap sentences, placing the jap above the eng. If it cannot, it will default to 1. Use 2 for newer models.

number_of_malformed_batch_retries : (Malformed batch is when je-fixing fails) How many times Kudasai will attempt to mend a malformed batch (mending is resending the request), only for gpt4. Be careful with increasing as cost increases at (cost * length * n) at worst case. This setting is ignored if je_check_mode is set to 1.

batch_retry_timeout : How long Kudasai will try to translate a batch in seconds, if a requests exceeds this duration, Kudasai will leave it untranslated.

number_of_concurrent_batches : How many translations batches Kudasai will send to the translation API at a time. For OpenAI, be conservative as rate-limiting is aggressive, I'd suggest 3-5. For Gemini, do not exceed 60.
----------------------------------------------------------------------------------
Open AI Settings:
See https://platform.openai.com/docs/api-reference/chat/create for further details
----------------------------------------------------------------------------------
openai_model : ID of the model to use. Kudasai only works with 'chat' models.

openai_system_message : Instructions to the model. Basically tells the model how to translate.

openai_temperature : What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. Lower values are typically better for translation.

openai_top_p : An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. I generally recommend altering this or temperature but not both.

openai_n : How many chat completion choices to generate for each input message. Do not change this.

openai_stream : If set, partial message deltas will be sent, like in ChatGPT. Tokens will be sent as data-only server-sent events as they become available, with the stream terminated by a data: [DONE] message. See the OpenAI python library on GitHub for example code. Do not change this.

openai_stop : Up to 4 sequences where the API will stop generating further tokens. Do not change this.

openai_logit_bias : Modifies the likelihood of specified tokens appearing in the completion. Do not change this.

openai_max_tokens :  The maximum number of tokens to generate in the chat completion. The total length of input tokens and generated tokens is limited by the model's context length. I wouldn't recommend changing this. Is none by default. If you change to an integer, make sure it doesn't exceed that model's context length or your request will fail and repeat till timeout.

openai_presence_penalty : Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics. While negative values encourage repetition. Should leave this at 0.0.

openai_frequency_penalty : Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim. Negative values encourage repetition. Should leave this at 0.0.
----------------------------------------------------------------------------------
openai_stream, openai_logit_bias, openai_stop and openai_n are included for completion's sake, current versions of Kudasai will hardcode their values when validating the Kijiku_rule.json to their default values. As different values for these settings do not have a use case in Kudasai's current implementation.
----------------------------------------------------------------------------------
Gemini Settings:
https://ai.google.dev/docs/concepts#model-parameters for further details
----------------------------------------------------------------------------------
gemini_model : The model to use. Currently only supports gemini-pro and gemini-pro-vision, the 1.0 model and it's aliases.

gemini_prompt : Instructions to the model. Basically tells the model how to translate.

gemini_temperature : What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. Lower values are typically better for translation.

gemini_top_p : An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. I generally recommend altering this or temperature but not both.

gemini_top_k : Determines the number of most probable tokens to consider for each selection step. A higher value increases diversity, a lower value makes the output more deterministic.

gemini_candidate_count : The number of candidates to generate for each input message. Do not change this.

gemini_stream : If set, partial message deltas will be sent, like in Gemini Chat. Tokens will be sent as data-only server-sent events as they become available, with the stream terminated by a data: [DONE] message. Do not change this.

gemini_stop_sequences : Up to 4 sequences where the API will stop generating further tokens. Do not change this.

gemini_max_output_tokens : The maximum number of tokens to generate in the chat completion. The total length of input tokens and generated tokens is limited by the model's context length. I wouldn't recommend changing this. Is none by default. If you change to an integer, make sure it doesn't exceed that model's context length or your request will fail and repeat till timeout.
----------------------------------------------------------------------------------
gemini_stream, gemini_stop_sequences and gemini_candidate_count are included for completion's sake, current versions of Kudasai will hardcode their values when validating the Kijiku_rule.json to their default values. As different values for these settings do not have a use case in Kudasai's current implementation.
----------------------------------------------------------------------------------
Deepl Settings:
https://developers.deepl.com/docs/api-reference/translate for further details
----------------------------------------------------------------------------------
deepl_context : The context in which the text should be translated. This is used to improve the translation. If you don't have any context, you can leave this empty.

deepl_split_sentences : How the text should be split into sentences. Possible values are 'OFF', 'ALL', 'NO_NEWLINES'.

deepl_preserve_formatting : Whether the formatting of the text should be preserved. If you don't want to preserve the formatting, you can set this to False.

deepl_formality : The formality of the text. Possible values are 'default', 'more', 'less', 'prefer_more', 'prefer_less'.

----------------------------------------------------------------------------------
    """

##-------------------start-of-validate_json()--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def validate_json() -> None:

        """

        Validates the translation_settings.json file.

        """

        base_translation_keys = [
            "prompt_assembly_mode",
            "number_of_lines_per_batch",
            "sentence_fragmenter_mode",
            "je_check_mode",
            "number_of_malformed_batch_retries",
            "batch_retry_timeout",
            "number_of_concurrent_batches"
        ]

        openai_keys = [
            "openai_model",
            "openai_system_message",
            "openai_temperature",
            "openai_top_p",
            "openai_n",
            "openai_stream",
            "openai_stop",
            "openai_logit_bias",
            "openai_max_tokens",
            "openai_presence_penalty",
            "openai_frequency_penalty"
        ]

        gemini_keys = [
            "gemini_model",
            "gemini_prompt",
            "gemini_temperature",
            "gemini_top_p",
            "gemini_top_k",
            "gemini_candidate_count",
            "gemini_stream",
            "gemini_stop_sequences",
            "gemini_max_output_tokens"
        ]

        deepl_keys = [
            "deepl_context",
            "deepl_split_sentences",
            "deepl_preserve_formatting",
            "deepl_formality"
        ]

        validation_rules = {
            "prompt_assembly_mode": lambda x: isinstance(x, int) and 1 <= x <= 2,
            "number_of_lines_per_batch": lambda x: isinstance(x, int) and x > 0,
            "sentence_fragmenter_mode": lambda x: isinstance(x, int) and 1 <= x <= 2,
            "je_check_mode": lambda x: isinstance(x, int) and 1 <= x <= 2,
            "number_of_malformed_batch_retries": lambda x: isinstance(x, int) and x >= 0,
            "batch_retry_timeout": lambda x: isinstance(x, int) and x >= 0,
            "number_of_concurrent_batches": lambda x: isinstance(x, int) and x >= 0,
            "openai_model": lambda x: isinstance(x, str) and x in ALLOWED_OPENAI_MODELS,
            "openai_system_message": lambda x: x not in ["", "None", None],
            "openai_temperature": lambda x: isinstance(x, float) and 0 <= x <= 2,
            "openai_top_p": lambda x: isinstance(x, float) and 0 <= x <= 1,
            "openai_max_tokens": lambda x: x is None or isinstance(x, int) and x > 0,
            "openai_presence_penalty": lambda x: isinstance(x, float) and -2 <= x <= 2,
            "gemini_model": lambda x: isinstance(x, str) and x in ALLOWED_GEMINI_MODELS,
            "gemini_prompt": lambda x: x not in ["", "None", None],
            "gemini_temperature": lambda x: isinstance(x, float) and 0 <= x <= 2,
            "gemini_top_p": lambda x: x is None or (isinstance(x, float) and 0 <= x <= 2),
            "gemini_top_k": lambda x: x is None or (isinstance(x, int) and x >= 0),
            "gemini_max_output_tokens": lambda x: x is None or isinstance(x, int),
            "deepl_context": lambda x: isinstance(x, str),
            "deepl_split_sentences": lambda x: isinstance(x, str),
            "deepl_preserve_formatting": lambda x: isinstance(x, bool),
            "deepl_formality": lambda x: isinstance(x, str)
        }
        
        try:
            ## ensure categories are present
            assert "base translation settings" in JsonHandler.current_translation_settings, "base translation settings not found"
            assert "openai settings" in JsonHandler.current_translation_settings, "openai settings not found"
            assert "gemini settings" in JsonHandler.current_translation_settings, "gemini settings not found"
            assert "deepl settings" in JsonHandler.current_translation_settings, "deepl settings not found"

            ## assign to variables to reduce repetitive access
            base_translation_settings = JsonHandler.current_translation_settings["base translation settings"]
            openai_settings = JsonHandler.current_translation_settings["openai settings"]
            gemini_settings = JsonHandler.current_translation_settings["gemini settings"]
            deepl_settings = JsonHandler.current_translation_settings["deepl settings"]

            ## ensure all keys are present
            assert all(key in base_translation_settings for key in base_translation_keys), "base translation settings keys missing"
            assert all(key in openai_settings for key in openai_keys), "openai settings keys missing"
            assert all(key in gemini_settings for key in gemini_keys), "gemini settings keys missing"
            assert all(key in deepl_settings for key in deepl_keys), "deepl settings keys missing"

            ## validate each key using the validation rules
            for key, validate in validation_rules.items():
                if(key in base_translation_settings and not validate(base_translation_settings[key])):
                    raise ValueError(f"Invalid value for {key}")
                elif(key in openai_settings and not validate(openai_settings[key])):
                    raise ValueError(f"Invalid value for {key}")
                elif(key in gemini_settings and not validate(gemini_settings[key])):
                    raise ValueError(f"Invalid value for {key}")
                elif(key in deepl_settings and not validate(deepl_settings[key])):
                    raise ValueError(f"Invalid value for {key}")
                

            ## force stop/logit_bias into None
            openai_settings["openai_stop"] = None
            openai_settings["openai_logit_bias"] = None
            openai_settings["openai_stream"] = False

            gemini_settings["gemini_stop_sequences"] = None
            gemini_settings["gemini_stream"] = False

            ## force n and candidate_count to 1
            openai_settings["openai_n"] = 1
            gemini_settings["gemini_candidate_count"] = 1

            ## ensure deepl_formality and deepl_split_sentences are in allowed values
            if(isinstance(deepl_settings["deepl_formality"], str) and deepl_settings["deepl_formality"] not in ["default", "more", "less", "prefer_more", "prefer_less"]):
                raise ValueError("Invalid value for deepl_formality")
            
            if(isinstance(deepl_settings["deepl_split_sentences"], str) and deepl_settings["deepl_split_sentences"] not in ["OFF", "ALL", "NO_NEWLINES"]):
                raise ValueError("Invalid value for deepl_split_sentences")

        except Exception as e:
            logging.warning(f"translation_settings.json is not valid, setting to invalid_placeholder, current:"
                            f"\n{JsonHandler.current_translation_settings}"
                            f"\nReason: {e}")
            
            JsonHandler.current_translation_settings = FileEnsurer.INVALID_TRANSLATION_SETTINGS_PLACEHOLDER

        logging.info(f"translation_settings.json is valid, current:"
                    f"\n{JsonHandler.current_translation_settings}")    

##-------------------start-of-reset_translation_settings_to_default()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def reset_translation_settings_to_default() -> None:

        """

        Resets the translation_settings.json to default.

        """

        JsonHandler.current_translation_settings = FileEnsurer.DEFAULT_KIJIKU_RULES
        
        JsonHandler.dump_translation_settings()

        JsonHandler.load_translation_settings()

##-------------------start-of-dump_translation_settings()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def dump_translation_settings() -> None:

        """

        Dumps the translation_settings.json file to disk.

        """

        with open(FileEnsurer.config_translation_settings_path, 'w+', encoding='utf-8') as file:
            json.dump(JsonHandler.current_translation_settings, file)

##-------------------start-of-load_translation_settings()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def load_translation_settings() -> None:

        """

        Loads the translation_settings.json file into memory.

        """

        with open(FileEnsurer.config_translation_settings_path, 'r', encoding='utf-8') as file:
            JsonHandler.current_translation_settings = json.load(file)

##-------------------start-of-log_translation_settings()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def log_translation_settings(output_to_console:bool=False) -> None:

        """

        Prints the translation_settings.json file to the log.
        Logs by default, but can be set to print to console as well.

        Parameters:
        output_to_console (bool | optional | default=False) : Whether to print to console as well.

        """
        
        sections = ["base translation settings", "openai settings", "gemini settings", "deepl settings"]

        for section in sections:
            print("-------------------")
            print(f"{section.capitalize()}:")
            print("-------------------")

            for key,value in JsonHandler.current_translation_settings[section].items():
                log_message = key + " : " + str(value)
                logging.info(log_message)
                if(output_to_console):
                    print(log_message)

##-------------------start-of-change_translation_settings()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def change_translation_settings() -> None:

        """

        Allows the user to change the settings of the translation_settings.json file

        """
        
        while(True):

            Toolkit.clear_console()

            settings_print_message = JsonHandler.translation_settings_message + SettingsChanger.generate_settings_change_menu()

            action = input(settings_print_message).lower()

            if(action == 'q'):
                break

            ## loads a custom json directly
            if(action == "c"):
                SettingsChanger.load_custom_json()

            elif(action == "d"):
                print("Resetting to default settings.")
                JsonHandler.reset_translation_settings_to_default()

            elif(action in JsonHandler.current_translation_settings["base translation settings"]):
                SettingsChanger.change_setting("base translation settings", action)

            elif(action in JsonHandler.current_translation_settings["openai settings"]):
                SettingsChanger.change_setting("openai settings", action)

            elif(action in JsonHandler.current_translation_settings["gemini settings"]):
                SettingsChanger.change_setting("gemini settings", action)

            elif(action in JsonHandler.current_translation_settings["deepl settings"]):
                SettingsChanger.change_setting("deepl settings", action)

            else:
                print("Invalid setting name. Please try again.")

            Toolkit.pause_console("\nPress enter to continue.")

        JsonHandler.dump_translation_settings()
        
##-------------------start-of-convert_to_correct_type()-------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def convert_to_correct_type(setting_name:str, initial_value:str) -> typing.Any:

        """

        Converts the input string to the correct type based on the setting name.

        Parameters:
        setting_name (str) : The name of the setting to convert.
        initial_value (str) : The initial value to convert.

        Returns:
        (typing.Any) : The converted value.

        """

        value = initial_value
        
        type_expectations = {
            "prompt_assembly_mode": {"type": int, "constraints": lambda x: 1 <= x <= 2},
            "number_of_lines_per_batch": {"type": int, "constraints": lambda x: x > 0},
            "sentence_fragmenter_mode": {"type": int, "constraints": lambda x: 1 <= x <= 2},
            "je_check_mode": {"type": int, "constraints": lambda x: 1 <= x <= 2},
            "number_of_malformed_batch_retries": {"type": int, "constraints": lambda x: x >= 0},
            "batch_retry_timeout": {"type": int, "constraints": lambda x: x >= 0},
            "number_of_concurrent_batches": {"type": int, "constraints": lambda x: x >= 0},
            "openai_model": {"type": str, "constraints": lambda x: x in ALLOWED_OPENAI_MODELS},
            "openai_system_message": {"type": str, "constraints": lambda x: x not in ["", "None", None]},
            "openai_temperature": {"type": float, "constraints": lambda x: 0 <= x <= 2},
            "openai_top_p": {"type": float, "constraints": lambda x: 0 <= x <= 2},
            "openai_n": {"type": int, "constraints": lambda x: x == 1},
            "openai_stream": {"type": bool, "constraints": lambda x: x is False},
            "openai_stop": {"type": None, "constraints": lambda x: x is None},
            "openai_logit_bias": {"type": None, "constraints": lambda x: x is None},
            "openai_max_tokens": {"type": int, "constraints": lambda x: x is None or isinstance(x, int)},
            "openai_presence_penalty": {"type": float, "constraints": lambda x: -2 <= x <= 2},
            "openai_frequency_penalty": {"type": float, "constraints": lambda x: -2 <= x <= 2},
            "gemini_model": {"type": str, "constraints": lambda x: x in ALLOWED_GEMINI_MODELS},
            "gemini_prompt": {"type": str, "constraints": lambda x: x not in ["", "None", None]},
            "gemini_temperature": {"type": float, "constraints": lambda x: 0 <= x <= 2},
            "gemini_top_p": {"type": float, "constraints": lambda x: x is None or (isinstance(x, float) and 0 <= x <= 2)},
            "gemini_top_k": {"type": int, "constraints": lambda x: x is None or x >= 0},
            "gemini_candidate_count": {"type": int, "constraints": lambda x: x == 1},
            "gemini_stream": {"type": bool, "constraints": lambda x: x is False},
            "gemini_stop_sequences": {"type": None, "constraints": lambda x: x is None},
            "gemini_max_output_tokens": {"type": int, "constraints": lambda x: x is None or isinstance(x, int)},
            "deepl_context": {"type": str, "constraints": lambda x: isinstance(x, str)},
            "deepl_split_sentences": {"type": str, "constraints": lambda x: isinstance(x, str)},
            "deepl_preserve_formatting": {"type": bool, "constraints": lambda x: isinstance(x, bool)},
            "deepl_formality": {"type": str, "constraints": lambda x: isinstance(x, str)}
        }

        if(setting_name not in type_expectations):
            raise ValueError("Invalid setting name")

        setting_info = type_expectations[setting_name]

        if("stream" in setting_name):
            value = Toolkit.string_to_bool(initial_value)

        elif(initial_value.lower() in ["none","null"]):
            value = None

        if(setting_info["type"] is None):
            converted_value = None

        elif(setting_info["type"] == int) or (setting_info["type"] == float):

            if(value is None or value == ''):
                converted_value = None
                
            elif(setting_info["type"] == int):
                converted_value = int(value)

            else:
                converted_value = float(value)

        else:
            converted_value = setting_info["type"](value)

        if("constraints" in setting_info and not setting_info["constraints"](converted_value)):
            raise ValueError(f"{setting_name} out of range")

        return converted_value
    
##-------------------start-of-SettingsChanger---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
class SettingsChanger:

    """
    
    Handles changing the settings of the translation_settings.json file.

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

        for key,value in JsonHandler.current_translation_settings["base translation settings"].items():
            menu += key + " : " + str(value) + "\n"

        print("\n")

        for key,value in JsonHandler.current_translation_settings["openai settings"].items():
            menu += key + " : " + str(value) + "\n"

        print("\n")

        for key,value in JsonHandler.current_translation_settings["gemini settings"].items():
            menu += key + " : " + str(value) + "\n"
            
        print("\n")

        for key,value in JsonHandler.current_translation_settings["deepl settings"].items():
            menu += key + " : " + str(value) + "\n"

        menu += """
It is recommended that you maximize the console window for this. You will have to to see the settings above.

Enter the name of the setting you want to change, type d to reset to default, type c to load an external/custom json directly, or type 'q' to quit settings change : 
"""

        return menu
    
##-------------------start-of-load_custom_json()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def load_custom_json() -> None:

        """

        Loads a custom json into the translation_settings.json file.

        """

        Toolkit.clear_console()

        ## saves old rules in case on invalid json
        old_translation_settings = JsonHandler.current_translation_settings

        try:

            ## loads the custom json file
            with open(FileEnsurer.external_translation_settings_path, 'r', encoding='utf-8') as file:
                JsonHandler.current_translation_settings = json.load(file) 

            JsonHandler.validate_json()

            ## validate_json() sets a dict to the invalid placeholder if it's invalid, so if it's that, it's invalid
            assert JsonHandler.current_translation_settings != FileEnsurer.INVALID_TRANSLATION_SETTINGS_PLACEHOLDER
            
            JsonHandler.dump_translation_settings()

            print("Settings loaded successfully.")
        
        except AssertionError:
            print("Invalid JSON file. Please try again.")
            JsonHandler.current_translation_settings = old_translation_settings

        except FileNotFoundError:
            print("Missing JSON file. Make sure you have a json in the same directory as kudasai.py and that the json is named \"translation_settings.json\". Please try again.")
            JsonHandler.current_translation_settings = old_translation_settings

##-------------------start-of-change_setting()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
    @staticmethod
    def change_setting(setting_area:str, setting_name:str) -> None:

        """

        Changes the setting of the translation_settings.json file.

        Parameters:
        setting_area (str) : The area of the setting to change.
        setting_name (str) : The name of the setting to change.

        """

        new_value = input(f"\nEnter a new value for {setting_name}: ")

        try:
            converted_value = JsonHandler.convert_to_correct_type(setting_name, new_value)

            JsonHandler.current_translation_settings[setting_area][setting_name] = converted_value
            print(f"Updated {setting_name} to {converted_value}.")
        
        except Exception as e:
            print(f"Invalid input. No changes made. {e}")