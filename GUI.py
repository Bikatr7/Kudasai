import tkinter as tk
import os

import Kudasai

class KudasaiGUI:

#-------------------start-of-__init__()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self) -> None:

        self.mainWindow = tk.Tk()
        self.mainWindow.title("Kudasai GUI")
        self.mainWindow.configure(bg="#202020")
        self.mainWindow.geometry("1200x600")

        self.text_color = "#FFFFFF"
        self.primaryColor = "#000000"
        self.secondaryColor = "#202020"

        self.scriptDir = os.path.dirname(os.path.abspath(__file__))
        self.configDir = os.path.join(os.environ['USERPROFILE'],"KudasaiConfig")
        self.jsonFiles = []
        self.jsonPaths = []

        self.create_text_entry()
        self.create_preprocess_button()
        self.create_copy_button()

        self.create_output_label()

        self.jsonFiles, self.jsonPaths = self.get_json_options()

        self.create_json_option_menu(self.jsonFiles)

#-------------------start-of-get_json_options()-----------------------------------------------------------------------------------------------------------------------------------------------------------

    def get_json_options(self) -> tuple[list[str], list[str]]:

        """

        Gets the json options from the Replacements folder\n

        Parameters:\n
        None\n

        Returns:\n
        jsonFiles (list): List of json files\n
        jsonPaths (list): List of json file paths\n

        """

        jsonFolder = os.path.join(self.scriptDir,"Replacements")

        jsonFiles = []
        jsonPaths = []

        for fileName in os.listdir(jsonFolder):

            if(fileName.endswith(".json")):
                filePath = os.path.join(jsonFolder, fileName)
                jsonFiles.append(fileName)
                jsonPaths.append(filePath)

        return jsonFiles, jsonPaths

#-------------------start-of-create_text_entry()-----------------------------------------------------------------------------------------------------------------------------------------------------------

    def create_text_entry(self) -> None:

        """

        Creates the text entry box\n

        Parameters:\n
        None\n

        Returns:\n
        None\n

        """

        self.text_entry = tk.Text(self.mainWindow, bg=self.primaryColor, fg=self.text_color, height=18, width=600)
        self.text_entry.pack(side=tk.TOP)

#-------------------start-of-create_preprocess_button()---------------------------------------------------------------------------------------------------------------------------------------------------

    def create_preprocess_button(self) -> None:

        """

        Creates the preprocess button\n

        Parameters:\n
        None\n

        Returns:\n
        None\n

        """

        self.button_frame1 = tk.Frame(self.mainWindow, bg=self.primaryColor)
        self.button_frame1.pack()

        Preprocess = tk.Button(self.button_frame1, text="Preprocess", bg=self.primaryColor, fg=self.text_color, command=self.preprocess)
        Preprocess.pack(side=tk.LEFT)


#-------------------start-of-create_copy_button()--------------------------------------------------------------------------------------------------------------------------------------------------------

    def create_copy_button(self) -> None:

        """

        Creates the copy button\n

        Parameters:\n
        None\n

        Returns:\n
        None\n

        """

        button_frame2 = tk.Frame(self.mainWindow, bg=self.primaryColor)
        button_frame2.pack()

        copy_button = tk.Button(button_frame2, text="Copy Output", bg=self.primaryColor, fg=self.text_color, command=self.copy_output)
        copy_button.pack(side=tk.LEFT)

#-------------------start-of-create_json_option_menu()---------------------------------------------------------------------------------------------------------------------------------------------------

    def create_json_option_menu(self, jsonFiles:list[str]) -> None:

        """

        Creates the json option menu\n

        Parameters:\n
        jsonFiles (list - string): List of json files\n

        Returns:\n
        None\n

        """

        options = jsonFiles
        self.selected_option = tk.StringVar()  
        self.selected_option.set(options[0])  

        json_option_menu = tk.OptionMenu(self.button_frame1, self.selected_option, *options)
        json_option_menu.configure(bg=self.primaryColor, fg=self.text_color, highlightbackground=self.primaryColor, activebackground=self.primaryColor, menu=json_option_menu['menu'])  # Set colors

        # Configure the menu items' background and foreground color
        menu = json_option_menu['menu']
        menu.configure(bg=self.primaryColor, fg=self.text_color)

        json_option_menu.pack(side=tk.LEFT)

#-------------------start-of-create_output_label()----------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    def create_output_label(self) -> None:

        """

        Creates the output label\n

        Parameters:\n
        None\n

        Returns:\n
        None\n

        """

        self.label = tk.Label(self.mainWindow, bg=self.primaryColor, fg=self.text_color, height=18, width=600)
        self.label.pack(side=tk.BOTTOM)
        

#-------------------start-of-copy_output()-----------------------------------------------------------------------------------------------------------------------------------------------------------------

    def copy_output(self) -> None:

        """

        Copies the output to the clipboard\n

        Parameters:\n
        None\n

        Returns:\n
        None\n

        """

        self.mainWindow.clipboard_clear()
        self.mainWindow.clipboard_append(self.label.cget("text"))

#-------------------start-of-preprocess()----------------------------------------------------------------------------------------------------------------------------------------------------------------

    def preprocess(self) -> None:

        """

        Preprocesses the text in the text entry box\n

        Parameters:\n
        None\n

        Returns:\n
        None\n

        """

        text = self.text_entry.get("1.0", tk.END)

        with open(os.path.join(self.configDir,"guiTemp.txt"), "w+", encoding="utf-8") as file:
            file.write(text)

        Kudasai.main(os.path.join(self.configDir,"guiTemp.txt"), self.jsonPaths[self.jsonFiles.index(self.selected_option.get())],isGui=True)

        with open(os.path.join(self.scriptDir,"KudasaiOutput\\preprocessedText.txt"), "r+", encoding="utf-8") as file:
            text = file.read()

        self.label.config(text=text, justify=tk.LEFT, anchor=tk.NW)
        
#-------------------start-of-run()------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def run(self) -> None:

        """

        Runs the GUI\n

        Parameters:\n
        None\n

        Returns:\n
        None\n

        """

        self.mainWindow.mainloop()

#-------------------start-of-main()-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

if(__name__ == "__main__"):
    gui = KudasaiGUI()
    gui.run()
