## built-in libraries
import json

## custom modules
from modules.common.file_ensurer import FileEnsurer

class GenderUtil:

    genders = None

    @staticmethod
    def load_genders(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
        

    @staticmethod
    def discard_non_names(names: list[str]) -> list[str]:
        if(GenderUtil.genders is None):
            GenderUtil.genders = GenderUtil.load_genders(FileEnsurer.external_translation_genders_path)

        new_names = []

        for name in names:
            for gender, gender_names in GenderUtil.genders.items():
                for full_name, _ in gender_names.items(): 
                    if(name in full_name):
                        new_names.append(name)
                        break

        return new_names


    @staticmethod
    def honorific_stripper(name:str) -> str:
        if("-" in name):
            return name.split("-")[0]
        
        return name

    @staticmethod
    def find_name_gender(name:str) -> list[str]:
        result = []

        if(GenderUtil.genders is None):
            GenderUtil.genders = GenderUtil.load_genders(FileEnsurer.external_translation_genders_path)

        for gender, names in GenderUtil.genders.items():
            for full_name, _ in names.items():
                if(name in full_name):
                    result.append(gender)

        return result