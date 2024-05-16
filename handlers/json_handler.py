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

    with open(FileEnsurer.translation_settings_description_path, 'r', encoding='utf-8') as file:
        translation_settings_message = file.read()


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

        logging.debug(f"translation_settings.json is valid, current:"
                    f"\n{JsonHandler.current_translation_settings}")    

##-------------------start-of-reset_translation_settings_to_default()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def reset_translation_settings_to_default() -> None:

        """

        Resets the translation_settings.json to default.

        """

        JsonHandler.current_translation_settings = FileEnsurer.DEFAULT_TRANSLATION_SETTING
        
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
    def log_translation_settings(output_to_console:bool=False, specific_section:str | None = None) -> None:

        """

        Prints the translation_settings.json file to the log.
        Logs by default, but can be set to print to console as well.

        Parameters:
        output_to_console (bool | optional | default=False) : Whether to print to console as well.

        """
        
        sections = ["base translation settings", "openai settings", "gemini settings", "deepl settings"]
        
        ## if a specific section is provided, only print that section and base translation settings
        if(specific_section is not None):
            specific_section = specific_section.lower()
            sections = [section for section in sections if section.lower() == specific_section or section == "base translation settings"]

        for section in sections:
            print("-------------------")
            print(f"{section.capitalize()}:")
            print("-------------------")
        
            for key, value in JsonHandler.current_translation_settings.get(section, {}).items():
                log_message = f"{key} : {value}"
                logging.debug(log_message)
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