## built-in libraries
from datetime import datetime

import os
import typing
import platform
import subprocess

class Toolkit():
    """
    
    A class containing various functions that are used throughout Kudasai.

    """

    CURRENT_VERSION = "v3.2.0"

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

        try:

            print(message)

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
    def check_update() -> typing.Tuple[bool, str]:

        """

        Determines if Kudasai has a new latest release, and confirms if an internet connection is present or not.

        Returns:
        is_connection (bool) : Whether or not the user has an internet connection.
        update_prompt (str) : The update prompt to be displayed to the user, can either be blank if there is no update or contain the update prompt if there is an update.

        """

        update_prompt = ""
        is_connection = True

        try:

            from urllib.request import urlopen
            import json
            from distutils.version import LooseVersion

            response = urlopen("https://api.github.com/repos/Bikatr7/Kudasai/releases/latest")
            data = json.loads(response.read().decode())

            latest_version = str(data["tag_name"])
            release_notes = data["body"]

            if(LooseVersion(latest_version) > LooseVersion(Toolkit.CURRENT_VERSION)):

                update_prompt += "There is a new update for Kudasai (" + latest_version + ")\nIt is recommended that you use the latest version of Kudasai\nYou can download it at https://github.com/Bikatr7/Kudasai/releases/latest \n"

                if(release_notes):
                    update_prompt += "\nRelease notes:\n\n" + release_notes + '\n'

            return is_connection, update_prompt

        ## used to determine if user lacks an internet connection.
        except:

            print("You seem to lack an internet connection, this will prevent you from checking from update notification and machine translation.\n")

            Toolkit.pause_console()

            is_connection = False

            return is_connection, update_prompt

##-------------------start-of-get_timestamp()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def get_timestamp(is_archival:bool=False) -> str:

        """
        
        Generates a timestamp for an action taken by Kudasai.

        Parameters:
        is_archival (bool | optional) : Whether or not the timestamp is for archival purposes.
        
        Returns:
        time_stamp (string) : The timestamp for the action.        
        
        """

        if(is_archival):
            time_stamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")

        else:
            time_stamp = "[" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] "

        return time_stamp