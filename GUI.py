## Built-in modules
import os
import tkinter as tk
import typing

from tkinter import scrolledtext

## Custom modules
from Models.Kaiseki import Kaiseki
from Models.Kijiku import Kijiku
from Util.associated_functions import check_update
from Kudasai import Kudasai

##-------------------start-of-KudasaiGUI---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class KudasaiGUI:

    """

    The gui for Kudasai\n

    """

##-------------------start-of-__init__()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self) -> None:

        """

        Initializes the KudasaiGUI class\n

        Parameters:\n
        self (object - KudasaiGUI) : The KudasaiGUI object\n

        Returns:\n
        None\n

        """

        os.system("title " + "Kudasai Console")

        self.text_color = "#FFFFFF"
        self.primary_color = "#000000"
        self.secondary_color = "#202020"

        self.main_window = tk.Tk()
        self.main_window.title("Kudasai GUI")
        self.main_window.configure(bg="#202020")
        self.main_window.geometry("1200x600")
        self.main_window.resizable(False, False) ## Prevents resizing of window

        self.main_window.protocol("WM_DELETE_WINDOW", self.on_main_window_close) ## causes all windows to close when the main window is closed

        if(os.name == 'nt'):  ## Windows
            self.config_dir = os.path.join(os.environ['USERPROFILE'],"KudasaiConfig")
        else:  ## Linux
            self.config_dir = os.path.join(os.path.expanduser("~"), "KudasaiConfig")

        self.script_dir = os.path.dirname(os.path.abspath(__file__))

        self.output_dir = os.path.join(self.script_dir, "KudasaiOutput")

        self.replacement_json_files = []
        self.replacement_json_paths = []

        self.translation_model_files = []
        self.translation_model_paths = []

        self.replacement_json_files, self.replacement_json_paths = self.get_json_options() 
        self.translation_model_files, self.translation_model_paths = self.get_translation_mode_options() 

        self.unpreprocessed_text_path = os.path.join(self.config_dir,"unpreprocessed_text.txt")
        self.gui_temp_translation_log_path = os.path.join(self.config_dir,"guiTempTranslationLog.txt")

        self.gui_temp_kaiseki_path = os.path.join(self.config_dir,"guiTempKaiseki.txt")
        self.gui_temp_kijiku_path = os.path.join(self.config_dir,"guiTempKijiku.txt")
        self.is_there_update_path = os.path.join(self.config_dir, "isThereUpdate.txt")

        self.kudasai_results_path = os.path.join(os.path.join(self.script_dir,"KudasaiOutput"), "output.txt")
        self.translated_text_path = os.path.join(os.path.join(self.script_dir,"KudasaiOutput"), "translatedText.txt")
        self.preprocessed_text_path = os.path.join(os.path.join(self.script_dir,"KudasaiOutput"), "preprocessedText.txt")

        ## preprocessing and translating clients are set to None before they are initialized
        self.kudasai_client = None
        self.kaiseki_client = None
        self.kijiku_client = None

        if(not os.path.exists(self.output_dir)):
            os.mkdir(self.output_dir)

        check_update(True)

        with open(self.is_there_update_path, 'r', encoding='utf-8') as file:
            if(file.read() == "true"):
                self.create_update_alert_window()

        self.create_secondary_window()

        self.create_text_entry()

        self.create_frames()

        self.create_preprocess_button()
        self.create_json_option_menu()

        self.create_copy_button()
        self.create_translate_button()

        self.create_translation_mode_menu()

        self.create_main_output_label()

##-------------------start-of-reset_preprocessing_files()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def reset_preprocessing_files(self) -> None:

        """

        Resets the preprocessing files\n

        Parameters:\n
        self (object - KudasaiGUI) : The KudasaiGUI object\n

        Returns:\n
        None\n

        """

        files_to_truncate = [
            self.kudasai_results_path,
            self.preprocessed_text_path
        ]

        for file_path in files_to_truncate: ## Creates files if they don't exist, truncates them if they do
            with open(file_path, 'w+') as file:
                file.truncate(0)

##-------------------start-of-reset_preprocessing_files()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def reset_translation_files(self) -> None:

        """

        Resets the translation files\n

        Parameters:\n
        self (object - KudasaiGUI) : The KudasaiGUI object\n

        Returns:\n
        None\n

        """

        files_to_truncate = [
            self.translated_text_path,
        ]

        for file_path in files_to_truncate: ## Creates files if they don't exist, truncates them if they do
            with open(file_path, 'w+') as file:
                file.truncate(0)

##-------------------start-of-reset_preprocessing_files()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def reset_temp_files(self) -> None:

        """

        Resets the standard temp files\n

        Parameters:\n
        self (object - KudasaiGUI) : The KudasaiGUI object\n

        Returns:\n
        None\n

        """

        files_to_truncate = [
            self.unpreprocessed_text_path,
            self.gui_temp_translation_log_path,
            self.gui_temp_kaiseki_path,
            self.gui_temp_kijiku_path,
        ]

        for file_path in files_to_truncate: ## Creates files if they don't exist, truncates them if they do
            with open(file_path, 'w+') as file:
                file.truncate(0)

##-------------------start-of-create_secondary_window()-----------------------------------------------------------------------------------------------------------------------------------------------------

    def create_secondary_window(self) -> None:

        """

        Creates the secondary window\n

        Parameters:\n
        self (object - KudasaiGUI) : The KudasaiGUI object\n

        Returns:\n
        None\n

        """

        self.secondary_window = tk.Tk()
        self.secondary_window.title("Results")
        self.secondary_window.configure(bg="#202020")
        self.secondary_window.geometry("300x600")
        self.secondary_window.resizable(False, False) ## Prevents resizing of window

        self.secondary_window.withdraw() ## Hides the window

        self.create_results_output_label()

##-------------------start-of-create_update_alert_window()()-----------------------------------------------------------------------------------------------------------------------------------------------------

    def create_update_alert_window(self) -> None:

        """

        Creates the update alert window\n

        Parameters:\n
        self (object - KudasaiGUI) : The KudasaiGUI object\n

        Returns:\n
        None\n

        """

        self.update_alert_window = tk.Tk()
        self.update_alert_window.title("Please Update Kudasai")
        self.update_alert_window.configure(bg="#202020")
        self.update_alert_window.geometry("300x600")
        self.update_alert_window.resizable(False, False) ## Prevents resizing of window

        self.create_update_alert_output_label()

        self.update_alert_output_label.insert(tk.END, "There is a new update for Kudasai\nIt is recommended that you use the latest version of Kudasai\nYou can download it at https://github.com/Seinuve/Kudasai/releases/latest \n") ## Display the preprocessed text

        self.update_alert_window.lift()

##-------------------start-of-create_text_entry()-----------------------------------------------------------------------------------------------------------------------------------------------------------

    def create_text_entry(self) -> None:

        """

        Creates the text entry box\n

        Parameters:\n
        self (object - KudasaiGUI) : The KudasaiGUI object\n

        Returns:\n
        None\n

        """

        self.text_entry = tk.Text(self.main_window, bg=self.primary_color, fg=self.text_color, height=18, width=600)
        self.text_entry.pack(side=tk.TOP)

##-------------------start-of-create_main_output_label()----------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    def create_main_output_label(self) -> None:

        """

        Creates the output label\n

        Parameters:\n
        self (object - KudasaiGUI) : The KudasaiGUI object\n

        Returns:\n
        None\n

        """

        self.main_output_label = scrolledtext.ScrolledText(self.main_window, bg=self.primary_color, fg=self.text_color, height=18, width=600)
        self.main_output_label.pack(side=tk.BOTTOM)

##-------------------start-of-create_results_output_label()-------------------------------------------------------------------------------------------------------------------------------------------

    def create_results_output_label(self) -> None:

        """

        Creates the output label\n

        Parameters:\n
        self (object - KudasaiGUI) : The KudasaiGUI object\n

        Returns:\n
        None\n

        """

        self.secondary_output_label = scrolledtext.ScrolledText(self.secondary_window, bg=self.primary_color, fg=self.text_color, height=39, width=300)
        self.secondary_output_label.pack(side=tk.BOTTOM)

##-------------------start-of-create_update_alert_output_label()-------------------------------------------------------------------------------------------------------------------------------------------

    def create_update_alert_output_label(self) -> None:

        self.update_alert_output_label = scrolledtext.ScrolledText(self.update_alert_window, bg=self.primary_color, fg=self.text_color, height=39, width=300)
        self.update_alert_output_label.pack(side=tk.BOTTOM)

##-------------------start-of-create_frames()---------------------------------------------------------------------------------------------------------------------------------------------------------------

    def create_frames(self) -> None:

        """

        Creates the frames\n

        Parameters:\n
        self (object - KudasaiGUI) : The KudasaiGUI object\n

        Returns:\n
        None\n

        """

        self.top_button_frame = tk.Frame(self.main_window, bg=self.primary_color) ## Frame for the top buttons
        self.top_button_frame.pack()

        self.middle_button_frame = tk.Frame(self.main_window, bg=self.primary_color) ## Frame for the middle buttons
        self.middle_button_frame.pack()

        self.bottom_button_frame = tk.Frame(self.main_window, bg=self.primary_color) ## Frame for the bottom buttons
        self.bottom_button_frame.pack()

##-------------------start-of-create_preprocess_button()---------------------------------------------------------------------------------------------------------------------------------------------------

    def create_preprocess_button(self) -> None:

        """

        Creates the preprocess button\n

        Parameters:\n
        self (object - KudasaiGUI) : The KudasaiGUI object\n

        Returns:\n
        None\n

        """

        preprocess_button = tk.Button(self.top_button_frame, text="Preprocess", bg=self.primary_color, fg=self.text_color, command=self.preprocess)
        preprocess_button.pack(side=tk.LEFT)

##-------------------start-of-create_translate_button()-----------------------------------------------------------------------------------------------------------------------------------------------------

    def create_translate_button(self) -> None:

        """

        Creates the translate button\n

        Parameters:\n
        self (object - KudasaiGUI) : The KudasaiGUI object\n

        Returns:\n
        None\n

        """

        translate_button = tk.Button(self.bottom_button_frame, text="Translate", bg=self.primary_color, fg=self.text_color, command=self.translate)
        translate_button.pack(side=tk.LEFT)

##-------------------start-of-create_copy_button()--------------------------------------------------------------------------------------------------------------------------------------------------------

    def create_copy_button(self) -> None:

        """

        Creates the copy button\n

        Parameters:\n
        self (object - KudasaiGUI) : The KudasaiGUI object\n

        Returns:\n
        None\n

        """

        copy_button = tk.Button(self.middle_button_frame, text="Copy Output", bg=self.primary_color, fg=self.text_color, command=self.copy_output)
        copy_button.pack(side=tk.RIGHT)

##-------------------start-of-create_json_option_menu()---------------------------------------------------------------------------------------------------------------------------------------------------

    def create_json_option_menu(self) -> None:

        """

        Creates the json option menu\n

        Parameters:\n
        self (object - KudasaiGUI) : The KudasaiGUI object\n

        Returns:\n
        None\n

        """

        options = self.replacement_json_files
        self.selected_json_option = tk.StringVar()  
        self.selected_json_option.set(options[0])  ## Set default value

        json_option_menu = tk.OptionMenu(self.top_button_frame, self.selected_json_option, *options)
        json_option_menu.configure(bg=self.primary_color, fg=self.text_color, highlightbackground=self.primary_color, activebackground=self.primary_color, menu=json_option_menu['menu'])  # Set colors

        menu = json_option_menu['menu'] 
        menu.configure(bg=self.primary_color, fg=self.text_color) ## Set colors

        json_option_menu.pack(side=tk.LEFT)

##-------------------start-of-create_translation_mode_menu()---------------------------------------------------------------------------------------------------------------------------------------------------

    def create_translation_mode_menu(self) -> None:

        """

        Creates the translation mode menu\n

        Parameters:\n
        self (object - KudasaiGUI) : The KudasaiGUI object\n

        Returns:\n
        None\n

        """

        options = self.translation_model_files
        self.selected_translation_mode = tk.StringVar()   
        self.selected_translation_mode.set(options[0])  ## Set default value

        translation_mode_menu = tk.OptionMenu(self.bottom_button_frame, self.selected_translation_mode, *options)
        translation_mode_menu.configure(bg=self.primary_color, fg=self.text_color, highlightbackground=self.primary_color, activebackground=self.primary_color, menu=translation_mode_menu['menu'])

        menu = translation_mode_menu['menu']
        menu.configure(bg=self.primary_color, fg=self.text_color) ## Set colors

        translation_mode_menu.pack(side=tk.RIGHT)

##-------------------start-of-get_json_options()-----------------------------------------------------------------------------------------------------------------------------------------------------------

    def get_json_options(self) -> tuple[typing.List[str], typing.List[str]]:

        """

        Gets the json options from the Replacements folder\n

        Parameters:\n
        self (object - KudasaiGUI) : The KudasaiGUI object\n

        Returns:\n
        replacement_json_files (list): List of json files\n
        replacement_json_paths (list): List of json file paths\n

        """

        json_folder = os.path.join(self.script_dir,"Replacements")

        replacement_json_files = []
        replacement_json_paths = []

        for file_name in os.listdir(json_folder):

            if(file_name.endswith(".json")): ## If the file is a json file, add it to the options
                file_path = os.path.join(json_folder, file_name)
                replacement_json_files.append(file_name)
                replacement_json_paths.append(file_path)

        return replacement_json_files, replacement_json_paths
    
##-------------------start-of-get_translation_mode_options()------------------------------------------------------------------------------------------------------------------------------------------------

    def get_translation_mode_options(self) -> tuple[typing.List[str], typing.List[str]]:

        """

        Gets the translation mode options from the Models folder\n

        Parameters:\n
        self (object - KudasaiGUI) : The KudasaiGUI object\n

        Returns:\n
        translation_model_files (list): List of model files\n
        translation_model_paths (list): List of model file paths\n

        """

        model_folder = os.path.join(self.script_dir,"Models")

        translation_model_files = []
        translation_model_paths = []

        for file_name in os.listdir(model_folder):

            if(file_name.endswith(".py") and not file_name.startswith("__init__") and not file_name.startswith("Kansei")): ## If the file is a model file, add it to the options
                file_path = os.path.join(model_folder, file_name)
                file_name = file_name.replace(".py", "")
                translation_model_files.append(file_name)
                translation_model_paths.append(file_path)

        return translation_model_files, translation_model_paths
    
##-------------------start-of-preprocess()----------------------------------------------------------------------------------------------------------------------------------------------------------------

    def preprocess(self) -> None:

        """

        Preprocesses the text in the text entry box\n

        Parameters:\n
        self (object - KudasaiGUI) : The KudasaiGUI object\n

        Returns:\n
        None\n

        """

        self.reset_temp_files() # Reset the files
        self.reset_preprocessing_files

        unpreprocessed_text = self.text_entry.get("1.0", tk.END)

        with open(self.unpreprocessed_text_path, "w+", encoding="utf-8") as file: ## Write the text to a temporary file for Kudasai to read and preprocess
            file.write(unpreprocessed_text)

        if(self.kudasai_client is None): ## If the Kudasai object has not been created yet, create it (this is for the first time the user presses the preprocess button
            self.kudasai_client = Kudasai(from_gui=True) ## creates Kudasai object, passing if it is being run from the GUI or not
        
        self.kudasai_client.preprocess(self.unpreprocessed_text_path, self.replacement_json_paths[self.replacement_json_files.index(self.selected_json_option.get())]) ## Preprocess the text

        with open(self.preprocessed_text_path, "r+", encoding="utf-8") as file:
            preprocessed_text = file.read() ## Read the preprocessed text

        with open(self.kudasai_results_path, "r+", encoding="utf-8") as file:
            kudasai_results = file.read() ## Read the results

        self.main_output_label.delete("1.0", tk.END)
        self.main_output_label.insert(tk.END, preprocessed_text) ## Display the preprocessed text
        
        try: ## Try to display the results
            self.secondary_output_label.delete("1.0", tk.END)
            self.secondary_output_label.insert(tk.END, kudasai_results)

        except: ## if window is destroyed, create a new one
            self.create_secondary_window()
            self.secondary_output_label.insert(tk.END, kudasai_results)

        self.secondary_window.deiconify() ## Show the results window

        self.secondary_window.mainloop()

##-------------------start-of-translate()-----------------------------------------------------------------------------------------------------------------------------------------------------------------

    def translate(self) -> None:

        """

        Translates the text in the text entry box\n

        Parameters:\n
        self (object - KudasaiGUI) : The KudasaiGUI object\n

        Returns:\n
        None\n

        """            

        self.reset_temp_files() ## Reset the files
        self.reset_translation_files()

        if(self.selected_translation_mode.get() == "Kijiku"):
            self.handle_kijiku()
        
        elif(self.selected_translation_mode.get() == "Kaiseki"):
            self.handle_kaiseki()

##-------------------start-of-copy_output()-----------------------------------------------------------------------------------------------------------------------------------------------------------------

    def copy_output(self) -> None:

        """

        Copies the output to the clipboard\n

        Parameters:\n
        self (object - KudasaiGUI) : The KudasaiGUI object\n

        Returns:\n
        None\n

        """

        self.main_window.clipboard_clear()
        self.main_window.clipboard_append(self.main_output_label.get("1.0", "end-1c"))

##-------------------start-of-handle_kijiku()---------------------------------------------------------------------------------------------------------------------------------------------------------------

    def handle_kijiku(self) -> None:

        """

        Handles the gui's interaction with the Kijiku model\n

        Parameters:\n
        self (object - KudasaiGUI) : The KudasaiGUI object\n

        Returns:\n
        None\n

        """

        untranslated_text = self.text_entry.get("1.0", tk.END) ## Get the text from the text entry box

        with open(self.gui_temp_kijiku_path, "w+", encoding="utf-8") as file: ## Write the text to a temporary file for Kijiku to read and translate
            file.write(untranslated_text)

        if(self.kijiku_client is None): ## If the Kijiku object has not been created yet, create it (this is for the first time the user presses the translate button
            self.kijiku_client = Kijiku(self.config_dir,self.script_dir,from_gui=True) ## creates Kijiku object, passing the path to the config directory, the path to the script directory, and if it is being run from the GUI or not

        self.kijiku_client.translate(self.gui_temp_kijiku_path)

        with open(self.translated_text_path, "r+", encoding="utf-8") as file:
            translated_text = file.read() ## Read the translated text

        with open(self.gui_temp_translation_log_path, "r+", encoding="utf-8") as file: # Write the text to a temporary file
            kijiku_results = file.read() ## Read the results
                
        self.main_output_label.delete("1.0", tk.END)
        self.main_output_label.insert(tk.END, translated_text)

        try: ## Try to display the results
            self.secondary_output_label.delete("1.0", tk.END)
            self.secondary_output_label.insert(tk.END, kijiku_results)

        except: ## if window is destroyed, create a new one
            self.create_secondary_window()
            self.secondary_output_label.insert(tk.END, kijiku_results)

        self.secondary_window.deiconify() ## Show the results window
        self.secondary_window.mainloop()
        
##-------------------start-of-handle_kaiseki()--------------------------------------------------------------------------------------------------------------------------------------------------------------

    def handle_kaiseki(self) -> None:

        """

        Handles the gui's interaction with the Kaiseki model\n

        Parameters:\n
        self (object - KudasaiGUI) : The KudasaiGUI object\n

        Returns:\n
        None\n

        """

        untranslated_text = self.text_entry.get("1.0", tk.END) ## Get the text from the text entry box

        with open(self.gui_temp_kaiseki_path, "w+", encoding="utf-8") as file: ## Write the text to a temporary file for Kaiseki to read and translate
            file.write(untranslated_text)

        if(self.kaiseki_client is None): ## If the Kaiseki object has not been created yet, create it (this is for the first time the user presses the translate button
            self.kaiseki_client = Kaiseki(self.config_dir,self.script_dir,from_gui=True) ## creates Kaiseki object, passing the path to the config directory, the path to the script directory, and if it is being run from the GUI or not

        self.kaiseki_client.translate(self.gui_temp_kaiseki_path)

        with open(self.translated_text_path, "r+", encoding="utf-8") as file:
            translated_text = file.read() ## Read the translated text

        with open(self.gui_temp_translation_log_path, "r+", encoding="utf-8") as file: ## Write the text to a temporary file
            kaiseki_results = file.read()

        self.main_output_label.delete("1.0", tk.END)
        self.main_output_label.insert(tk.END, translated_text)

        try: ## Try to display the results
            self.secondary_output_label.delete("1.0", tk.END)
            self.secondary_output_label.insert(tk.END, kaiseki_results)

        except: ## if window is destroyed, create a new one
            self.create_secondary_window()
            self.secondary_output_label.insert(tk.END, kaiseki_results)

        self.secondary_window.deiconify() ## Show the results window
        self.secondary_window.mainloop()

##-------------------start-of-on_main_window_close()-------------------------------------------------------------------------------------------------------------------------------------------------------

    def on_main_window_close(self) -> None:

        """

        Handles what happens when the main window is closed\n

        Parameters:\n
        self (object - KudasaiGUI) : The KudasaiGUI object\n

        Returns:\n
        None\n

        """

        try:
            self.update_alert_window.destroy()
        except:
            pass

        try:
            self.secondary_window.destroy()
        except:
            pass
        
        try:
            self.main_window.destroy()
        except:
            pass

##-------------------start-of-run()------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def run(self) -> None:

        """

        Runs the GUI\n

        Parameters:\n
        self (object - KudasaiGUI) : The KudasaiGUI object\n

        Returns:\n
        None\n

        """

        self.main_window.mainloop()

##-------------------start-of-main()-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

if(__name__ == "__main__"):
    gui = KudasaiGUI()
    gui.run()
