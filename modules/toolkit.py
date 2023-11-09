## built-in modules
import os
import typing
import platform
import subprocess

class Toolkit():

    """
    
    The class for a bunch of utility functions used throughout Kudasai.

    """

    CURRENT_VERSION = "v2.1.3" 

##-------------------start-of-clear_console()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def clear_console() -> None:

        """

        Clears the console.

        """
        
        os.system('cls' if os.name == 'nt' else 'clear')

##-------------------start-of-pause_console()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def pause_console(message:str="Press any key to continue...") -> None:

        """

        Pauses the console.
        Requires msvcrt on Windows and termios on Linux/Mac, will do nothing if neither are present.

        Parameters:
        message (string | optional) : The custom message to be displayed to the user.

        """


        print(message)

        try:
        
            ## Windows
            if(os.name == 'nt'): 

                import msvcrt
                
                msvcrt.getch() 

            ## Linux and Mac
            elif(os.name == 'posix'):  

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

        except ImportError:

            pass

##-------------------start-of-maximize_window()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def maximize_window():

        """
        
        Maximizes the console window.

        """

        try:

            system_name = platform.system()

            if(system_name == "Windows"):
                os.system('mode con: cols=140 lines=40')

            elif(system_name == "Linux"):
                print("\033[8;40;140t")

            elif(system_name == "Darwin"):
                subprocess.call(["printf", "'\\e[8;40;140t'"])

        except:
            pass

##-------------------start-of-minimize_window()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def minimize_window():

        """
        
        Minimizes the console window.

        """

        try:

            system_name = platform.system()

            if(system_name == "Windows"):
                os.system('mode con: cols=80 lines=25')

            elif(system_name == "Linux"):
                print("\033[8;25;80t")

            elif(system_name == "Darwin"):
                subprocess.call(["printf", "'\\e[8;25;80t'"])

        except:
            pass

##-------------------start-of-get_elapsed_time()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def get_elapsed_time(start:float, end:float) -> str:

        """

        Calculates elapsed time with an offset.

        Parameters:
        start (float) : Start time.
        end (float) : End time.

        Returns:
        print_value (string): The elapsed time in a human-readable format.

        """

        elapsed_time = end - start
        print_value = ""

        if(elapsed_time < 60.0):
            print_value = str(round(elapsed_time, 2)) + " seconds"
        elif(elapsed_time < 3600.0):
            print_value = str(round(elapsed_time / 60, 2)) + " minutes"
        else:
            print_value = str(round(elapsed_time / 3600, 2)) + " hours"

        return print_value


##-------------------start-of-check_update()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def check_update() -> typing.Tuple[bool,str]:

        """

        Determines if Kudasai has a new latest release, and confirms if an internet connection is present or not.
        If requests is not installed, it will return is_connection as False.

        Returns:
        is_connection (bool) : Whether or not the user has an internet connection.
        update_prompt (str) : The update prompt to be displayed to the user, can either be blank if there is no update or contain the update prompt if there is an update.

        """

        update_prompt = ""
        is_connection = True
        
        try:

            import requests
        
            response = requests.get("https://api.github.com/repos/Bikatr7/Kudasai/releases/latest")
            latest_version = response.json()["tag_name"]
            release_notes = response.json()["body"]

            if(latest_version != Toolkit.CURRENT_VERSION):
                update_prompt += "There is a new update for Kudasai (" + latest_version + ")\nIt is recommended that you use the latest version of Kudasai\nYou can download it at https://github.com/Bikatr7/Kudasai/releases/latest \n"
            
                if(release_notes):
                    update_prompt += "\nRelease notes:\n\n" + release_notes + '\n'


            return is_connection, update_prompt

        ## used to determine if user lacks an internet connection or possesses another issue that would cause the automated mtl to fail.
        except:

            is_connection = False 
                    
            return is_connection, update_prompt
