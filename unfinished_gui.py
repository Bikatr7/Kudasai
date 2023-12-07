## built-in libraries
import typing

## third-party libraries
import gradio as gr

## custom modules
from modules.common.toolkit import Toolkit
from modules.common.logger import Logger
from modules.common.file_ensurer import FileEnsurer

from modules.gui.gui_file_util import gui_get_text_from_file, gui_get_json_from_file

from models.kairyou import Kairyou

from kudasai import Kudasai

##-------------------start-of-KudasaiGUI---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class KudasaiGUI:

    """
    
    Kudasai is a class that contains the GUI for Kudasai.

    """


##-------------------start-of-build_gui()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def build_gui(self):

        """

        Builds the GUI.

        """

        with gr.Blocks() as self.gui:

            ## tab 1 | Main
            with gr.Tab("Kudasai") as self.kudasai_tab:

                ## tab 2 | preprocessing
                with gr.Tab("Preprocessing") as self.preprocessing_tab:
                    with gr.Row():

                        ## input files
                        with gr.Column():
                            self.input_txt_file = gr.File(label='TXT file with Japanese Text', file_count='single', file_types=['.txt'], type='file')
                            self.input_json_file = gr.File(label='Replacements JSON file', file_count='single', file_types=['.json'], type='file')

                            ##self.api_key_input = gr.Textbox(label='API Key (Not needed for preprocess)', lines=1, show_label=True, interactive=True, type='password')

                            ## run and clear buttons
                            with gr.Row():
                                self.preprocessing_run_button = gr.Button('Run')
                                self.preprocessing_clear_button = gr.Button('Clear', variant='stop')

                        ## output fields
                        with gr.Column():
                            self.preprocess_output_field  = gr.Textbox(label='Preprocessed text', lines=22, max_lines=22, show_label=True, interactive=False, show_copy_button=True)

                            with gr.Row():
                                self.save_to_file_preprocessed_text = gr.Button('Save As')
                            
                        with gr.Column():
                            self.preprocessing_results_output_field = gr.Textbox(label='Preprocessing Results', lines=22, interactive=False, show_copy_button=True)

                            with gr.Row():
                                self.save_to_file_preprocessing_results = gr.Button('Save As')

                        with gr.Column():
                            self.debug_log_output_field_preprocess_tab = gr.Textbox(label='Debug Log', lines=22, interactive=False, show_copy_button=True)

                            with gr.Row():
                                self.save_to_file_debug_log = gr.Button('Save As')


                ## tab 3 | Logging
                with gr.Tab("Logging") as self.results_tab:

                    with gr.Row():
                        self.debug_log_output_field_log_tab = gr.Textbox(label='Debug Log', lines=10, interactive=False)

                    with gr.Row():
                        self.error_log = gr.Textbox(label='Error Log', lines=10, interactive=False)

##-------------------start-of-preprocessing_run_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            def preprocessing_run_button_click(input_txt_file:gr.File, input_json_file:gr.File) -> typing.Tuple[str, str, str, str]:

                """

                Runs the preprocessing and displays the results in the preprocessing output field. If no txt file is selected, an error is raised. If no json file is selected, an error is raised.
                Also displays the preprocessing results, and the debug log.

                Parameters:
                input_txt_file (gr.File) : The input txt file.
                input_json_file (gr.File) : The input json file.

                """

                if(input_txt_file is not None):

                    if(input_json_file is not None):
                        text_to_preprocess = gui_get_text_from_file(input_txt_file)
                        replacements = gui_get_json_from_file(input_json_file)

                        Kairyou.text_to_preprocess = text_to_preprocess
                        Kairyou.replacement_json = replacements

                        Kairyou.preprocess()

                        Kairyou.write_kairyou_results()

                        ## Log text and Preprocessing is cleared from the client, so we need to get it from the log file
                        log_text = FileEnsurer.standard_read_file(Logger.log_file_path)
                        preprocessing_log = FileEnsurer.standard_read_file(FileEnsurer.kairyou_log_path)

                        ## Kairyou is a "in-place" replacement, so we can just return the text_to_preprocess, as for the double log text return, we do that because we want to display the log text on the log tab, and on the preprocess tab
                        return Kairyou.text_to_preprocess, preprocessing_log, log_text, log_text
                        
                    
                    else:
                        raise gr.Error("No JSON file selected")
                
                else:
                    raise gr.Error("No TXT file selected")

##-------------------start-of-preprocessing_clear_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------                

            def preprocessing_clear_button_click() -> typing.Tuple[None, None, str, str, str, str]:

                """

                Clears all fields on the preprocessing tab. As well as the input fields.

                """

                input_txt_file = None
                input_json_file = None

                preprocess_output_field = ""
                preprocessing_results_output_field = ""
                debug_log_output_field_preprocess_tab = ""
                debug_log_output_field_log_tab = ""

                return input_txt_file, input_json_file, preprocess_output_field, preprocessing_results_output_field, debug_log_output_field_preprocess_tab, debug_log_output_field_log_tab

##-------------------start-of-Listeners---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

##-------------------start-of-preprocessing_run_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.preprocessing_run_button.click(fn=preprocessing_run_button_click, 
                                                inputs=[
                                                    self.input_txt_file,
                                                    self.input_json_file], 
                                                                                           
                                                outputs=[
                                                    self.preprocess_output_field,  ## preprocessed text
                                                    self.preprocessing_results_output_field,  ## kairyou results
                                                    self.debug_log_output_field_preprocess_tab, ## debug log on preprocess tab
                                                    self.debug_log_output_field_log_tab]) ## debug log on log tab
            
##-------------------start-of-preprocessing_clear_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.preprocessing_clear_button.click(preprocessing_clear_button_click,
                                                  inputs=[],

                                                  outputs=[
                                                      self.input_txt_file,
                                                      self.input_json_file,
                                                      self.preprocess_output_field,
                                                      self.preprocessing_results_output_field,
                                                      self.debug_log_output_field_preprocess_tab,
                                                      self.debug_log_output_field_log_tab])
            
##-------------------start-of-launch()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------                

    def launch(self):

        """

        Launches the GUI.

        """

        self.build_gui()
        self.gui.launch(inbrowser=True, show_error=True)

        Kudasai.boot()

##-------------------start-of-main()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

if(__name__ == '__main__'):

    try:

        kudasai_gui = KudasaiGUI()
        kudasai_gui.launch()

        Logger.push_batch()

    except Exception as e:

        FileEnsurer.handle_critical_exception(e)
