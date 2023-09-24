## built-in libaries


## custom modules


class docxHandler():

    """
    
    Handles docx to txt conversions.\n

    """
##--------------------start-of-__init__()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, inc_docx_path:str, inc_image_kanji_replacement_dict:dict) -> None:

        """

        Initializes the docxHandler class.\n

        Parameters:\n
        inc_docx_path (str) : The path to the docx file.\n
        inc_image_kanji_replacement_dict (dict) : The dictionary containing the image replacements.\n

        Returns:\n
        None.\n

        """

        docx_path = inc_docx_path

        image_kanji_replacement_dict = inc_image_kanji_replacement_dict["image_replacements"]