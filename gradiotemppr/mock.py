## built-in libraries
import typing

## third-party libraries
import gradio as gr

## custom modules

## this is what i called the other py file, same directory
import gradiotemppr.dummy as dummy

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
                with gr.Tab("Preprocessing | Kairyou") as self.preprocessing_tab:
                    with gr.Row():

                        ## input files
                        with gr.Column():
                            self.input_txt_file_preprocessing = gr.File(label='TXT file with Japanese Text', file_count='single', file_types=['.txt'], type='filepath')
                            self.input_json_file = gr.File(label='Replacements JSON file', file_count='single', file_types=['.json'], type='filepath')

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
                            self.input_txt_file_kaiseki = gr.File(label='TXT file with Japanese Text', file_count='single', file_types=['.txt'], type='filepath', interactive=True)
                            self.input_text_kaiseki = gr.Textbox(label='Japanese Text', placeholder='Use this or the text file input, if you provide both, Kudasai will use the file input.', lines=10, show_label=True, interactive=True, type='text')


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

                        with gr.Column():
                            self.kaiseki_je_check_text_field = gr.Textbox(label='JE Check Text', lines=29,max_lines=29, interactive=False, show_copy_button=True)

                            with gr.Row():
                                self.save_to_file_je_check_text_kaiseki = gr.Button('Save As')

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
                
##-------------------start-of-kaiseki_translate_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            def kaiseki_translate_button_click(input_txt_file:gr.File, input_text:gr.Textbox, api_key_input:gr.Textbox) -> typing.Tuple[str, str, str]:

                """
                
                Translates the text in the input_txt_file or input_text using the DeepL API. If no txt file or text is selected, an error is raised. If no API key is provided or the API key is invalid, an error is raised.
                Displays the translated text, and the debug log.

                Parameters:
                input_txt_file (gr.File) : The input txt file.
                input_text (gr.Textbox) : The input text.
                api_key_input (gr.Textbox) : The API key input.

                Returns:
                translated_text (str) : The translated text.
                log_text (str) : The log text.
                log_text (str) : The log text.

                """        

                ## Log text is cleared from the client, so we need to get it from the log file
                log_text = ""

                ## je check text and translated text are lists of strings, so we need to convert them to strings
                translated_text = ""
                je_check_text = ""


                return translated_text, je_check_text, log_text
                 
##-------------------start-of-kaiseki_translate_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.translate_button_kaiseki.click(kaiseki_translate_button_click,
                                                inputs=[
                                                    self.input_txt_file_kaiseki,
                                                    self.input_text_kaiseki,
                                                    self.api_key_input],
                                                
                                                outputs=[
                                                    self.output_field_kaiseki, ## translated text
                                                    self.kaiseki_je_check_text_field, ## je check text field on kaiseki tab
                                                    self.debug_log_output_field_log_tab]) ## debug log on log tab
            

##-------------------start-of-launch()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------                

    def launch(self):

        """

        Launches the GUI.

        """

        self.build_gui()
        self.gui.queue().launch(inbrowser=True, show_error=True)

        ##Kudasai.boot()

##-------------------start-of-main()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

if(__name__ == '__main__'):#

    try:

        kudasai_gui = KudasaiGUI()
        kudasai_gui.launch()

    except Exception as e:

        import traceback

        print(traceback.format_exc())