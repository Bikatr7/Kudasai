## built-in libraries
import json

##-------------------start-of-gui_get_text_from_file()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def gui_get_text_from_file(file) -> str:

    """

    This function extracts the text from a file.

    Parameters:
    file (gr.File) : The file to extract the text from.

    """

    file_path:str = file.name ## type: ignore | name is not type hinting for some fucking reason

    with open(file_path, "r", encoding='utf-8') as file:
        text = file.read()

    return text

##-------------------start-of-gui_get_json_from_file()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def gui_get_json_from_file(file) -> dict:

    """
    
    This functions extracts the text from a json file and forms it into a dict.

    Parameters:
    file (gr.File) : The file to form a json from.
    
    """

    file_path:str = file.name ## type: ignore | name is not type hinting for some fucking reason

    with open(file_path, 'r', encoding='utf-8') as file: 
        json_dict = json.load(file) 

    return json_dict