## built-in libraries
import json
import typing

## third-party libraries
import gradio as gr

## custom modules
from modules.common.file_ensurer import FileEnsurer

from handlers.json_handler import JsonHandler

class GuiJsonUtil:

    current_kijiku_rules = dict()

##-------------------start-of-fetch_kijiku_setting_key_values()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def fetch_kijiku_setting_key_values(key_name:str) -> str:
        
        """
        
        Fetches the default values for the settings tab from the kijiku_settings.json file.

        Parameters:
        key_name (str) : Which value to fetch.

        Returns:
        (str) : The default value for the specified key. 

        """

        ## Done this way because if the value is None, it'll be shown as a blank string in the settings tab, which is not what we want.
        return GuiJsonUtil.current_kijiku_rules["open ai settings"].get(key_name, "None")
    
##-------------------start-of-update_kijiku_settings_with_new_values()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def update_kijiku_settings_with_new_values(gradio_kijiku_rule:gr.File, new_values:typing.List[typing.Tuple[str,str]]) -> None:

        """
        
        Dumps the new values for the settings tab into the kijiku_settings.json file.

        Parameters:
        new_values (typing.List[typing.Tuple[str,str]]) : A list of tuples containing the key and value to be updated.

        """

        ## save old json in case of need to revert
        old_rules = GuiJsonUtil.current_kijiku_rules
        new_rules = old_rules.copy()

        try:

            for header in new_rules.keys():
                for key, value in new_values:
                    new_rules[header][key] = JsonHandler.convert_to_correct_type(key, str(value))

            JsonHandler.current_kijiku_rules = new_rules
            JsonHandler.validate_json()

            ## validate_json() sets a dict to the invalid placeholder if it's invalid, so if it's that, it's invalid
            assert JsonHandler.current_kijiku_rules != FileEnsurer.INVALID_KIJIKU_RULES_PLACEHOLDER

            ## so, because of how gradio deals with temp file, we need to both dump into the settings file from FileEnsurer AND the gradio_kijiku_rule file which is stored in the temp folder under AppData
            ## name is the path to the file btw
            with open(FileEnsurer.config_kijiku_rules_path, "w") as file:
                json.dump(new_rules, file)

            with open(gradio_kijiku_rule.name, "w") as file: ## type: ignore
                json.dump(new_rules, file)

            GuiJsonUtil.current_kijiku_rules = new_rules

        except Exception as e:

            ## revert to old data
            with open(FileEnsurer.config_kijiku_rules_path, "w") as file:
                json.dump(old_rules, file)

            with open(gradio_kijiku_rule.name, "w") as file: ## type: ignore
                json.dump(old_rules, file)

            GuiJsonUtil.current_kijiku_rules = old_rules

            ## throw error so webgui can tell user
            raise e