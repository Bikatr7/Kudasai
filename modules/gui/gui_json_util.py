## built-in libraries
import json
import typing

## custom modules
from modules.common.file_ensurer import FileEnsurer

from handlers.json_handler import JsonHandler

class GuiJsonUtil:

    current_kijiku_rules = FileEnsurer.config_kijiku_rules_path

##-------------------start-of-fetch_kijiku_settings_tab_default_values()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def fetch_kijiku_settings_tab_default_values(key_name:str) -> str:
        
        """
        
        Fetches the default values for the settings tab from the kijiku_settings.json file.

        Parameters:
        key_name (str) : Which value to fetch.

        Returns:
        (str) : The default value for the specified key. 

        """

        with open(GuiJsonUtil.current_kijiku_rules, "r") as file:
            data = json.load(file)

        return data["open ai settings"][key_name]
    
##-------------------start-of-update_kijiku_settings_with_new_values()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def update_kijiku_settings_with_new_values(new_values:typing.List[typing.Tuple[str,str]]) -> None:

        """
        
        Dumps the new values for the settings tab into the kijiku_settings.json file.

        Parameters:
        new_values (typing.List[typing.Tuple[str,str]]) : A list of tuples containing the key and value to be updated.

        """

        with open(GuiJsonUtil.current_kijiku_rules, "r") as file:
            data = json.load(file)

        ## save old json in case of need to revert
        old_data = data

        JsonHandler.current_kijiku_rules = data

        try:

            for key, value in new_values:
                data["open ai settings"][key] = JsonHandler.convert_to_correct_type(key, value)

            with open(GuiJsonUtil.current_kijiku_rules, "w") as file:
                json.dump(data, file)

            JsonHandler.validate_json()

            ## validate_json() sets a dict to the invalid placeholder if it's invalid, so if it's that, it's invalid
            assert JsonHandler.current_kijiku_rules != FileEnsurer.invalid_kijiku_rules_placeholder

        except Exception as e:

            ## revert to old data
            with open(GuiJsonUtil.current_kijiku_rules, "w") as file:
                json.dump(old_data, file)

            ## throw error so webgui can tell user
            raise e