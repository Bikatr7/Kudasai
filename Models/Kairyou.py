##-------------------start-of-Kairyou---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Kairyou:

    """

    Kairyou is the preprocessor for the Kudasai program.
    
    """

##-------------------start-of-__init__()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, from_gui:bool) -> None: 

        """
        
        Constructor for Kairyou class.\n

        Parameters:\n
        from_gui (bool) : indicates whether or not the request is from the gui.\n

        Returns:\n
        None\n

        """

        self.from_gui = from_gui