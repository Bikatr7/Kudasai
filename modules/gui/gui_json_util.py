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

        for key, value in new_values:
            data["open ai settings"][key] = value

        with open(GuiJsonUtil.current_kijiku_rules, "w") as file:
            json.dump(data, file)