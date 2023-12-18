## built-in libraries
import json

## custom modules
from modules.common.file_ensurer import FileEnsurer

##-

def fetch_kijiku_settings_tab_default_values(key_name:str) -> str:
    
    """
    
    Fetches the default values for the settings tab from the kijiku_settings.json file.

    Parameters:
    key_name (str) : Which value to fetch.

    Returns:
    (str) : The default value for the specified key. 

    """

    with open(FileEnsurer.config_kijiku_rules_path, "r") as f:
        data = json.load(f)

    return data["open ai settings"][key_name]
