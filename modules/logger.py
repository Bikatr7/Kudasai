## custom modules
from modules.toolkit import Toolkit

class Logger:

    """
    
    The logger class is used to log actions taken by Kudasai.

    """

    log_file_path = ""

    current_batch = ""
    
##--------------------start-of-log_action()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def log_action(action:str, output:bool=False, omit_timestamp:bool=False, is_error:bool=False) -> str:

        """
        
        Logs an action.

        Parameters:
        action (str) : the action being logged.
        output (bool | optional | defaults to false) : whether or not to output the action to the console.
        omit_timestamp (bool | optional | defaults to false) : whether or not to omit the timestamp from the action.
        is_error (bool | optional | defaults to false) : whether or not the action is an error.
 
        """

        time_stamp = Toolkit.get_timestamp()

        if(omit_timestamp):
            time_stamp = ""

        Logger.current_batch += time_stamp + action + "\n"

        if(output):
            print(time_stamp + action + "\n")

        if(is_error):
            return time_stamp + action + "\n"
        
        return ""

##--------------------start-of-log_barrier()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def log_barrier():
            
        """
        
        Logs a barrier.

        """
    
        Logger.log_action("-------------------------")

##--------------------start-of-push_batch()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def push_batch():

        """
        
        Pushes all stored actions to the log file.

        """

        with open(Logger.log_file_path, 'a+', encoding="utf-8") as file:
            file.write(Logger.current_batch)

        Logger.current_batch = ""

##--------------------start-of-clear_log_file()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def clear_log_file():

        """
        
        Clears the log file.
        
        """

        with open(Logger.log_file_path, 'w+', encoding="utf-8") as file:
            file.truncate(0)
