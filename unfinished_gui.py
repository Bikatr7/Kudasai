## built-in libraries
import io
from os import error
from re import S
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

    ## scary javascript code that allows us to save textbox contents to a file
    save_as_js = """
    (text) => {
        const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'downloaded_text.txt';
        a.click();
        URL.revokeObjectURL(url);
    }
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
                with gr.Tab("Preprocessing | Kairyou") as self.preprocessing_tab:
                    with gr.Row():

                        ## input files
                        with gr.Column():
                            self.input_txt_file_preprocessing = gr.File(label='TXT file with Japanese Text', file_count='single', file_types=['.txt'], type='file')
                            self.input_json_file = gr.File(label='Replacements JSON file', file_count='single', file_types=['.json'], type='file')

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
                                self.save_to_file_debug_log_preprocessing_tab = gr.Button('Save As')


                ## tab 3 | Translation Model 1 | Kaiseki
                with gr.Tab("Translation With DeepL | Kaiseki") as self.kaiseki_tab:
                    with gr.Row():

                        ## input file or text input, gui allows for both but will prioritize file input
                        with gr.Column():
                            self.input_txt_file_kaiseki = gr.File(label='TXT file with Japanese Text', file_count='single', file_types=['.txt'], type='file',interactive=True)
                            self.input_text_kaiseki = gr.Textbox(label='Japanese Text', value='Use this or the text file input, if you provide both, Kudasai will use the file input.', lines=10, show_label=True, interactive=True, type='text')


                            with gr.Row():
                                self.api_key_input = gr.Textbox(label='API Key', lines=1, show_label=True, interactive=True, type='password')

                            with gr.Row():
                                self.translate_button_kaiseki = gr.Button('Translate')
                                self.clear_button_kaiseki = gr.Button('Clear', variant='stop')

                        ## output fields
                        with gr.Column():
                            self.output_field_kaiseki = gr.Textbox(label='Translated Text', lines=29,max_lines=29, interactive=False, show_copy_button=True)

                            with gr.Row():
                                self.save_to_file_kaiseki = gr.Button('Save As')

                        with gr.Column():
                            self.debug_log_output_field_kaiseki_tab = gr.Textbox(label='Debug Log', lines=29,max_lines=29, interactive=False, show_copy_button=True)

                            with gr.Row():
                                self.save_to_file_debug_log_kaiseki_tab = gr.Button('Save As')


                ## tab 4 | Logging
                with gr.Tab("Logging") as self.results_tab:

                    with gr.Row():
                        self.debug_log_output_field_log_tab = gr.Textbox(label='Debug Log', lines=10, interactive=False)

                    with gr.Row():
                        self.save_to_file_debug_log_logging_tab = gr.Button('Save As')

                    with gr.Row():
                        self.error_log = gr.Textbox(label='Error Log', lines=10, interactive=False)

                    with gr.Row():
                        self.save_to_file_error_log = gr.Button('Save As')

                    with gr.Row():
                        self.clear_log_button = gr.Button('Clear Log', variant='stop')

##-------------------start-of-Listener-Functions---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

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

            def preprocessing_clear_button_click() -> typing.Tuple[None, None, str, str, str]:

                """

                Clears all fields on the preprocessing tab. As well as the input fields.

                """

                input_txt_file = None
                input_json_file = None

                preprocess_output_field = ""
                preprocessing_results_output_field = ""
                debug_log_output_field_preprocess_tab = ""

                return input_txt_file, input_json_file, preprocess_output_field, preprocessing_results_output_field, debug_log_output_field_preprocess_tab
            
##-------------------start-of-kaiseki_run_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            def kaiseki_clear_button_click() -> typing.Tuple[None, str, str, str]:

                """
                
                Clears all fields on the Kaiseki tab. As well as the input fields.

                """

                input_file_kaiseki = None
                input_text_kaiseki = ""

                output_field_kaiseki = ""
                debug_log_output_field_kaiseki_tab = ""

                return input_file_kaiseki, input_text_kaiseki, output_field_kaiseki, debug_log_output_field_kaiseki_tab
            
##-------------------start-of-clear_log_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        
            def clear_log_button_click() -> typing.Tuple[str, str]:

                """

                Clears the logs on the log tab.

                """

                debug_log_output_field_log_tab = ""
                error_log = ""

                return debug_log_output_field_log_tab, error_log
            
##-------------------start-of-Listener-Declaration---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

##-------------------start-of-preprocessing_run_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.preprocessing_run_button.click(fn=preprocessing_run_button_click, 
                                                inputs=[
                                                    self.input_txt_file_preprocessing,
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
                                                      self.input_txt_file_preprocessing, ## input txt file
                                                      self.input_json_file, ## input json file
                                                      self.preprocess_output_field, ## preprocessed text output field
                                                      self.preprocessing_results_output_field, ## preprocessing results output field
                                                      self.debug_log_output_field_preprocess_tab])## debug log on preprocess tab

##-------------------start-of-clear_button_kaiseki_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.clear_button_kaiseki.click(kaiseki_clear_button_click,
                                            inputs=[],

                                            outputs=[
                                                self.input_txt_file_kaiseki, ## input txt file
                                                self.input_text_kaiseki, ## input text
                                                self.output_field_kaiseki, ## translation output field
                                                self.debug_log_output_field_kaiseki_tab]) ## debug log on kaiseki tab
            
##-------------------start-of-clear_log_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.clear_log_button.click(clear_log_button_click,
                                        inputs=[],

                                        outputs=[
                                            self.debug_log_output_field_log_tab,
                                            self.error_log])
            
        
##-------------------start-of-save_to_file_preprocessing_results_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.save_to_file_preprocessed_text.click(lambda text: text, ## save text as is
                inputs=[self.preprocess_output_field],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                _js=(self.save_as_js).replace("downloaded_text.txt", "preprocessed_text.txt")
            )
            
##-------------------start-of-save_to_file_preprocessing_results_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.save_to_file_preprocessing_results.click(lambda text: text, ## save text as is
                inputs=[self.preprocessing_results_output_field],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                _js=(self.save_as_js).replace("downloaded_text.txt", "preprocessing_results.txt")
            )

##-------------------start-of-save_to_file_debug_log_processing_tab_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.save_to_file_debug_log_preprocessing_tab.click(lambda text: text, ## save text as is
                inputs=[self.debug_log_output_field_preprocess_tab],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                _js=(self.save_as_js).replace("downloaded_text.txt", "processing_debug_log.txt")
            )


##-------------------start-of-save_to_file_kaiseki_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.save_to_file_kaiseki.click(lambda text: text, ## save text as is
                inputs=[self.output_field_kaiseki],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                _js=(self.save_as_js).replace("downloaded_text.txt", "translated_text.txt")
            )

##-------------------start-of-save_to_file_debug_log_kaiseki_tab_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.save_to_file_debug_log_kaiseki_tab.click(lambda text: text, ## save text as is
                inputs=[self.debug_log_output_field_kaiseki_tab],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                _js=(self.save_as_js).replace("downloaded_text.txt", "kaiseki_debug_log.txt")
            )

##-------------------start-of-save_to_file_debug_log_logging_tab_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.save_to_file_debug_log_logging_tab.click(lambda text: text, ## save text as is
                inputs=[self.debug_log_output_field_log_tab],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                _js=(self.save_as_js).replace("downloaded_text.txt", "debug_log_all.txt")
            )

##-------------------start-of-save_to_file_error_log_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.save_to_file_error_log.click(lambda text: text, ## save text as is
                inputs=[self.error_log],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                _js=(self.save_as_js).replace("downloaded_text.txt", "error_log.txt")
            )

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
