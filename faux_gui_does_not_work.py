import os
import gradio as gr
import tkinter as tk
import pyperclip
from tkinter import filedialog
from Kudasai import Kudasai


# -----------------START OF HELPER FUNCTIONS------------#
def copy_to_clipboard(inputText):
    pyperclip.copy(inputText)
    print("Input text copied to clipboard")


def save_text_as_file_gui(inputText):
    root = tk.Tk()
    # root.withdraw()  # Hide the main window
    file_path = filedialog.asksaveasfilename(defaultextension=".txt")  # Open the Save As dialog box

    if file_path:  # If a file path is provided
        with open(file_path, "w", encoding='utf-8') as file:
            file.write(inputText)  # Write the text to the file
    else:  # If the user cancels the dialog box
        print("Save file to TXT terminated as No file name was selected/provided.")
    root.destroy()
    return

def read_txt_file(path):
    # subfunction that reads text files for updating the UI with their contents
    working_dir = os.getcwd()
    full_path = working_dir + path
    with open(full_path, 'r', encoding='utf-8') as file:
        contents = file.read()
    return contents

def log_reader_updater():
    # Function that is called at a set interval whenever run button or Start log button is clicked.
    # This is the function that updates the respective text boxes, this is necessary as some process flow within
    # Kudasai causes the output boxes to error out if made a direct return of the primary function below
    # Interval is set in the gradio functionality section below and is set to update every two seconds
    # Absolute paths used from os.getcwd(), needs refactor to employ the preloader/filehandler module
    preprocessed_txt = read_txt_file('/KudasaiOutput/preprocessedText.txt')
    translated_text = read_txt_file('/KudasaiOutput/translatedText.txt')
    kairyou_results_txt = read_txt_file('/KudasaiOutput/Kairyou Results.txt')
    debug_log = read_txt_file('/KudasaiOutput/debug log.txt')
    error_log = read_txt_file('/KudasaiOutput/error log.txt')

    return preprocessed_txt, translated_text, kairyou_results_txt, debug_log, error_log

#----------START OF gradio_run_kudasai------------------#
def gradio_run_kudasai(input_file, json_file, auto_tl_mode):

    """
    The primary function that is called when the Run button is clicked

    input_file -> gradio file object, an input from the gr.File block,
                fileobject.name will return absolute path as a string
    json_file -> gradio file object, input from the gr.File block
    auto_tl_mode -> int (0=preprocess only, 1=preprocess+kijiku) -
                input module below for the radio button is set to input index values

    """
    # needs error handling

    kudasai = Kudasai()
    kudasai.setup_kairyou_for_cli(input_file.name, json_file.name)
    kudasai.gradio_run_kudasai()

    if auto_tl_mode == 1: #
        kudasai.gradio_run_kijiku()



# -----------------START OF GRADIO WebUI------------#

# -----------------UI design-----------------#

with gr.Blocks() as interface:

    with gr.Tab("Kudasai"):  # Tab1
        with gr.Tab('Kairyou + Kijiku') as KairyouTab:
            with gr.Row():
                with gr.Column():
                    Tab1_txt_file = gr.File(label='TXT file with Japanese Text', file_count='single', file_types=['.txt'], type='file')
                    Tab1_json_file = gr.File(label='JSON file', file_count='single',
                                                 file_types=['.json'], type='file')
                    with gr.Row():
                        Tab1_auto_TL_mode = gr.Radio(label='Auto-Translation', choices=['Preprocess only', 'AutoTL with Kijiku'], value='Preprocess only', type='index', interactive=True)

                    with gr.Row():
                        Tab1_run_btn = gr.Button('Run')
                        Tab1_clear_btn = gr.Button('Clear', variant='stop')

                    with gr.Row():
                        Tab1_start_log = gr.Button('Start log')
                        Tab1_stop_log = gr.Button('Stop Log', variant='stop')

                with gr.Column():
                    Tab1_output1 = gr.Textbox(label='Pre-processed text', lines=15, max_lines=25, interactive=False)

                    with gr.Row():
                        Tab1_copy_btn = gr.Button('Copy to Clipboard')
                        Tab1_save_btn = gr.Button('Save As')
                    # Tab1_send_to_kijiku = gr.Button('Send to Kijiku AutoTL')
            with gr.Row():
                Tab1_output2 = gr.Textbox(label='Results', lines=10, max_lines=25)
                Tab1_output4 = gr.Textbox(label='Error Log', lines=10, max_lines=25)

            with gr.Row():
                Tab1_output5 = gr.Textbox(label='Translation', lines=10, max_lines=25)

            with gr.Row():
                Tab1_output3 = gr.Textbox(label='Debug Log', lines=10, max_lines=25)


# -----------------UI functionality-----------------#
    # Functionality for Tab 1
    Tab1_run_btn.click(fn=gradio_run_kudasai, inputs=[Tab1_txt_file, Tab1_json_file, Tab1_auto_TL_mode], outputs=None)
    Tab1_copy_btn.click(fn=copy_to_clipboard, inputs=Tab1_output1, outputs=None)
    Tab1_save_btn.click(fn=save_text_as_file_gui, inputs=Tab1_output1, outputs=None)

    Tab1_clear_btn.click(fn=lambda: None, inputs=None, outputs=Tab1_json_file)
    Tab1_clear_btn.click(fn=lambda: None, inputs=None, outputs=Tab1_txt_file)

    #Logger functionality
    # preprocessed_txt, translated_text, kairyou_results_txt, debug_log, error_log

    loggerStart = Tab1_run_btn.click(fn=log_reader_updater, inputs=None, outputs=[Tab1_output1, Tab1_output5, Tab1_output2, Tab1_output3, Tab1_output4], every=2)
    loggerStartBtn = Tab1_start_log.click(fn=log_reader_updater, inputs=None, outputs=[Tab1_output1, Tab1_output5, Tab1_output2, Tab1_output3, Tab1_output4], every=2)
    loggerStopBtn = Tab1_stop_log.click(fn=None, inputs=None, outputs=None, cancels=[loggerStart, loggerStartBtn])


if __name__ == '__main__':
    interface.queue().launch(enable_queue=True)