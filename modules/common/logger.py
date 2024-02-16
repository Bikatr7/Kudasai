## custom modules
from modules.common.toolkit import Toolkit
from modules.common.decorators import permission_error_decorator

class Logger:

    """
    
    The logger class is used to log actions taken by Kudasai.

    """

    log_file_path = ""

    current_batch = ""

    errors = []
    
##--------------------start-of-log_action()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def log_action(action:str, output:bool=False, omit_timestamp:bool=False) -> None:

        """
        
        Logs an action.

        Parameters:
        action (str) : the action being logged.
        output (bool | optional | defaults to false) : whether or not to output the action to the console.
        omit_timestamp (bool | optional | defaults to false) : whether or not to omit the timestamp from the action.
 
        """

        timestamp = Toolkit.get_timestamp() 

        log_line = timestamp + action + "\n"

        Logger.current_batch += log_line

        if(omit_timestamp):
            log_line = action

        if(output):
            print(log_line)

##--------------------start-of-log_error()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def log_error(action:str, output:bool=False, omit_timestamp:bool=False) -> None:

        """
        
        Logs an error.

        Parameters:
        action (str) : the action being logged.
        output (bool | optional | defaults to false) : whether or not to output the action to the console.
        omit_timestamp (bool | optional | defaults to false) : whether or not to omit the timestamp from the action.
 
        """

        timestamp = Toolkit.get_timestamp() 

        log_line = timestamp + action + "\n"

        Logger.current_batch += log_line

        if(omit_timestamp):
            log_line = action

        if(output):
            print(log_line)

        Logger.errors.append(log_line)

##--------------------start-of-log_barrier()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def log_barrier() -> None:
            
        """
        
        Logs a barrier.

        """
    
        Logger.log_action("-------------------------")

##--------------------start-of-clear_batch()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def clear_batch() -> None:

        """
        
        Clears the current batch.

        """

        Logger.current_batch = ""
        Logger.errors = []

##--------------------start-of-push_batch()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    @permission_error_decorator()
    def push_batch() -> None:

        """
        
        Pushes all stored actions to the log file.

        """

        with open(Logger.log_file_path, 'a+', encoding="utf-8") as file:
            file.write(Logger.current_batch)

##--------------------start-of-clear_log_file()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    @permission_error_decorator()
    def clear_log_file() -> None:

        """
        
        Clears the log file.
        
        """

        with open(Logger.log_file_path, 'w+', encoding="utf-8") as file:
            file.truncate(0)
