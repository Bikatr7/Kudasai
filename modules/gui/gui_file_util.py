## third-party libraries
import gradio as gr


##-------------------start-of-gui_get_text_from_file()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def gui_get_text_from_file(filepath) -> str:

    """

    Runs the preprocessing.

    Parameters:
    filepath (str) : The path to the input file.

    """

    txt_file_path:str = filepath.name ## type: ignore | name is not type hinting for some fucking reason

    with open(txt_file_path, "r", encoding='utf-8') as file:
        text = file.read()

    return text