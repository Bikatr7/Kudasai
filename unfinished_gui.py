import gradio as gr

class KudasaiInterface:
    def __init__(self):
        self.interface = None
        self.build_interface()

    def build_interface(self):
        with gr.Blocks() as interface:

            with gr.Tab("Kudasai"):  # Tab1
                with gr.Tab('Kairyou + Kijiku') as KairyouTab:
                    with gr.Row():
                        with gr.Column():
                            self.Tab1_txt_file = gr.File(label='TXT file with Japanese Text', file_count='single', file_types=['.txt'], type='file')
                            self.Tab1_json_file = gr.File(label='JSON file', file_count='single',
                                                     file_types=['.json'], type='file')
                            with gr.Row():
                                self.Tab1_auto_TL_mode = gr.Radio(label='Auto-Translation', choices=['Preprocess only', 'AutoTL with Kijiku'], value='Preprocess only', type='index', interactive=True)

                            with gr.Row():
                                self.Tab1_run_btn = gr.Button('Run')
                                self.Tab1_clear_btn = gr.Button('Clear', variant='stop')

                            with gr.Row():
                                self.Tab1_start_log = gr.Button('Start log')
                                self.Tab1_stop_log = gr.Button('Stop Log', variant='stop')

                        with gr.Column():
                            self.Tab1_output1 = gr.Textbox(label='Pre-processed text', lines=15, max_lines=25, interactive=False)

                            with gr.Row():
                                self.Tab1_copy_btn = gr.Button('Copy to Clipboard')
                                self.Tab1_save_btn = gr.Button('Save As')
                            # self.Tab1_send_to_kijiku = gr.Button('Send to Kijiku AutoTL')
                    with gr.Row():
                        self.Tab1_output2 = gr.Textbox(label='Results', lines=10, max_lines=25)
                        self.Tab1_output4 = gr.Textbox(label='Error Log', lines=10, max_lines=25)

                    with gr.Row():
                        self.Tab1_output5 = gr.Textbox(label='Translation', lines=10, max_lines=25)

                    with gr.Row():
                        self.Tab1_output3 = gr.Textbox(label='Debug Log', lines=10, max_lines=25)

        self.interface = interface

    def launch(self):
        if self.interface:
            self.interface.queue().launch(inbrowser=True, show_error=True, server_name="127.0.0.1")

if __name__ == '__main__':
    kudasai_interface = KudasaiInterface()
    kudasai_interface.launch()
