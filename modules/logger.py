## built-in imports
import datetime

class Logger:

    """
    
    The logger class is used to log actions taken by Kudasai.

    """

    log_file_path = ""

    current_batch = ""

##--------------------start-of-get_time_stamp()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def get_time_stamp():

        """
        
        Gets the time stamp for a logging action taken.

        Returns:\n
        time_stamp (str) : The time stamp for the logging action.

        """

        current_date = datetime.date.today().strftime("%Y-%m-%d")

        current_time = datetime.datetime.now().time().strftime("%H:%M:%S")

        time_stamp = "(" + current_date + " " + current_time + ") : "

        return time_stamp
    
##--------------------start-of-log_action()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def log_action(action:str):

        """
        
        Logs an action.

        Parameters:
        action (str) : the action being logged.
 
        """

        time_stamp = Logger.get_time_stamp()

        Logger.current_batch += time_stamp + action + "\n"

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
