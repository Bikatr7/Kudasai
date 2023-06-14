## built-in modules
import os
import requests

##-------------------start-of-clear_console()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def clear_console() -> None:

    """

    clears the console\n

    Parameters:\n
    None\n

    Returns:\n
    None\n

    """

    os.system('cls' if os.name == 'nt' else 'clear')

##-------------------start-of-pause_console()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def pause_console(message:str="Press enter to continue . . .") -> None:

    """

    pauses the console\n

    Parameters:\n
    message (string) the message that will be displayed when the console is paused\n

    Returns:\n
    None\n

    """

    if(os.name == 'nt'):  ## Windows
        os.system('pause /P f{message}')
    else: ## Linux
        input(message)

##-------------------start-of-get_elapsed_time()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def get_elapsed_time(start:float, end:float) -> str:

    """

    calculates elapsed time\n

    Parameters:\n
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

def check_update() -> bool:

    """

    determines if Kudasai has a new latest release, and confirms if an internet connection is present or not\n

    Parameters:\n
    None\n

    Returns:\n
    True if the user has an internet connection, False if the user does not\n

    """

    try:
    
        CURRENT_VERSION = "v1.5.1" 

        response = requests.get("https://api.github.com/repos/Seinuve/Kudasai/releases/latest")
        latestVersion = response.json()["tag_name"]

        if(latestVersion != CURRENT_VERSION):
            print("There is a new update for Kudasai (" + latestVersion + ")\nIt is recommended that you use the latest version of Kudasai\nYou can download it at https://github.com/Seinuve/Kudasai/releases/latest \n")
            pause_console()
            clear_console()

        return True

    except: ## used to determine if user lacks an internet connection or possesses another issue that would cause the automated mtl to fail

        return False