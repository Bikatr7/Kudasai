import tkinter as tk


class KudasaiGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Kudasai GUI")
        self.window.configure(bg="#202020")
        self.window.geometry("1200x600")

        self.text_color = "#FFFFFF"

        self.create_text_entry()
        self.create_buttons()
        self.create_option_menu()
        self.create_label()

    def create_text_entry(self):
        self.text_entry = tk.Text(self.window, bg="#303030", fg=self.text_color, height=18, width=600)
        self.text_entry.pack()

    def create_buttons(self):
        self.button_frame = tk.Frame(self.window, bg="#202020")
        self.button_frame.pack(pady=10)

        button1 = tk.Button(self.button_frame, text="Display Text", bg="#303030", fg=self.text_color, command=self.display_text)
        button1.pack(side=tk.LEFT, padx=5)

    def create_option_menu(self):
        options = ["Option 1", "Option 2", "Option 3"]  # Hardcoded options
        self.selected_option = tk.StringVar()  # Variable to hold the selected option
        self.selected_option.set(options[0])  # Set the initial selected option

        option_menu = tk.OptionMenu(self.button_frame, self.selected_option, *options)  # Create the drop-down menu
        option_menu.configure(bg="#303030", fg=self.text_color, highlightbackground="#303030")  # Set colors
        option_menu.pack(side=tk.LEFT, padx=5)

    def create_label(self):
        self.label = tk.Label(self.window, bg="#303030", fg=self.text_color, height=18, width=600)
        self.label.pack()

    def display_text(self):
        text = self.text_entry.get("1.0", tk.END)
        self.label.config(text=text, justify=tk.LEFT, anchor=tk.NW)

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    gui = KudasaiGUI()
    gui.run()
