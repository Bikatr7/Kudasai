## built-in libraries
import json
import typing
import regex

## custom modules
from modules.common.file_ensurer import FileEnsurer

##-------------------start-of-GenderUtil---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class GenderUtil:

    genders:typing.Optional[dict] = None
    cache = {}

##-------------------start-of-find_english_words()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def find_english_words(text:str) -> list[tuple[str, int]]:

        """

        Finds the english words in the text.

        Parameters:
        text (str) : The text to be searched.

        Returns:
        (list[tuple[str, int]]) : The list of words and their starting index.

        """

        return [(match.group(), match.start()) for match in regex.finditer(r'\p{Latin}+', text)]
    
##-------------------start-of-is_potential_name()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def is_potential_name(word:str) -> bool:
        
        """
        
        Assuming words are potential names and excluding full-width Latin characters, this function returns a boolean value indicating whether the word is a potential name.
        
        Parameters:
        word (str) : The word to be checked.

        Returns:
        (bool) : The result of the check.

        """

        return not any(0xFF00 <= ord(ch) <= 0xFFEF for ch in word)
    
##-------------------start-of-group_names()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def group_names(text, names_with_positions: list[tuple[str, int]], max_distance: int = 10) -> list[str]:

        """

        Groups names together if they follow one another within a certain distance and are separated by spaces.

        Parameters:
        text (str) : The text to be searched.
        names_with_positions (list[tuple[str, int]]) : The names with their positions.
        max_distance (int) : The maximum distance between names.
        
        Returns:
        (list[str]) : The grouped names.

        """

        honorifics = [
            "chan",
            "dono",
            "kun",
            "kōhai",
            "paisen",
            "sama",
            "san",
            "senpai",
            "sensei",
            "shi",
            "ue"
        ]

        grouped_names = []
        i = 0
        skip_next = False
        length = len(names_with_positions)
        
        while i < length - 1:

            if(skip_next):
                skip_next = False

            else:
                current_name, current_pos = names_with_positions[i]
                next_name, next_pos = names_with_positions[i + 1]
                
                ## Check if names are separated by spaces and are within the maximum distance.
                separator = text[current_pos + len(current_name):next_pos]

                if(GenderUtil.is_potential_name(next_name) and (separator.isspace()) and next_pos - current_pos <= max_distance):
                    grouped_names.append(current_name + " " + next_name)
                    skip_next = True
                else:
                    grouped_names.append(current_name)
            i += 1
        
        if(not skip_next and names_with_positions):
            grouped_names.append(names_with_positions[-1][0])

        ## merge honorifics with names
        for i, name in enumerate(grouped_names):
            if(i + 1 < len(grouped_names) and grouped_names[i + 1].lower() in honorifics):
                grouped_names[i] += "-" + grouped_names[i + 1]
                grouped_names.pop(i + 1)
        
        return grouped_names

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

        Returns:
        new_names (list[str]) : The filtered names.

        """

        if(GenderUtil.genders is None):
            GenderUtil.genders = GenderUtil.load_genders(FileEnsurer.external_translation_genders_path)

        new_names = [name for name in names if any(GenderUtil.honorific_stripper(name) in full_name for gender, gender_names in GenderUtil.genders.items() for full_name, _ in gender_names.items())]

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
    
##-------------------start-of-reverse_honorific_stripper()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def reverse_honorific_stripper(name:str) -> str:

        """

        Removes the name from the honorific. (Gets the honorific)

        Parameters:
        name (str) : The name to be stripped.

        Returns:
        (str) : The stripped name.

        """

        if("-" in name):
            return name.split("-")[1]
        
        return ""
    
##-------------------start-of-find_name_gender()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def find_name_gender(name:str, is_cote:bool = False) -> list[str]:

        """

        Finds the gender associated to a name.

        Parameters:
        name (str) : The name to find

        Returns:
        result (list[str])

        """

        ## known names that are literally 99% this
        cote_predetermined: typing.Dict[typing.Tuple[str, str], str] = {
            ("Sakayanagi", "san"): "Female",
            ("Horikita", "san"): "Female",
            ("Horikita", ""): "Female",
            ("Sakayanagi", ""): "Female",
            ("Sakayanagi", "sama"): "Male",
            ("Sakayanagi", "sensei"): "Male"
        }

        if(GenderUtil.genders is None):
            GenderUtil.genders = GenderUtil.load_genders(FileEnsurer.external_translation_genders_path)

        if(name in GenderUtil.cache):
            return GenderUtil.cache[name]
        
        honorific = GenderUtil.reverse_honorific_stripper(name)
        stripped_name = GenderUtil.honorific_stripper(name)

        ## check if the name is predetermined
        if((stripped_name, honorific) in cote_predetermined and is_cote):
            result = [cote_predetermined[(stripped_name, honorific)]]
            GenderUtil.cache[name] = result
            return result

        result = [gender for gender, names in GenderUtil.genders.items() for full_name in names if stripped_name in full_name]

        print(result)

        if(len(set(result)) > 1 or result == ["Unknown"]):
            if(honorific == "kun"):
                result = ["Male"]
            elif(honorific == "chan"):
                result = ["Female"]
            
            else:
                result = ["Unknown"]

        GenderUtil.cache[name] = result

        return result