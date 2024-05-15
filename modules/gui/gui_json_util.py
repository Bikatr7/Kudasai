## built-in libraries
import json
import typing

## third-party libraries
import gradio as gr

## custom modules
from modules.common.file_ensurer import FileEnsurer

from handlers.json_handler import JsonHandler

class GuiJsonUtil:

    current_translation_settings = dict()

##-------------------start-of-fetch_kijiku_setting_key_values()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def fetch_translation_settings_key_values(header:str, key_name:str) -> str:
        
        """
        
        Fetches the default values for the settings tab from the translation_settings.json file.

        Parameters:
        key_name (str) : Which value to fetch.

        Returns:
        (str) : The default value for the specified key. 

        """

        ## Done this way because if the value is None, it'll be shown as a blank string in the settings tab, which is not what we want.
        return GuiJsonUtil.current_translation_settings[header].get(key_name, "None")
    
##-------------------start-of-update_translation_settings_with_new_values()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def update_translation_settings_with_new_values(gradio_translation_settings:gr.File, new_values:typing.List[typing.Tuple[str,str]]) -> None:

        """
        
        Dumps the new values for the settings tab into the translation_settings.json file.

        Parameters:
        new_values (typing.List[typing.Tuple[str,str]]) : A list of tuples containing the key and value to be updated.

        """

        ## save old json in case of need to revert
        old_rules = GuiJsonUtil.current_translation_settings
        new_rules = old_rules.copy()

        try:

            for header in new_rules.keys():
                for key, value in new_values:
                    new_rules[header][key] = JsonHandler.convert_to_correct_type(key, str(value))

            JsonHandler.current_translation_settings = new_rules
            JsonHandler.validate_json()

            ## validate_json() sets a dict to the invalid placeholder if it's invalid, so if it's that, it's invalid
            assert JsonHandler.current_translation_settings != FileEnsurer.INVALID_TRANSLATION_SETTINGS_PLACEHOLDER

            ## so, because of how gradio deals with temp file, we need to both dump into the settings file from FileEnsurer AND the gradio_translation_settings file which is stored in the temp folder under AppData
            ## name is the path to the file btw
            with open(FileEnsurer.config_translation_settings_path, "w") as file:
                json.dump(new_rules, file)

            with open(gradio_translation_settings.name, "w") as file: ## type: ignore
                json.dump(new_rules, file)

            GuiJsonUtil.current_translation_settings = new_rules

        except Exception as e:

            ## revert to old data
            with open(FileEnsurer.config_translation_settings_path, "w") as file:
                json.dump(old_rules, file)

            with open(gradio_translation_settings.name, "w") as file: ## type: ignore
                json.dump(old_rules, file)

            GuiJsonUtil.current_translation_settings = old_rules

            ## throw error so webgui can tell user
            raise e