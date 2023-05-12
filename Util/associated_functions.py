import os
import requests

from typing import List

#-------------------start-of-clear_console()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def clear_console() -> None:

    """

    clears the console\n

    Parameters:\n
    None\n

    Returns:\n
    None\n

    """

    os.system('cls' if os.name == 'nt' else 'clear')

#-------------------start-of-pause_console()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def pause_console(message="Press any key to continue . . ."):

    """

    pauses the console\n

    Parameters:\n
    message (string) the message that will be displayed when the console is paused\n

    Returns:\n
    None\n

    """

    if(os.name == 'nt'):  # Windows
        os.system('pause /P f{message}')
    else: 
        input(message)

#-------------------start-of-get_elapsed_time()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def get_elapsed_time(start:float, end:float) -> str:

    """

    calculates elapsed time\n

    Parameters:\n
    start (float): start time\n
    end (float): end time\n

    Returns:\n
    printValue (string) elapsed time\n

    """

    printValue = ""

    if(end-start < 60.0):
        printValue = str(round(end-start, 2)) + " seconds"
    
    elif(end-start < 3600.0):
        printValue = str(round((end-start)/60, 2)) + " minutes"
    
    else:
        printValue = str(round((end-start)/3600, 2)) + " hours"

    return printValue

#-------------------start-of-output_results()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def output_results(scriptDir:str, configDir:str, debugText:List[str], jeCheckText:List[str], finalText:List[str], errorText:List[str],fromGui) -> None:

        '''

        Outputs results to several txt files\n

        Parameters:\n
        scriptDir (string) the path of the directory that holds Kudasai.py\n
        debugText (list - string) debug text\n
        jeCheckText (list - string) J->E text\n
        finalText (list - string) translated text\n
        errorText (list - string) errors\n

        Returns:\n
        None\n

        '''

        outputDir = os.path.join(scriptDir, "KudasaiOutput")

        if(not os.path.exists(outputDir)):
               os.mkdir(outputDir)

        debugPath = os.path.join(outputDir, "tlDebug.txt")
        jePath = os.path.join(outputDir, "jeCheck.txt")
        resultsPath = os.path.join(outputDir, "translatedText.txt")
        errorPath = os.path.join(outputDir, "errors.txt")

        with open(debugPath, 'w+', encoding='utf-8') as file:
                file.writelines(debugText)

        with open(jePath, 'w+', encoding='utf-8') as file: 
                file.writelines(jeCheckText)

        with open(resultsPath, 'w+', encoding='utf-8') as file:
                file.writelines(finalText)

        with open(errorPath, 'w+', encoding='utf-8') as file:
                file.writelines(errorText)


        if(fromGui):
            with open(os.path.join(configDir,"guiTempTranslationLog.txt"), "a+", encoding="utf-8") as file: # Write the text to a temporary file
                file.write("Debug text have been written to : " + debugPath + "\n\n")
                file.write("J->E text have been written to : " + jePath + "\n\n")
                file.write("Translated text has been written to : " + resultsPath + "\n\n")
                file.write("Errors have been written to : " + errorPath + "\n\n")

            return
        
        print("\n\nDebug text have been written to : " + debugPath)
        print("\nJ->E text have been written to : " + jePath)
        print("\nTranslated text has been written to : " + resultsPath)
        print("\nErrors have been written to : " + errorPath + "\n")

#-------------------start-of-check_update()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def check_update() -> bool:

    """

    determines if Kudasai has a new latest release, and confirms if an internet connection is present or not\n

    Parameters:\n
    None\n

    Returns:\n
    True if the user has an internet connection, False if the user does not\n
    """

    try:
    
        CURRENT_VERSION = "v1.5.0beta" 

        response = requests.get("https://api.github.com/repos/Seinuve/Kudasai/releases/latest")
        latestVersion = response.json()["tag_name"]

        if(latestVersion != CURRENT_VERSION):
            print("There is a new update for Kudasai (" + latestVersion + ")\nIt is recommended that you use the latest version of Kudasai\nYou can download it at https://github.com/Seinuve/Kudasai/releases/latest \n")
            pause_console()
            clear_console()

        return True

    except: ## used to determine if user lacks an internet connection or possesses another issue that would cause the automated mtl to fail

        return False