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

def check_update(from_gui:bool) -> bool:

    """

    determines if Kudasai has a new latest release, and confirms if an internet connection is present or not\n

    Parameters:\n
    from_gui (bool) : whether or not the function call is from the gui

    Returns:\n
    True if the user has an internet connection, False if the user does not\n

    """

    if(os.name == 'nt'):  # Windows
        config_dir = os.path.join(os.environ['USERPROFILE'],"KudasaiConfig")
    else:  ## Linux
        config_dir = os.path.join(os.path.expanduser("~"), "KudasaiConfig")

    ## the temp file for the gui, used to detect if an update is available
    is_there_update_path = os.path.join(config_dir, "isThereUpdate.txt")
    
    try:
    
        CURRENT_VERSION = "v1.5.3" 

        response = requests.get("https://api.github.com/repos/Seinuve/Kudasai/releases/latest")
        latestVersion = response.json()["tag_name"]

        if(not from_gui):

            if(latestVersion != CURRENT_VERSION):
                print("There is a new update for Kudasai (" + latestVersion + ")\nIt is recommended that you use the latest version of Kudasai\nYou can download it at https://github.com/Seinuve/Kudasai/releases/latest \n")
                pause_console()
                clear_console()

        else:
            if(latestVersion != CURRENT_VERSION):
                with open(is_there_update_path, 'w+', encoding='utf-8') as file:
                    file.write("true")

            else:
                with open(is_there_update_path, 'w+', encoding='utf-8') as file:
                    file.write("false")

        return True

    except: ## used to determine if user lacks an internet connection or possesses another issue that would cause the automated mtl to fail

        if(from_gui):
            with open(is_there_update_path, 'w+', encoding='utf-8') as file:
                file.write("false")
                
        return False