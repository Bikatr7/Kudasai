import os

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

def output_results(scriptDir:str, debugText:List[str], jeCheckText:List[str], finalText:List[str], errorText:List[str]) -> None:

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

        print("\n\nDebug text have been written to : " + debugPath)
        print("\nJ->E text have been written to : " + jePath)
        print("\nTranslated text has been written to : " + resultsPath)
        print("\nErrors have been written to : " + errorPath + "\n")