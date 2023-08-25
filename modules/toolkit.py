## built-in modules
import os
import msvcrt
import requests
import typing

class toolkit():

    """
    
    The class for a bunch of utility functions used throughout Kudasai.\n

    """

##-------------------start-of-__init__()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self) -> None:

        """
        
        Constructor for the toolkit class.\n

        Parameters:\n
        None.\n

        Returns:\n
        None.\n

        """

        self.CURRENT_VERSION = "v1.5.4" 

##-------------------start-of-clear_console()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def clear_console(self) -> None:

        """

        clears the console\n

        Parameters:\n
        self (object - toolkit) : the toolkit object.\n

        Returns:\n
        None\n

        """

        os.system('cls' if os.name == 'nt' else 'clear')

##-------------------start-of-pause_console()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def pause_console(self, message:str="Press any key to continue...") -> None:

        """

        Pauses the console.\n

        Parameters:\n
        self (object - toolkit) : the toolkit object.\n
        message (str | optional) : the message that will be displayed when the console is paused.\n

        Returns:\n
        None\n

        """

        print(message)  ## Print the custom message
        
        if(os.name == 'nt'):  ## Windows
            
            msvcrt.getch() 

        else:  ## Linux, No idea if any of this works lmao

            import termios

            ## Save terminal settings
            old_settings = termios.tcgetattr(0)

            try:
                new_settings = termios.tcgetattr(0)
                new_settings[3] = new_settings[3] & ~termios.ICANON
                termios.tcsetattr(0, termios.TCSANOW, new_settings)
                os.read(0, 1)  ## Wait for any key press

            finally:

                termios.tcsetattr(0, termios.TCSANOW, old_settings)

##-------------------start-of-get_elapsed_time()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def get_elapsed_time(self, start:float, end:float) -> str:

        """

        calculates elapsed time\n

        Parameters:\n
        self (object - toolkit) : the toolkit object.\n
        start (float): start time\n
        end (float): end time\n

        Returns:\n
        print_value (string) elapsed time\n

        """

        print_value = ""

        if(end-start < 60.0):
            print_value = str(round(end-start, 2)) + " seconds"
        
        elif(end-start < 3600.0):
            print_value = str(round((end-start)/60, 2)) + " minutes"
        
        else:
            print_value = str(round((end-start)/3600, 2)) + " hours"

        return print_value


##-------------------start-of-check_update()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def check_update(self) -> typing.Tuple[bool,str]:

        """

        Determines if Kudasai has a new latest release, and confirms if an internet connection is present or not.\n

        Parameters:\n
        self (object - toolkit) : the toolkit object.\n

        Returns:\n
        is_connection (bool) : whether or not the user has an internet connection.\n
        update_prompt (str) : the update prompt to be displayed to the user, can either be blank if there is no update or contain the update prompt if there is an update.\n

        """

        update_prompt = ""
        is_connection = True
        
        try:
        
            response = requests.get("https://api.github.com/repos/Seinuve/Kudasai/releases/latest")
            latest_version = response.json()["tag_name"]
            release_notes = response.json()["body"]

            if(latest_version != self.CURRENT_VERSION):
                update_prompt += "There is a new update for Kudasai (" + latest_version + ")\nIt is recommended that you use the latest version of Kudasai\nYou can download it at https://github.com/Seinuve/Kudasai/releases/latest \n"
            
                if(release_notes):
                    update_prompt += "\nRelease notes:\n\n" + release_notes + '\n'


            return is_connection, update_prompt

        ## used to determine if user lacks an internet connection or possesses another issue that would cause the automated mtl to fail
        except:

            is_connection = False 
                    
            return is_connection, update_prompt
