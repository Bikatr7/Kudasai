## third-party libraries
import gradio as gr

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

            ## tab 1
            with gr.Tab("Kudasai") as self.kudasai_tab:

                ## tab 2
                with gr.Tab("Preprocessing and Translation") as self.model_tab:
                    with gr.Row():

                        ## input files
                        with gr.Column():
                            self.input_txt_file = gr.File(label='TXT file with Japanese Text', file_count='single', file_types=['.txt'], type='file')
                            self.input_json_file = gr.File(label='Replacements JSON file', file_count='single', file_types=['.json'], type='file')

                            ## mode selection 
                            with gr.Row():
                                self.mode_selection = gr.Dropdown(label='Mode', choices=['Preprocess only', 'AutoTL with OpenAI', 'AutoTL with DeepL'], value='Preprocess only', type='index', interactive=True)

                            with gr.Row():
                                self.api_key_input = gr.Textbox(label='API Key (Not needed for preprocess)', lines=1, show_label=True, interactive=True, type='password')

                            ## run and clear buttons
                            with gr.Row():
                                self.run_button = gr.Button('Run')
                                self.clear_button = gr.Button('Clear', variant='stop')

                        ## output fields
                        with gr.Column():
                            self.preprocess_output_field  = gr.Textbox(label='Preprocessed text', lines=33, show_label=True, interactive=False, show_copy_button=True)

                            with gr.Row():
                                self.save_to_file_one = gr.Button('Save As')
                            
                        with gr.Column():
                            self.translation_output_field = gr.Textbox(label='Translated Text', lines=33, show_label=True, interactive=False, show_copy_button=True)

                            with gr.Row():
                                self.save_to_file_two = gr.Button('Save As')
                ## tab 3
                with gr.Tab("Logging") as self.results_tab:
                    with gr.Row():
                        self.preprocessing_results = gr.Textbox(label='Preprocessing Results', lines=10, interactive=False)

                    with gr.Row():
                        self.debug_log = gr.Textbox(label='Debug Log', lines=10, interactive=False)

                    with gr.Row():
                        self.error_log = gr.Textbox(label='Error Log', lines=10, interactive=False)


            def run_button_click(filepath):

                if(self.input_txt_file is not None):

                    txt_file_path = filepath.name ## type: ignore

                    with open(txt_file_path, "r", encoding='utf-8') as file:
                        text = file.read()

                    return text

            self.run_button.click(fn=run_button_click, inputs=[self.input_txt_file], outputs=[self.preprocess_output_field])

##-------------------start-of-launch()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------                

    def launch(self):

        """

        Launches the GUI.

        """

        self.build_gui()
        self.gui.queue().launch(inbrowser=True, show_error=True)

##-------------------start-of-main()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

if(__name__ == '__main__'):
    kudasai_gui = KudasaiGUI()
    kudasai_gui.launch()
