## Built-in modules
import os
import tkinter as tk
import json
import typing

from tkinter import scrolledtext

## Custom modules
from modules.preloader import preloader

from models.Kaiseki import Kaiseki
from models.Kijiku import Kijiku
from models.Kairyou import Kairyou

##-------------------start-of-KudasaiGUI---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class KudasaiGUI:

    """

    The gui for Kudasai.\n

    """

##-------------------start-of-__init__()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self) -> None:

        """

        Initializes the KudasaiGUI class.\n

        Parameters:\n
        self (object - KudasaiGUI) : The KudasaiGUI object\n

        Returns:\n
        None.\n

        """

        os.system("title " + "Kudasai Console")

        self.preloader = preloader()

        self.kairyou_client = None
        self.kaiseki_client = None
        self.kijiku_client = None

        ##---------------------------------------------------------------------

        self.text_color = "#FFFFFF"
        self.primary_color = "#000000"
        self.secondary_color = "#202020"

        self.main_window = tk.Tk()
        self.main_window.title("Kudasai GUI")
        self.main_window.configure(bg="#202020")
        self.main_window.geometry("1200x600")
        self.main_window.resizable(False, False) ## Prevents resizing of window

        self.main_window.protocol("WM_DELETE_WINDOW", self.on_main_window_close) ## causes all windows to close when the main window is closed

        self.replacement_json_files = []
        self.replacement_json_paths = []

        self.translation_model_files = []
        self.translation_model_paths = []

        self.replacement_json_files, self.replacement_json_paths = self.get_json_options() 
        self.translation_model_files, self.translation_model_paths = self.get_translation_mode_options() 

        ##---------------------------------------------------------------------


        self.is_connection, update_prompt = self.preloader.toolkit.check_update()

        if(update_prompt != ""):
            self.create_update_alert_window(update_prompt)

        self.create_secondary_window()

        self.create_text_entry()

        self.create_frames()

        self.create_preprocess_button()
        self.create_json_option_menu()

        self.create_copy_button()
        self.create_translate_button()

        self.create_translation_mode_menu()

        self.create_main_output_label()

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

    def create_update_alert_window(self, update_prompt:str) -> None:

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

        self.update_alert_output_label.insert(tk.END, update_prompt)

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

        json_folder = os.path.join(self.preloader.file_handler.script_dir, "replacement jsons")

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

        model_folder = os.path.join(self.preloader.file_handler.script_dir, "models")

        translation_model_files = []
        translation_model_paths = []

        model_blacklist = ["Kansei", "__init__", "Kairyou"]

        for file_name in os.listdir(model_folder):

            if(file_name.endswith(".py") and not any(file_name.startswith(name) for name in model_blacklist)):
                file_path = os.path.join(model_folder, file_name)
                file_name = file_name.replace(".py", "")
                translation_model_files.append(file_name)
                translation_model_paths.append(file_path)

        return translation_model_files, translation_model_paths
    
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

##-------------------start-of-preprocess()----------------------------------------------------------------------------------------------------------------------------------------------------------------

    def preprocess(self) -> None:

        """

        Preprocesses the text in the text entry box\n

        Parameters:\n
        self (object - KudasaiGUI) : The KudasaiGUI object\n

        Returns:\n
        None\n

        """


        text_to_preprocess = self.text_entry.get("1.0", tk.END)

        try:

            with open(self.replacement_json_paths[self.replacement_json_files.index(self.selected_json_option.get())], 'r', encoding='utf-8') as file: 
                replacement_json = json.load(file) 
    
        except:

            self.main_output_label.delete("1.0", tk.END)
            self.main_output_label.insert(tk.END, "Error: Could not load replacement json file")
            return


        self.kairyou_client = Kairyou(replacement_json, text_to_preprocess, self.preloader)

        self.kairyou_client.preprocess()
        self.preloader.write_kairyou_results(self.kairyou_client)

        self.main_output_label.delete("1.0", tk.END)
        self.main_output_label.insert(tk.END, self.kairyou_client.text_to_preprocess) ## Display the preprocessed text
        
        try: ## Try to display the results
            self.secondary_output_label.delete("1.0", tk.END)
            self.secondary_output_label.insert(tk.END, self.kairyou_client.preprocessing_log)

        except: ## if window is destroyed, create a new one
            self.create_secondary_window()
            self.secondary_output_label.insert(tk.END, self.kairyou_client.preprocessing_log)

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

        try: ## Try to display the results
            self.secondary_output_label.delete("1.0", tk.END)

        except: ## if window is destroyed, create a new one
            pass

        if(self.selected_translation_mode.get() == "Kijiku"):
            self.handle_kijiku()
        
        elif(self.selected_translation_mode.get() == "Kaiseki"):
            self.handle_kaiseki()

##-------------------start-of-handle_kijiku()---------------------------------------------------------------------------------------------------------------------------------------------------------------

    def handle_kijiku(self) -> None:

        """

        Handles the gui's interaction with the Kijiku model\n

        Parameters:\n
        self (object - KudasaiGUI) : The KudasaiGUI object\n

        Returns:\n
        None\n

        """

        text_to_translate = self.text_entry.get("1.0", tk.END) ## Get the text from the text entry box

        self.kijiku_client = Kijiku(text_to_translate, self.preloader)

        self.kijiku_client.translate()
        self.preloader.write_kijiku_results(self.kijiku_client)
                
        self.main_output_label.delete("1.0", tk.END)
        self.main_output_label.insert(tk.END, ''.join(self.kijiku_client.translated_text))

        try: ## Try to display the results
            self.secondary_output_label.delete("1.0", tk.END)
            self.secondary_output_label.insert(tk.END, self.kijiku_client.translation_print_result)

        except: ## if window is destroyed, create a new one
            self.create_secondary_window()
            self.secondary_output_label.insert(tk.END, self.kijiku_client.translation_print_result)

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

        text_to_translate = self.text_entry.get("1.0", tk.END) ## Get the text from the text entry box

        self.kaiseki_client = Kaiseki(text_to_translate, self.preloader)

        self.kaiseki_client.translate()
        self.preloader.write_kaiseki_results(self.kaiseki_client)

        self.main_output_label.delete("1.0", tk.END)
        self.main_output_label.insert(tk.END, ''.join(self.kaiseki_client.translated_text))

        try: ## Try to display the results
            self.secondary_output_label.delete("1.0", tk.END)
            self.secondary_output_label.insert(tk.END, self.kaiseki_client.translation_print_result)

        except: ## if window is destroyed, create a new one
            self.create_secondary_window()
            self.secondary_output_label.insert(tk.END, self.kaiseki_client.translation_print_result)

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
