import os
import tkinter as tk

import Kudasai

from typing import List
from tkinter import scrolledtext

from Models import Kijiku, Kaiseki


class KudasaiGUI:

#-------------------start-of-__init__()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self) -> None:

        os.system("title " + "Kudasai Console")

        self.text_color = "#FFFFFF"
        self.primaryColor = "#000000"
        self.secondaryColor = "#202020"

        self.mainWindow = tk.Tk()
        self.mainWindow.title("Kudasai GUI")
        self.mainWindow.configure(bg="#202020")
        self.mainWindow.geometry("1200x600")
        self.mainWindow.resizable(False, False) # Prevents resizing of window

        self.mainWindow.protocol("WM_DELETE_WINDOW", self.on_main_window_close) # Calls on_main_window_close() when the main window is closed

        if(os.name == 'nt'):  # Windows
            self.configDir = os.path.join(os.environ['USERPROFILE'],"KudasaiConfig")
        else:  # Linux
            self.configDir = os.path.join(os.path.expanduser("~"), "KudasaiConfig")

        self.scriptDir = os.path.dirname(os.path.abspath(__file__))

        self.jsonFiles = []
        self.jsonPaths = []

        self.modelFiles = []
        self.modelPaths = []

        self.jsonFiles, self.jsonPaths = self.get_json_options() # Get options for preprocessing mode
        self.modelFiles, self.modelPaths = self.get_translation_mode_options() # Get options for translation mode

        self.unpreprocessedTextPath = os.path.join(self.configDir,"unpreprocessedText.txt")
        self.guiTempTranslationLogPath = os.path.join(self.configDir,"guiTempTranslationLog.txt")

        self.guiTempKaisekiPath = os.path.join(self.configDir,"guiTempKaiseki.txt")
        self.guiTempKijikuPath = os.path.join(self.configDir,"guiTempKijiku.txt")

        self.kudasaiResultsPath = os.path.join(os.path.join(self.scriptDir,"KudasaiOutput"), "output.txt")
        self.translatedTextPath = os.path.join(os.path.join(self.scriptDir,"KudasaiOutput"), "translatedText.txt")
        self.preprocessedTextPath = os.path.join(os.path.join(self.scriptDir,"KudasaiOutput"), "preprocessedText.txt")

        self.create_secondary_window()

        self.create_text_entry()

        self.create_frames()

        self.create_preprocess_button()
        self.create_json_option_menu()

        self.create_copy_button()
        self.create_translate_button()

        self.create_translation_mode_menu()

        self.create_main_output_label()

#-------------------start-of-reset_preprocessing_files()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def reset_preprocessing_files(self) -> None:

        """

        Resets the files\n

        Parameters:\n
        None\n

        Returns:\n
        None\n

        """
        outputDir = os.path.join(self.scriptDir, "KudasaiOutput")
        if(not os.path.exists(outputDir)):
            os.mkdir(outputDir)

        filesToTruncate = [
            self.kudasaiResultsPath,
            self.preprocessedTextPath
        ]

        for filePath in filesToTruncate: # Creates files if they don't exist, truncates them if they do
            with open(filePath, 'w+') as file:
                file.truncate(0)

#-------------------start-of-reset_preprocessing_files()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def reset_translation_files(self) -> None:

        """

        Resets the files\n

        Parameters:\n
        None\n

        Returns:\n
        None\n

        """
        outputDir = os.path.join(self.scriptDir, "KudasaiOutput")
        if(not os.path.exists(outputDir)):
            os.mkdir(outputDir)

        filesToTruncate = [
            self.translatedTextPath,
        ]

        for filePath in filesToTruncate: # Creates files if they don't exist, truncates them if they do
            with open(filePath, 'w+') as file:
                file.truncate(0)

#-------------------start-of-reset_preprocessing_files()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def reset_temp_files(self) -> None:

        """

        Resets the files\n

        Parameters:\n
        None\n

        Returns:\n
        None\n

        """
        outputDir = os.path.join(self.scriptDir, "KudasaiOutput")
        if(not os.path.exists(outputDir)):
            os.mkdir(outputDir)

        filesToTruncate = [
            self.unpreprocessedTextPath,
            self.guiTempTranslationLogPath,
            self.guiTempKaisekiPath,
            self.guiTempKijikuPath,
        ]

        for filePath in filesToTruncate: # Creates files if they don't exist, truncates them if they do
            with open(filePath, 'w+') as file:
                file.truncate(0)

#-------------------start-of-create_secondary_window()-----------------------------------------------------------------------------------------------------------------------------------------------------

    def create_secondary_window(self) -> None:

        """

        Creates the secondary window\n

        Parameters:\n
        None\n

        Returns:\n
        None\n

        """

        self.secondaryWindow = tk.Tk()
        self.secondaryWindow.title("Results")
        self.secondaryWindow.configure(bg="#202020")
        self.secondaryWindow.geometry("300x600")
        self.secondaryWindow.resizable(False, False) # Prevents resizing of window

        self.secondaryWindow.withdraw() # Hides the window

        self.create_results_output_label()

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

#-------------------start-of-create_main_output_label()----------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    def create_main_output_label(self) -> None:

        """

        Creates the output label\n

        Parameters:\n
        None\n

        Returns:\n
        None\n

        """

        self.mainOutputLabel = scrolledtext.ScrolledText(self.mainWindow, bg=self.primaryColor, fg=self.text_color, height=18, width=600)
        self.mainOutputLabel.pack(side=tk.BOTTOM)

#-------------------start-of-create_results_output_label()-------------------------------------------------------------------------------------------------------------------------------------------

    def create_results_output_label(self) -> None:

        """

        Creates the output label\n

        Parameters:\n
        None\n

        Returns:\n
        None\n

        """

        self.secondaryOutputLabel = scrolledtext.ScrolledText(self.secondaryWindow, bg=self.primaryColor, fg=self.text_color, height=39, width=300)
        self.secondaryOutputLabel.pack(side=tk.BOTTOM)

#-------------------start-of-create_frames()---------------------------------------------------------------------------------------------------------------------------------------------------------------

    def create_frames(self) -> None:

        """

        Creates the frames\n

        Parameters:\n
        None\n

        Returns:\n
        None\n

        """

        self.topButtonFrame = tk.Frame(self.mainWindow, bg=self.primaryColor) # Frame for the top buttons
        self.topButtonFrame.pack()

        self.middleButtonFrame = tk.Frame(self.mainWindow, bg=self.primaryColor) # Frame for the middle buttons
        self.middleButtonFrame.pack()

        self.bottomButtonFrame = tk.Frame(self.mainWindow, bg=self.primaryColor) # Frame for the bottom buttons
        self.bottomButtonFrame.pack()

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

    def create_json_option_menu(self) -> None:

        """

        Creates the json option menu\n

        Parameters:\n
        jsonFiles (list - string): List of json files\n

        Returns:\n
        None\n

        """

        options = self.jsonFiles
        self.selectedJsonMode = tk.StringVar()  
        self.selectedJsonMode.set(options[0])  # Set default value

        jsonOptionMenu = tk.OptionMenu(self.topButtonFrame, self.selectedJsonMode, *options)
        jsonOptionMenu.configure(bg=self.primaryColor, fg=self.text_color, highlightbackground=self.primaryColor, activebackground=self.primaryColor, menu=jsonOptionMenu['menu'])  # Set colors

        menu = jsonOptionMenu['menu'] 
        menu.configure(bg=self.primaryColor, fg=self.text_color) # Set colors

        jsonOptionMenu.pack(side=tk.LEFT)

#-------------------start-of-create_translation_mode_menu()---------------------------------------------------------------------------------------------------------------------------------------------------

    def create_translation_mode_menu(self) -> None:

        """

        Creates the translation mode menu\n

        Parameters:\n
        translationModes (list - string): List of translation modes\n

        Returns:\n
        None\n

        """

        options = self.modelFiles
        self.selectedTranslationMode = tk.StringVar()   
        self.selectedTranslationMode.set(options[0])  # Set default value

        translationModeMenu = tk.OptionMenu(self.bottomButtonFrame, self.selectedTranslationMode, *options)
        translationModeMenu.configure(bg=self.primaryColor, fg=self.text_color, highlightbackground=self.primaryColor, activebackground=self.primaryColor, menu=translationModeMenu['menu'])

        menu = translationModeMenu['menu']
        menu.configure(bg=self.primaryColor, fg=self.text_color) # Set colors

        translationModeMenu.pack(side=tk.RIGHT)

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

            if(fileName.endswith(".json")): # If the file is a json file, add it to the options
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

            if(fileName.endswith(".py") and not fileName.startswith("__init__")): # If the file is a model file, add it to the options
                filePath = os.path.join(modelFolder, fileName)
                fileName = fileName.replace(".py", "")
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

        self.reset_temp_files() # Reset the files
        self.reset_preprocessing_files

        unpreprocessedText = self.textEntry.get("1.0", tk.END)

        with open(self.unpreprocessedTextPath, "w+", encoding="utf-8") as file: # Write the text to a temporary file for Kudasai to read and preprocess
            file.write(unpreprocessedText)

        Kudasai.main(self.unpreprocessedTextPath, self.jsonPaths[self.jsonFiles.index(self.selectedJsonMode.get())],isGui=True) # Preprocess the text

        with open(self.preprocessedTextPath, "r+", encoding="utf-8") as file:
            preprocessedText = file.read() # Read the preprocessed text

        with open(self.kudasaiResultsPath, "r+", encoding="utf-8") as file:
            kudasaiResults = file.read() # Read the results

        self.mainOutputLabel.delete("1.0", tk.END)
        self.mainOutputLabel.insert(tk.END, preprocessedText) # Display the preprocessed text
        
        try: # Try to display the results
            self.secondaryOutputLabel.delete("1.0", tk.END)
            self.secondaryOutputLabel.insert(tk.END, kudasaiResults)


        except: # if window is destroyed, create a new one
            self.create_secondary_window()
            self.secondaryOutputLabel.insert(tk.END, kudasaiResults)

        self.secondaryWindow.deiconify() # Show the results window

        self.secondaryWindow.mainloop()

#-------------------start-of-translate()-----------------------------------------------------------------------------------------------------------------------------------------------------------------

    def translate(self) -> None:

        """

        Translates the text in the text entry box\n

        Parameters:\n
        None\n

        Returns:\n
        None\n

        """            

        self.reset_temp_files() # Reset the files
        self.reset_translation_files()

        if(self.selectedTranslationMode.get() == "Kijiku"):
            self.handle_kijiku()
        
        elif(self.selectedTranslationMode.get() == "Kaiseki"):
            self.handle_kaiseki()

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
        self.mainWindow.clipboard_append(self.mainOutputLabel.get("1.0", "end-1c"))

#-------------------start-of-handle_kijiku()---------------------------------------------------------------------------------------------------------------------------------------------------------------

    def handle_kijiku(self) -> None:

        """

        Handles the gui's interaction with the Kijiku model\n

        Parameters:\n
        None\n

        Returns:\n
        None\n

        """

        untranslatedText = self.textEntry.get("1.0", tk.END) # Get the text from the text entry box

        with open(self.guiTempKijikuPath, "w+", encoding="utf-8") as file: # Write the text to a temporary file for Kijiku to read and translate
            file.write(untranslatedText)

        untranslatedText,_ = Kijiku.initialize_text(self.guiTempKijikuPath,self.configDir) # Initialize the text into a list of lines, and ensure the config dictionary is up to date
        
        Kijiku.commence_translation(untranslatedText,self.scriptDir,self.configDir,isGui=True) # Translate the text

        with open(self.translatedTextPath, "r+", encoding="utf-8") as file:
            translatedText = file.read() # Read the translated text

        with open(self.guiTempTranslationLogPath, "r+", encoding="utf-8") as file: # Write the text to a temporary file
            kijikuResults = file.read() # Read the results
                
        self.mainOutputLabel.delete("1.0", tk.END)
        self.mainOutputLabel.insert(tk.END, translatedText)

        try: # Try to display the results
            self.secondaryOutputLabel.delete("1.0", tk.END)
            self.secondaryOutputLabel.insert(tk.END, kijikuResults)

        except: # if window is destroyed, create a new one
            self.create_secondary_window()
            self.secondaryOutputLabel.insert(tk.END, kijikuResults)

        self.secondaryWindow.deiconify() # Show the results window
        self.secondaryWindow.mainloop()
        
#-------------------start-of-handle_kaiseki()--------------------------------------------------------------------------------------------------------------------------------------------------------------

    def handle_kaiseki(self) -> None:

        """

        Handles the gui's interaction with the Kaiseki model\n

        Parameters:\n
        None\n

        Returns:\n
        None\n

        """

        untranslatedText = self.textEntry.get("1.0", tk.END) # Get the text from the text entry box

        with open(self.guiTempKaisekiPath, "w+", encoding="utf-8") as file: # Write the text to a temporary file for Kaiseki to read and translate
            file.write(untranslatedText)

        translator,untranslatedText = Kaiseki.initialize_translator(self.guiTempKaisekiPath,self.configDir) # Initialize the translator

        Kaiseki.commence_translation(translator,untranslatedText,self.scriptDir,self.configDir,True) # Translate the text

        with open(self.translatedTextPath, "r+", encoding="utf-8") as file:
            translatedText = file.read() # Read the translated text

        with open(self.guiTempTranslationLogPath, "r+", encoding="utf-8") as file: # Write the text to a temporary file
            kaisekiResults = file.read()

        self.mainOutputLabel.delete("1.0", tk.END)
        self.mainOutputLabel.insert(tk.END, translatedText)

        try: # Try to display the results
            self.secondaryOutputLabel.delete("1.0", tk.END)
            self.secondaryOutputLabel.insert(tk.END, kaisekiResults)

        except: # if window is destroyed, create a new one
            self.create_secondary_window()
            self.secondaryOutputLabel.insert(tk.END, kaisekiResults)

        self.secondaryWindow.deiconify() # Show the results window
        self.secondaryWindow.mainloop()

#-------------------start-of-on_main_window_close()-------------------------------------------------------------------------------------------------------------------------------------------------------

    def on_main_window_close(self):

        """

        Handles the closing of the main window\n

        Parameters:\n
        None\n

        Returns:\n
        None\n

        """
        try:
            self.secondaryWindow.destroy()
        except:
            pass
        
        try:
            self.mainWindow.destroy()
        except:
            pass

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
