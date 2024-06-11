## built-in libraries
import json
import typing

## custom modules
from modules.common.file_ensurer import FileEnsurer

##-------------------start-of-GenderUtil---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class GenderUtil:

    genders:typing.Optional[dict] = None
    cache = {}

##-------------------start-of-load_genders()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def load_genders(file_path:str) -> dict:

        """
        
        Loads the genders from the specified file path.

        Parameters:
        file_path (str) : The file

        Returns:
        (dict) : The loaded json.

        """

        GenderUtil.cache = {}

        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
        
##-------------------start-of-discard_non_names()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def discard_non_names(names: list[str]) -> list[str]:

        """
        
        Discards any names that are not in the gender list.

        Parameters:
        names (list[str]) : The names to be filtered.

        Returns:D
        new_names (list[str]) : The filtered names.

        """

        if(GenderUtil.genders is None):
            GenderUtil.genders = GenderUtil.load_genders(FileEnsurer.external_translation_genders_path)

        new_names = [name for name in names if any(name in full_name for gender, gender_names in GenderUtil.genders.items() for full_name, _ in gender_names.items())]

        return new_names
            
##-------------------start-of-honorific_stripper()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def honorific_stripper(name:str) -> str:

        """

        Strips the honorific from the name.

        Parameters:
        name (str) : The name to be stripped.

        Returns:
        (str) : The stripped name.

        """

        if("-" in name):
            return name.split("-")[0]
        
        return name
    
##-------------------start-of-find_name_gender()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def find_name_gender(name:str) -> list[str]:

        """

        Finds the gender associated to a name.

        Parameters:
        name (str) : The name to find

        Returns:
        result (list[str])

        """

        if(GenderUtil.genders is None):
            GenderUtil.genders = GenderUtil.load_genders(FileEnsurer.external_translation_genders_path)

        if(name in GenderUtil.cache):
            return GenderUtil.cache[name]

        result = []

        result = [gender for gender, names in GenderUtil.genders.items() for full_name in names if name in full_name]

        GenderUtil.cache[name] = result

        return result