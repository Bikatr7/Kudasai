import tkinter as tk
import os

import Kudasai

from typing import List
from tkinter import ttk
from time import sleep

from Models import Kijiku


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

        if(os.name == 'nt'):  # Windows
            self.configDir = os.path.join(os.environ['USERPROFILE'],"KudasaiConfig")
        else:  # Linux
            self.configDir = os.path.join(os.path.expanduser("~"), "KudasaiConfig")


        self.jsonFiles = []
        self.jsonPaths = []

        self.modelFiles = []
        self.modelPaths = []

        self.jsonFiles, self.jsonPaths = self.get_json_options()
        self.modelFiles, self.modelPaths = self.get_translation_mode_options()


        self.create_text_entry()

        self.create_frames()

        self.create_preprocess_button()
        self.create_json_option_menu(self.jsonFiles)

        self.create_copy_button()
        self.create_translate_button()

        self.create_translation_mode_menu(self.modelFiles)

        self.create_progress_bar()

        self.create_output_label()

#-------------------start-of-create_text_entry()-----------------------------------------------------------------------------------------------------------------------------------------------------------

    def create_text_entry(self) -> None:

        """

        Creates the text entry box\n

        Parameters:\n
        None\n

        Returns:\n
        None\n

        """

        self.textEntry = tk.Text(self.mainWindow, bg=self.primaryColor, fg=self.text_color, height=18, width=600)
        self.textEntry.pack(side=tk.TOP)

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
#-------------------start-of-create_frames()---------------------------------------------------------------------------------------------------------------------------------------------------------------

    def create_frames(self) -> None:

        self.topButtonFrame = tk.Frame(self.mainWindow, bg=self.primaryColor)
        self.topButtonFrame.pack()

        self.middleButtonFrame = tk.Frame(self.mainWindow, bg=self.primaryColor)
        self.middleButtonFrame.pack()

        self.bottomButtonFrame = tk.Frame(self.mainWindow, bg=self.primaryColor)
        self.bottomButtonFrame.pack()

        self.progressBarFrame = tk.Frame(self.mainWindow, bg=self.primaryColor)
        self.progressBarFrame.pack()

#-------------------start-of-create_preprocess_button()---------------------------------------------------------------------------------------------------------------------------------------------------

    def create_preprocess_button(self) -> None:

        """

        Creates the preprocess button\n

        Parameters:\n
        None\n

        Returns:\n
        None\n

        """

        preprocessButton = tk.Button(self.topButtonFrame, text="Preprocess", bg=self.primaryColor, fg=self.text_color, command=self.preprocess)
        preprocessButton.pack(side=tk.LEFT)

#-------------------start-of-create_translate_button()-----------------------------------------------------------------------------------------------------------------------------------------------------

    def create_translate_button(self) -> None:

        """

        Creates the translate button\n

        Parameters:\n
        None\n

        Returns:\n
        None\n

        """

        translateButton = tk.Button(self.bottomButtonFrame, text="Translate", bg=self.primaryColor, fg=self.text_color, command=self.translate)
        translateButton.pack(side=tk.LEFT)

#-------------------start-of-create_copy_button()--------------------------------------------------------------------------------------------------------------------------------------------------------

    def create_copy_button(self) -> None:

        """

        Creates the copy button\n

        Parameters:\n
        None\n

        Returns:\n
        None\n

        """

        copyButton = tk.Button(self.middleButtonFrame, text="Copy Output", bg=self.primaryColor, fg=self.text_color, command=self.copy_output)
        copyButton.pack(side=tk.RIGHT)

#-------------------start-of-create_json_option_menu()---------------------------------------------------------------------------------------------------------------------------------------------------

    def create_json_option_menu(self, jsonFiles:List[str]) -> None:

        """

        Creates the json option menu\n

        Parameters:\n
        jsonFiles (list - string): List of json files\n

        Returns:\n
        None\n

        """

        options = jsonFiles
        self.selectedJsonMode = tk.StringVar()  
        self.selectedJsonMode.set(options[0])  

        jsonOptionMenu = tk.OptionMenu(self.topButtonFrame, self.selectedJsonMode, *options)
        jsonOptionMenu.configure(bg=self.primaryColor, fg=self.text_color, highlightbackground=self.primaryColor, activebackground=self.primaryColor, menu=jsonOptionMenu['menu'])  # Set colors

        menu = jsonOptionMenu['menu']
        menu.configure(bg=self.primaryColor, fg=self.text_color)

        jsonOptionMenu.pack(side=tk.LEFT)

#-------------------start-of-create_translation_mode_menu()---------------------------------------------------------------------------------------------------------------------------------------------------

    def create_translation_mode_menu(self, translationModes:List[str]) -> None:

        """

        Creates the translation mode menu\n

        Parameters:\n
        translationModes (list - string): List of translation modes\n

        Returns:\n
        None\n

        """

        options = translationModes
        self.selectedTranslationMode = tk.StringVar()  
        self.selectedTranslationMode.set(options[0])  

        translationModeMenu = tk.OptionMenu(self.bottomButtonFrame, self.selectedTranslationMode, *options)
        translationModeMenu.configure(bg=self.primaryColor, fg=self.text_color, highlightbackground=self.primaryColor, activebackground=self.primaryColor, menu=translationModeMenu['menu'])

        # Configure the menu items' background and foreground color

        menu = translationModeMenu['menu']
        menu.configure(bg=self.primaryColor, fg=self.text_color)

        translationModeMenu.pack(side=tk.RIGHT)

#-------------------start-of-create_progress_bar()--------------------------------------------------------------------------------------------------------------------------------------------------------
        
    def create_progress_bar(self) -> None:

        """

        Creates the progress bar\n

        Parameters:\n
        None\n

        Returns:\n
        None\n

        """

        style = ttk.Style()
        style.theme_use('clam')  # Set a theme to avoid layout errors
        
        style.layout(
            "Custom.Horizontal.TProgressbar",
            [
                ("Horizontal.Progressbar.trough",
                {"children": [("Horizontal.Progressbar.pbar",
                                {"side": "left", "sticky": "ns"})],
                "sticky": "nswe"})
            ]
        )
        
        style.configure(
            "Custom.Horizontal.TProgressbar",
            background=self.secondaryColor,
            troughcolor=self.primaryColor
        )

        
        self.progress = ttk.Progressbar(
            self.progressBarFrame,
            orient=tk.HORIZONTAL,
            length=200,
            mode='determinate',
            style="Custom.Horizontal.TProgressbar"
        )
        self.progress.pack(side=tk.RIGHT)
        
#-------------------start-of-get_json_options()-----------------------------------------------------------------------------------------------------------------------------------------------------------

    def get_json_options(self) -> tuple[List[str], List[str]]:

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
    
#-------------------start-of-get_translation_mode_options()------------------------------------------------------------------------------------------------------------------------------------------------

    def get_translation_mode_options(self) -> tuple[List[str], List[str]]:

        """

        Gets the translation mode options from the Models folder\n

        Parameters:\n
        None\n

        Returns:\n
        modelFiles (list): List of model files\n

        """

        modelFolder = os.path.join(self.scriptDir,"Models")

        modelFiles = []
        modelPaths = []

        for fileName in os.listdir(modelFolder):

            if(fileName.endswith(".py") and not fileName.startswith("__init__")):
                filePath = os.path.join(modelFolder, fileName)
                modelFiles.append(fileName)
                modelPaths.append(filePath)

        return modelFiles, modelPaths
#-------------------start-of-preprocess()----------------------------------------------------------------------------------------------------------------------------------------------------------------

    def preprocess(self) -> None:

        """

        Preprocesses the text in the text entry box\n

        Parameters:\n
        None\n

        Returns:\n
        None\n

        """

        text = self.textEntry.get("1.0", tk.END)

        with open(os.path.join(self.configDir,"guiTempPreprocess.txt"), "w+", encoding="utf-8") as file:
            file.write(text)

        Kudasai.main(os.path.join(self.configDir,"guiTempPreprocess.txt"), self.jsonPaths[self.jsonFiles.index(self.selectedJsonMode.get())],isGui=True)

        with open(os.path.join(os.path.join(self.scriptDir,"KudasaiOutput"), "preprocessedText.txt"), "r+", encoding="utf-8") as file:
            text = file.read()

        self.label.config(text=text, justify=tk.LEFT, anchor=tk.NW)

#-------------------start-of-translate()-----------------------------------------------------------------------------------------------------------------------------------------------------------------

    def translate(self) -> None:

        """

        Translates the text in the text entry box\n

        Parameters:\n
        None\n

        Returns:\n
        None\n

        """            

        text = self.textEntry.get("1.0", tk.END)
        

        with open(os.path.join(self.configDir,"guiTempKijiku.txt"), "w+", encoding="utf-8") as file:
            file.writelines(text)

        text,_ = Kijiku.initialize_text(os.path.join(self.configDir,"guiTempKijiku.txt"),self.configDir)

        Kijiku.commence_translation(text,self.scriptDir,self.configDir,fromGui=True)

        with open(os.path.join(os.path.join(self.scriptDir,"KudasaiOutput"), "translatedText.txt"), "r+", encoding="utf-8") as file:
            text = file.read()
        
        self.label.config(text=text, justify=tk.LEFT, anchor=tk.NW)

        """
        self.progress['maximum'] = 100
        for i in range(101):
            self.progress['value'] = i
            self.progress.update()

            time.sleep(0.05)
        """

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
