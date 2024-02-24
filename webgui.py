## built-in libraries
import typing
import base64

## third-party libraries
import gradio as gr

from kairyou import Indexer
from kairyou import Kairyou

## custom modules
from modules.common.toolkit import Toolkit
from modules.common.logger import Logger
from modules.common.file_ensurer import FileEnsurer

from modules.gui.gui_file_util import gui_get_text_from_file, gui_get_json_from_file
from modules.gui.gui_json_util import GuiJsonUtil

from handlers.json_handler import JsonHandler

from models.kaiseki import Kaiseki
from models.kijiku import Kijiku
from translation_services.deepl_service import DeepLService

from translation_services.openai_service import OpenAIService

from kudasai import Kudasai

##-------------------start-of-KudasaiGUI---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class KudasaiGUI:

    """
    
    KudasaiGUI is a class that contains the GUI for Kudasai.

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

    ## used for whether the debug log tab for kaiseki/kijiku should be actively refreshing based of Logger.current_batch
    is_translation_ongoing = False

##-------------------start-of-build_gui()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def build_gui(self) -> None:

        """

        Builds the GUI.

        """

        with gr.Blocks(title="Kudasai") as self.gui:

##-------------------start-of-Utility-Functions---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

##-------------------start-of-fetch_log_content()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            def fetch_log_content() -> str:

                """
                
                Fetches the log content from the current log batch.

                Returns:
                log_text (str) : The log text.

                """

                if(self.is_translation_ongoing == False):
                    return "No translation ongoing"

                if(Logger.current_batch == ""):
                    return "No log content found."
                
                return Logger.current_batch
            
##-------------------start-of-get_saved_kaiseki_api_key()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            def get_saved_kaiseki_api_key() -> str:

                """
                
                Gets the saved kaiseki api key from the config folder, if it exists.

                Returns:
                api_key (str) : The api key.

                """

                try:
                    ## Api key is encoded in base 64 so we need to decode it before returning
                    return base64.b64decode(FileEnsurer.standard_read_file(FileEnsurer.deepl_api_key_path).encode('utf-8')).decode('utf-8')
                
                except:
                    return ""
                
##-------------------start-of-get_saved_kijiku_api_key()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
                
            def get_saved_kijiku_api_key() -> str:

                """
                
                Gets the kijiku saved api key from the config folder, if it exists.

                Returns:
                api_key (str) : The api key.

                """

                try:
                    ## Api key is encoded in base 64 so we need to decode it before returning
                    return base64.b64decode(FileEnsurer.standard_read_file(FileEnsurer.openai_api_key_path).encode('utf-8')).decode('utf-8')
                
                except:
                    return ""

##-------------------start-of-create_new_key_value_tuple_pairs()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------    

            def create_new_key_value_tuple_pairs(kijiku_settings:typing.List[str]) -> typing.List[typing.Tuple[str, str]]:
                
                """

                Applies the new kijiku settings to the uploaded kijiku rules file.

                Parameters:
                kijiku_settings (typing.List[typing.Union[gr.Textbox,gr.Slider,gr.Dropdown]]) : The kijiku setting values

                Returns:
                key_value_tuple_pairs (typing.List[typing.Tuple[str, str]]) : The new key value tuple pairs.

                """

                key_value_tuple_pairs = []

                kijiku_settings_key_names = {
                    0 : "model",
                    1 : "system_message",
                    2 : "temp",
                    3 : "top_p",
                    4 : "n",
                    5 : "stream",
                    6 : "stop",
                    7 : "logit_bias",
                    8 : "max_tokens",
                    9 : "presence_penalty",
                    10 : "frequency_penalty",
                    11 : "message_mode",
                    12 : "num_lines",
                    13 : "sentence_fragmenter_mode",
                    14 : "je_check_mode",
                    15 : "num_malformed_batch_retries",
                    16 : "batch_retry_timeout",
                    17 : "num_concurrent_batches"
                }

                for index, setting in enumerate(kijiku_settings):
                    key = kijiku_settings_key_names.get(index)

                    key_value_tuple_pairs.append((key, setting))

                return key_value_tuple_pairs
            
##-------------------start-of-GUI-Structure---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            ## tab 1 | Main
            with gr.Tab("Kudasai") as self.kudasai_tab:


                ## tab 3 | indexing
                with gr.Tab("Indexing | Kairyou") as self.indexing_tab:
                    with gr.Row():

                        ## input fields, text input for indexing, and replacement json file input.
                        with gr.Column():
                            self.input_txt_file_indexing = gr.File(label='TXT file with Japanese Text', file_count='single', file_types=['.txt'], type='filepath')
                            self.input_json_file_indexing = gr.File(label='Replacements JSON file', file_count='single', file_types=['.json'], type='filepath')
                            self.knowledge_base_file = gr.File(label='Knowledge Base Single File', file_count='single', file_types=['.txt'], type='filepath')
                            self.knowledge_base_directory = gr.File(label='Knowledge Base Directory', file_count='directory', type='filepath')

                            ## run and clear buttons
                            with gr.Row():
                                self.indexing_run_button = gr.Button('Run', variant='primary')
                                self.indexing_clear_button = gr.Button('Clear', variant='stop')

                            with gr.Row():
                                self.send_to_kairyou = gr.Button('Send to Kairyou (Preprocessing)')

                        ## output fields
                        with gr.Column():
                            self.indexing_output_field  = gr.Textbox(label='Indexed text', lines=51, max_lines=51, show_label=True, interactive=False, show_copy_button=True)

                            with gr.Row():
                                self.save_to_file_indexed_text = gr.Button('Save As')
                            
                        with gr.Column():
                            self.indexing_results_output_field = gr.Textbox(label='Indexing Results', lines=51, max_lines=51, interactive=False, show_copy_button=True)

                            with gr.Row():
                                self.save_to_file_indexing_results = gr.Button('Save As')

                        with gr.Column():
                            self.debug_log_output_field_indexing_tab = gr.Textbox(label='Debug Log', lines=51, max_lines=51, interactive=False, show_copy_button=True)

                            with gr.Row():
                                self.save_to_file_debug_log_indexing_tab = gr.Button('Save As')


                ## tab 3 | preprocessing
                with gr.Tab("Preprocessing | Kairyou") as self.preprocessing_tab:
                    with gr.Row():

                        ## input fields, text input for preprocessing, and replacement json file input.
                        with gr.Column():
                            self.input_txt_file_preprocessing = gr.File(label='TXT file with Japanese Text', file_count='single', file_types=['.txt'], type='filepath')
                            self.input_json_file_preprocessing = gr.File(label='Replacements JSON file', file_count='single', file_types=['.json'], type='filepath')
                            self.input_text_kairyou = gr.Textbox(label='Japanese Text', placeholder='Use this or the text file input, if you provide both, Kudasai will use the file input.', lines=10, show_label=True, interactive=True)

                            ## run and clear buttons
                            with gr.Row():
                                self.preprocessing_run_button = gr.Button('Run', variant='primary')
                                self.preprocessing_clear_button = gr.Button('Clear', variant='stop')

                            with gr.Row():
                                self.send_to_kaiseki = gr.Button('Send to Kaiseki (DeepL)')
                                self.send_to_kijiku = gr.Button('Send to Kijiku (OpenAI)')

                        ## output fields
                        with gr.Column():
                            self.preprocess_output_field  = gr.Textbox(label='Preprocessed text', lines=41, max_lines=41, show_label=True, interactive=False, show_copy_button=True)

                            with gr.Row():
                                self.save_to_file_preprocessed_text = gr.Button('Save As')
                            
                        with gr.Column():
                            self.preprocessing_results_output_field = gr.Textbox(label='Preprocessing Results', lines=41, max_lines=41, interactive=False, show_copy_button=True)

                            with gr.Row():
                                self.save_to_file_preprocessing_results = gr.Button('Save As')

                        with gr.Column():
                            self.debug_log_output_field_preprocess_tab = gr.Textbox(label='Debug Log', lines=41, max_lines=41, interactive=False, show_copy_button=True)

                            with gr.Row():
                                self.save_to_file_debug_log_preprocessing_tab = gr.Button('Save As')

                ## tab 4 | Translation Model 1 | Kaiseki
                with gr.Tab("Translation With DeepL | Kaiseki") as self.kaiseki_tab:
                    with gr.Row():

                        ## input file or text input, gui allows for both but will prioritize file input
                        with gr.Column():
                            self.input_txt_file_kaiseki = gr.File(label='TXT file with Japanese Text', file_count='single', file_types=['.txt'], type='filepath', interactive=True)
                            self.input_text_kaiseki = gr.Textbox(label='Japanese Text', placeholder='Use this or the text file input, if you provide both, Kudasai will use the file input.', lines=10, show_label=True, interactive=True)


                            with gr.Row():
                                self.kaiseki_api_key_input = gr.Textbox(label='API Key', value=get_saved_kaiseki_api_key, lines=1, show_label=True, interactive=True, type='password')

                            with gr.Row():
                                self.translate_button_kaiseki = gr.Button('Translate', variant="primary")
                                self.clear_button_kaiseki = gr.Button('Clear', variant='stop')

                        ## output fields
                        with gr.Column():
                            self.output_field_kaiseki = gr.Textbox(label='Translated Text', lines=29,max_lines=29, interactive=False, show_copy_button=True)

                            with gr.Row():
                                self.save_to_file_kaiseki = gr.Button('Save As')

                        with gr.Column():
                            self.kaiseki_je_check_text_field = gr.Textbox(label='JE Check Text', lines=29,max_lines=29, interactive=False, show_copy_button=True)

                            with gr.Row():
                                self.save_to_file_je_check_text_kaiseki = gr.Button('Save As')

                        with gr.Column():
                            self.debug_log_output_field_kaiseki_tab = gr.Textbox(label='Debug Log', lines=29,max_lines=29, interactive=False, show_copy_button=True)

                            with gr.Row():
                                self.save_to_file_debug_log_kaiseki_tab = gr.Button('Save As')

                ## tab 5 | Translation Model 2 | Kijiku
                with gr.Tab("Translation With OpenAI | Kijiku") as self.kijiku_tab:
                    with gr.Row():

                        ## input file or text input, gui allows for both but will prioritize file input
                        with gr.Column():
                            self.input_txt_file_kijiku = gr.File(label='TXT file with Japanese Text', file_count='single', file_types=['.txt'], type='filepath', interactive=True)
                            self.input_text_kijiku = gr.Textbox(label='Japanese Text', placeholder='Use this or the text file input, if you provide both, Kudasai will use the file input.', lines=10, show_label=True, interactive=True, type='text')
                            self.input_kijiku_rules_file = gr.File(value = FileEnsurer.config_kijiku_rules_path, label='Kijiku Rules File', file_count='single', file_types=['.json'], type='filepath')

                            with gr.Row():
                                self.kijiku_api_key_input = gr.Textbox(label='API Key', value=get_saved_kijiku_api_key, lines=1, max_lines=2, show_label=True, interactive=True, type='password')

                            with gr.Row():
                                self.translate_button_kijiku = gr.Button('Translate', variant="primary")
                                self.calculate_costs_button_kijiku = gr.Button('Calculate Costs', variant='secondary')

                            with gr.Row():
                                self.clear_button_kijiku = gr.Button('Clear', variant='stop')

                        ## output fields
                        with gr.Column():
                            self.kijiku_translated_text_output_field = gr.Textbox(label='Translated Text', lines=36,max_lines=36, interactive=False, show_copy_button=True)

                            with gr.Row():
                                self.save_to_file_kijiku = gr.Button('Save As')

                        with gr.Column():
                            self.kijiku_je_check_text_field = gr.Textbox(label='JE Check Text', lines=36,max_lines=36, interactive=False, show_copy_button=True)

                            with gr.Row():
                                self.save_to_file_je_check_text_kijiku = gr.Button('Save As')

                        with gr.Column():
                            self.debug_log_output_field_kijiku_tab = gr.Textbox(label='Debug Log', lines=36, max_lines=36, interactive=False, show_copy_button=True)

                            with gr.Row():
                                self.save_to_file_debug_log_kijiku_tab = gr.Button('Save As')

                ## tab 6 | Kijiku Settings
                with gr.Tab("Kijiku Settings") as self.kijiku_settings_tab:
                    with gr.Row():

                        with gr. Column():
                            gr.Markdown("OpenAI API Settings")
                            self.model_input_field = gr.Dropdown(label='Model',
                                                                value=GuiJsonUtil.fetch_kijiku_setting_key_values("model"),
                                                                choices=FileEnsurer.allowed_models, ## type: ignore
                                                                info="ID of the model to use. As of right now, Kijiku only works with 'chat' models.",
                                                                show_label=True,
                                                                interactive=True,
                                                                elem_id="model")

                            self.temperature_input_field = gr.Slider(label='Temperature',
                                                                    value=float(GuiJsonUtil.fetch_kijiku_setting_key_values("temp")),
                                                                    minimum=0.0,
                                                                    maximum=2.0,
                                                                    info="What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. Lower values are typically better for translation.",
                                                                    show_label=True,
                                                                    interactive=True,
                                                                    elem_id="temp")

                            self.top_p_input_field = gr.Slider(label='Top P',
                                                               value=float(GuiJsonUtil.fetch_kijiku_setting_key_values("top_p")),
                                                               minimum=0.0,
                                                               maximum=1.0,
                                                               info="An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. I generally recommend altering this or temperature but not both.",
                                                               show_label=True,
                                                               interactive=True,
                                                               elem_id="top_p")

                            self.n_input_field = gr.Textbox(label='N',
                                                            value=(GuiJsonUtil.fetch_kijiku_setting_key_values("n")),
                                                            info="How many chat completion choices to generate for each input message. Do not change this.",
                                                            show_label=True,
                                                            interactive=False,
                                                            elem_id="n")

                            self.stream_input_field = gr.Textbox(label='Stream',
                                                                value=str((GuiJsonUtil.fetch_kijiku_setting_key_values("stream"))),
                                                                info="If set, partial message deltas will be sent, like in ChatGPT. Tokens will be sent as data-only server-sent events as they become available, with the stream terminated by a data: [DONE] message. See the OpenAI python library on GitHub for example code. Do not change this.",
                                                                lines=1,
                                                                max_lines=1,
                                                                show_label=True,
                                                                interactive=False,
                                                                elem_id="stream")

                            self.stop_input_field = gr.Textbox(label='Stop',
                                                               value=str((GuiJsonUtil.fetch_kijiku_setting_key_values("stop"))),
                                                               info="Up to 4 sequences where the API will stop generating further tokens. Do not change this.",
                                                               lines=1,
                                                               max_lines=1,
                                                               show_label=True,
                                                               interactive=False,
                                                               elem_id="stop")

                            self.logit_bias_input_field = gr.Textbox(label='Logit Bias',
                                                                    value=str((GuiJsonUtil.fetch_kijiku_setting_key_values("logit_bias"))),
                                                                    info="Modifies the likelihood of specified tokens appearing in the completion. Do not change this.",
                                                                    lines=1,
                                                                    max_lines=1,
                                                                    show_label=True,
                                                                    interactive=False,
                                                                    elem_id="logit_bias")

                            self.max_tokens_input_field = gr.Textbox(label='Max Tokens',
                                                                    value=str((GuiJsonUtil.fetch_kijiku_setting_key_values("max_tokens"))),
                                                                    info="max_tokens :  The maximum number of tokens to generate in the chat completion. The total length of input tokens and generated tokens is limited by the model's context length. I wouldn't recommend changing this. Is none by default. If you change to an integer, make sure it doesn't exceed that model's context length or your request will fail and repeat till timeout.",
                                                                    lines=1,
                                                                    max_lines=1,
                                                                    show_label=True,
                                                                    interactive=True,
                                                                    elem_id="max_tokens")

                            self.presence_penalty_input_field = gr.Slider(label='Presence Penalty',
                                                                          value=float(GuiJsonUtil.fetch_kijiku_setting_key_values("presence_penalty")),
                                                                          minimum=-2.0,
                                                                          maximum=2.0,
                                                                          info="Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics. While negative values encourage repetition. Should leave this at 0.0.",
                                                                          show_label=True,
                                                                          interactive=True,
                                                                          elem_id="presence_penalty")

                            self.frequency_penalty_input_field = gr.Slider(label='Frequency Penalty',
                                                                           value=float(GuiJsonUtil.fetch_kijiku_setting_key_values("frequency_penalty")),
                                                                           minimum=-2.0,
                                                                           maximum=2.0,
                                                                           info="Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim. Negative values encourage repetition. Should leave this at 0.0.",
                                                                           show_label=True,
                                                                           interactive=True,
                                                                           elem_id="frequency_penalty")

                        with gr.Column():
                            gr.Markdown("Kijiku Process Configuration")

                            self.system_message_input_field = gr.Textbox(label='System Message',
                                                                        value=GuiJsonUtil.fetch_kijiku_setting_key_values("system_message"),
                                                                        info="Instructions to the model. Basically tells the model what to do.",
                                                                        lines=10,
                                                                        max_lines=10,
                                                                        show_label=True,
                                                                        interactive=True,
                                                                        elem_id="system_message")

                            self.message_mode_input_field = gr.Dropdown(label='Message Mode',
                                                                        value=int(GuiJsonUtil.fetch_kijiku_setting_key_values("message_mode")),
                                                                        choices=[1,2],
                                                                        info="1 or 2. 1 means the system message will actually be treated as a system message. 2 means it'll be treated as a user message. 1 is recommend for gpt-4 otherwise either works.",
                                                                        show_label=True,
                                                                        interactive=True,
                                                                        elem_id="message_mode")

                            self.num_lines_input_field = gr.Textbox(label='Number of Lines Per Batch',
                                                                    value=(GuiJsonUtil.fetch_kijiku_setting_key_values("num_lines")),
                                                                    info="The number of lines to be built into a prompt at once. Theoretically, more lines would be more cost effective, but other complications may occur with higher lines. So far been tested up to 48.",
                                                                    lines=1,
                                                                    max_lines=1,
                                                                    show_label=True,
                                                                    interactive=True,
                                                                    elem_id="num_lines")

                            self.sentence_fragmenter_mode_input_field = gr.Dropdown(label='Sentence Fragmenter Mode',
                                                                                    value=int(GuiJsonUtil.fetch_kijiku_setting_key_values("sentence_fragmenter_mode")),
                                                                                    choices=[1,2,3],
                                                                                    info="1 or 2 or 3 (1 - via regex and other nonsense, 2 - NLP via spacy (depreciated, will default to 3 if you select 2), 3 - None (Takes formatting and text directly from API return)) the API can sometimes return a result on a single line, so this determines the way Kijiku fragments the sentences if at all. Use 3 for gpt-4.",
                                                                                    show_label=True,
                                                                                    interactive=True,
                                                                                    elem_id="sentence_fragmenter_mode")

                            self.je_check_mode_input_field = gr.Dropdown(label='JE Check Mode',
                                                                        value=int(GuiJsonUtil.fetch_kijiku_setting_key_values("je_check_mode")),
                                                                        choices=[1,2],
                                                                        info="1 or 2, 1 will print out the jap then the english below separated by ---, 2 will attempt to pair the english and jap sentences, placing the jap above the eng. If it cannot, it will default to 1. Use 2 for gpt-4.",
                                                                        show_label=True,
                                                                        interactive=True,
                                                                        elem_id="je_check_mode")


                            self.num_malformed_batch_retries_input_field = gr.Textbox(label='Number of Malformed Batch Retries',
                                                                                      value=GuiJsonUtil.fetch_kijiku_setting_key_values("num_malformed_batch_retries"),
                                                                                      info="How many times Kijiku will attempt to mend a malformed batch, only for gpt4. Be careful with increasing as cost increases at (cost * length * n) at worst case.",
                                                                                      lines=1,
                                                                                      max_lines=1,
                                                                                      show_label=True,
                                                                                      interactive=True,
                                                                                      elem_id="num_malformed_batch_retries")

                            self.batch_retry_timeout_input_field = gr.Textbox(label='Batch Retry Timeout',
                                                                              value=GuiJsonUtil.fetch_kijiku_setting_key_values("batch_retry_timeout"),
                                                                              info="How long Kijiku will try to translate a batch in seconds, if a requests exceeds this duration, Kijiku will leave it untranslated.",
                                                                              lines=1,
                                                                              max_lines=1,
                                                                              show_label=True,
                                                                              interactive=True,
                                                                              elem_id="batch_retry_timeout")

                            self.num_concurrent_batches_input_field = gr.Textbox(label='Number of Concurrent Batches Allowed',
                                                                                value=GuiJsonUtil.fetch_kijiku_setting_key_values("num_concurrent_batches"),
                                                                                info="How many translations batches Kijiku will send to OpenAI at a time.",
                                                                                lines=1,
                                                                                max_lines=1,
                                                                                show_label=True,
                                                                                interactive=True,
                                                                                elem_id="num_concurrent_batches")

                    with gr.Row():
                        gr.Markdown("(stream, logit_bias, stop and n are included for legacy purposes, current versions of Kudasai will hardcode their values when validating the Kijiku_rule.json to their default values.)")

                    with gr.Row():
                        self.apply_changes_button = gr.Button('Apply Changes')
                        self.discard_changes_button = gr.Button('Discard Changes', variant='stop')

                ## tab 7 | Logging
                with gr.Tab("Logging") as self.logging_tab:

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

            def webgui_update_check() -> None:

                """
                
                Checks for if a Kudasai update is available.

                """

                Kudasai.connection, update_prompt = Toolkit.check_update()

                if(update_prompt != ""):
                    gr.Info("Update available, see https://github.com/Bikatr7/Kudasai/releases/latest/ for more information.")

##-------------------start-of-indexing_run_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
                    
            def indexing_run_button_click(input_txt_file:gr.File, input_json_file_preprocessing:gr.File, knowledge_base_file:str, knowledge_base_directory:typing.List[str]) -> typing.Tuple[str, str, str, str]:
                    
                """
                
                Runs the indexing and displays the results in the indexing output field. If no txt file is selected, an error is raised. If no json file is selected, an error is raised. If no knowledge base file is selected, an error is raised.
                Knowledge base file or directory must be selected, but not both.
                Also displays the indexing results, and the debug log.

                Parameters:
                input_txt_file (gr.File) : The input txt file.
                input_json_file_preprocessing (gr.File) : The input json file.
                knowledge_base_file (gr.File) : The knowledge base file.
                knowledge_base_directory (gr.File) : The knowledge base directory.

                Returns:
                indexed_text (str) : The indexed text.
                indexing_log (str) : The indexing log.
                log_text (str) : The log text for the Indexing tab.
                log_text (str) : The log text for the log tab.

                """

                if(input_txt_file is not None):

                    if(input_json_file_preprocessing is not None):

                        ## must be one, but not both
                        if(knowledge_base_file is not None or knowledge_base_directory is not None) and not (knowledge_base_file is not None and knowledge_base_directory is not None):


                            ## looks like file will just be the file path
                            ## but directory will be a list of file paths, I can't think of a workaround right now, so will have to update kairyou to accept a list of file paths. 
                            ## wait nvm im a genius, let's just read all the files and concatenate them into one string lmfao

                            knowledge_base_paths = []
                            knowledge_base_string = ""

                            text_to_index = gui_get_text_from_file(input_txt_file)
                            replacements = gui_get_json_from_file(input_json_file_preprocessing)

                            if(knowledge_base_file is not None):
                                knowledge_base_paths.append(knowledge_base_file)

                            else:
                                knowledge_base_paths = [file for file in knowledge_base_directory]

                            for file in knowledge_base_paths:
                                knowledge_base_string += gui_get_text_from_file(file)

                            gr.Info("Indexing takes a while, please be patient.")

                            unique_names, indexing_log = Indexer.index(text_to_index, knowledge_base_string, replacements)

                            ## Indexer does not directly log anything, in case of anything else touching it, we will grab the log from the log file
                            log_text = FileEnsurer.standard_read_file(Logger.log_file_path)

                            indexed_text = Kudasai.mark_indexed_names(text_to_index, unique_names)

                            return indexed_text, indexing_log, log_text, log_text

                        else:
                            raise gr.Error("No knowledge base file or directory selected")
                    
                    else:
                        raise gr.Error("No JSON file selected")
                    
                else:
                    raise gr.Error("No TXT file selected")

##-------------------start-of-preprocessing_run_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            def preprocessing_run_button_click(input_txt_file:gr.File, input_json_file_preprocessing:gr.File, input_text:str) -> typing.Tuple[str, str, str, str]:

                """

                Runs the preprocessing and displays the results in the preprocessing output field. If no txt file is selected, an error is raised. If no json file is selected, an error is raised.
                Also displays the preprocessing results, and the debug log.

                Parameters:
                input_txt_file (gr.File) : The input txt file.
                input_json_file_preprocessing (gr.File) : The input json file.

                Returns:
                text_to_preprocess (str) : The preprocessed text.
                preprocessing_log (str) : The preprocessing log.
                log_text (str) : The log text for the Kairyou tab.
                log_text (str) : The log text for the log tab.

                """

                if(input_txt_file == None and input_text == ""):
                    raise gr.Error("No TXT file selected and no text input")

                if(input_json_file_preprocessing is not None):

                    if(input_txt_file is not None):
                        text_to_preprocess = gui_get_text_from_file(input_txt_file)

                    else:
                        text_to_preprocess = input_text

                    replacements = gui_get_json_from_file(input_json_file_preprocessing)

                    preprocessed_text, preprocessing_log, error_log =  Kairyou.preprocess(text_to_preprocess, replacements)

                    timestamp = Toolkit.get_timestamp(is_archival=True)

                    FileEnsurer.write_kairyou_results(preprocessed_text, preprocessing_log, error_log, timestamp)

                    log_text = FileEnsurer.standard_read_file(Logger.log_file_path)

                    return preprocessed_text, preprocessing_log, log_text, log_text
            
                else:
                    raise gr.Error("No JSON file selected")
                
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
                je_check_text (str) : The je check text.
                log_text (str) : The log text for the Log tab.

                """

                if(Kudasai.connection == False):
                    raise gr.Error("No internet connection detected, please connect to the internet to use translation features of Kudasai.")

                ## in case of subsequent runs, we need to reset the static variables
                Kaiseki.reset_static_variables()

                ## start of translation, so we can assume that that we don't want to interrupt it
                FileEnsurer.do_interrupt = False

                ## if translate button is clicked, we can assume that the translation is ongoing
                self.is_translation_ongoing = True
                
                if(input_txt_file is None and input_text == ""):
                    raise gr.Error("No TXT file or text selected")
                
                if(api_key_input == ""):
                    raise gr.Error("No API key provided")
                
                if(input_txt_file is not None):
                    text_to_translate = gui_get_text_from_file(input_txt_file)

                else:
                    text_to_translate = input_text

                try:
                    DeepLService.set_api_key(str(api_key_input))

                    is_valid, e = DeepLService.test_api_key_validity()

                    if(is_valid == False and e is not None):
                        raise e

                except:
                    raise gr.Error("Invalid API key")
                
                Kaiseki.text_to_translate  = [line for line in str(text_to_translate).splitlines()]

                Kaiseki.commence_translation()

                Kaiseki.write_kaiseki_results()

                ## je check text and translated text are lists of strings, so we need to convert them to strings
                translated_text = "\n".join(Kaiseki.translated_text)
                je_check_text = "\n".join(Kaiseki.je_check_text)

                ## Log text is cleared from the client, so we need to get it from the log file
                log_text = FileEnsurer.standard_read_file(Logger.log_file_path)

                ## also gonna want to update the api key file with the new api key
                FileEnsurer.standard_overwrite_file(FileEnsurer.deepl_api_key_path, base64.b64encode(str(api_key_input).encode('utf-8')).decode('utf-8'), omit=True)

                return translated_text, je_check_text, log_text
            
##-------------------start-of-kijiku_translate_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            async def kijiku_translate_button_click(input_txt_file:gr.File, input_text:gr.Textbox, api_key_input:gr.Textbox) -> typing.Tuple[str, str, str]:

                """
                
                Translates the text in the input_txt_file or input_text using the OpenAI API. If no txt file or text is selected, an error is raised. If no API key is provided or the API key is invalid, an error is raised.
                Displays the translated text, and the debug log.

                Parameters:
                input_txt_file (gr.File) : The input txt file.
                input_text (gr.Textbox) : The input text.
                api_key_input (gr.Textbox) : The API key input.

                Returns:
                translated_text (str) : The translated text.
                je_check_text (str) : The je check text.
                log_text (str) : The log text for the Log tab.
                
                """

                if(Kudasai.connection == False):
                    raise gr.Error("No internet connection detected, please connect to the internet to use translation features of Kudasai.")

                ## in case of subsequent runs, we need to reset the static variables
                Kijiku.reset_static_variables()

                ## start of translation, so we can assume that that we don't want to interrupt it
                FileEnsurer.do_interrupt = False

                ## if translate button is clicked, we can assume that the translation is ongoing
                self.is_translation_ongoing = True

                ## first, set the json in the json handler to the json currently set as in gui_json_util
                JsonHandler.current_kijiku_rules = GuiJsonUtil.current_kijiku_rules

                ## due to the bug with the settings need to validate json again.
                ## bug has been resolved, but we'll keep this here just in case
                try:
                    JsonHandler.validate_json()

                except:
                    raise gr.Error("Issue with Kijiku settings detected, please look at the settings tab and ensure all values are valid. This is a known bug, and will be hopefully fixed in the future.")

                ## next api key
                try:
                    OpenAIService.set_api_key(str(api_key_input))

                    is_valid, e = await OpenAIService.test_api_key_validity()

                    if(is_valid == False and e is not None):
                        raise e

                except:
                    raise gr.Error("Invalid API key")
                
                ## setup text to translate
                if(input_txt_file is None and input_text == ""):
                    raise gr.Error("No TXT file or text selected")
                
                if(input_txt_file is not None):
                    text_to_translate = gui_get_text_from_file(input_txt_file)
                
                else:
                    text_to_translate = input_text

                ## need to convert to list of strings
                Kijiku.text_to_translate = [line for line in str(text_to_translate).splitlines()]

                ## commence translation
                await Kijiku.commence_translation(is_webgui=True)
                Kijiku.write_kijiku_results()

                ## je check text and translated text are lists of strings, so we need to convert them to strings
                translated_text = "\n".join(Kijiku.translated_text)
                je_check_text = "\n".join(Kijiku.je_check_text)

                ## Log text is cleared from the client, so we need to get it from the log file
                log_text = FileEnsurer.standard_read_file(Logger.log_file_path)

                ## also gonna want to update the api key file with the new api key
                FileEnsurer.standard_overwrite_file(FileEnsurer.openai_api_key_path, base64.b64encode(str(api_key_input).encode('utf-8')).decode('utf-8'), omit=True)

                return translated_text, je_check_text, log_text
            
##-------------------start-of-kijiku_calculate_costs_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            def kijiku_calculate_costs_button_click(input_txt_file:gr.File, input_text:gr.Textbox) -> str:


                """
                
                Calculates the cost of the text in the input_txt_file or input_text using the OpenAI API. If no txt file or text is selected, an error is raised.
                Displays the cost, and the debug log.

                Parameters:
                input_txt_file (gr.File) : The input txt file.
                input_text (gr.Textbox) : The input text.

                Returns:
                cost_estimation (str) : The cost estimation formatted as a string.
                
                """

                model = GuiJsonUtil.fetch_kijiku_setting_key_values("model")

                if(input_txt_file is None and input_text == ""):
                    raise gr.Error("No TXT file or text selected")
                
                if(input_txt_file is not None):
                    text_to_translate = gui_get_text_from_file(input_txt_file)

                else:
                    text_to_translate = input_text

                ## need to convert to list of strings
                Kijiku.text_to_translate = [line for line in str(text_to_translate).splitlines()]

                num_tokens, estimated_cost, model = Kijiku.estimate_cost(model)

                cost_estimation = "Estimated number of tokens : " + str(num_tokens) + "\n" + "Estimated minimum cost : " + str(estimated_cost) + " USD"
                
                gr.Info(cost_estimation)

                return cost_estimation
            
##-------------------start-of-indexing_clear_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            def indexing_clear_button_click() -> typing.Tuple[None, None, None, None, str, str, str]:


                """

                Clears all fields on the indexing tab. As well as the input fields.

                Returns:
                input_txt_file_indexing (gr.File) : An empty file.
                input_json_file_indexing (gr.File) : An empty file.
                knowledge_base_file (gr.File) : An empty file.
                indexing_output_field (str) : An empty string.
                indexing_results_output_field (str) : An empty string.
                debug_log_output_field_indexing_tab (str) : An empty string.

                """

                input_txt_file_indexing = None
                input_json_file_indexing = None
                knowledge_base_file = None
                knowledge_base_directory = None

                indexing_output_field = ""
                indexing_results_output_field = ""
                debug_log_output_field_indexing_tab = ""

                return input_txt_file_indexing, input_json_file_indexing, knowledge_base_file, knowledge_base_directory, indexing_output_field, indexing_results_output_field, debug_log_output_field_indexing_tab

##-------------------start-of-preprocessing_clear_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------                

            def preprocessing_clear_button_click() -> typing.Tuple[None, None, str, str, str, str]:

                """

                Clears all fields on the preprocessing tab. As well as the input fields.

                Returns:
                input_txt_file (gr.File) : An empty file.
                input_json_file_preprocessing (gr.File) : An empty file.
                preprocess_output_field (str) : An empty string.
                preprocessing_results_output_field (str) : An empty string.
                debug_log_output_field_preprocess_tab (str) : An empty string.

                """

                input_txt_file = None
                input_json_file_preprocessing = None

                input_text = ""
                preprocess_output_field = ""
                preprocessing_results_output_field = ""
                debug_log_output_field_preprocess_tab = ""

                return input_txt_file, input_json_file_preprocessing, input_text, preprocess_output_field, preprocessing_results_output_field, debug_log_output_field_preprocess_tab
            
##-------------------start-of-kaiseki_run_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            def kaiseki_clear_button_click() -> typing.Tuple[None, str, str, str, str]:

                """
                
                Clears all fields on the Kaiseki tab. As well as the input fields.

                Returns:
                input_txt_file_kaiseki (gr.File) : An empty file.
                input_text_kaiseki (str) : An empty string.
                output_field_kaiseki (str) : An empty string.
                je_check_text_field_kaiseki (str) : An empty string.
                debug_log_output_field_kaiseki_tab (str) : An empty string.

                """

                ## if clear button is clicked, we can assume that the translation is over, or that the user wants to cancel the translation
                self.is_translation_ongoing = False

                ## Same as above, we can assume that the user wants to cancel the translation
                FileEnsurer.do_interrupt = True
                
                input_file_kaiseki = None

                input_text_kaiseki = ""

                output_field_kaiseki = ""
                je_check_text_field_kaiseki = ""
                debug_log_output_field_kaiseki_tab = ""

                return input_file_kaiseki, input_text_kaiseki, output_field_kaiseki, je_check_text_field_kaiseki, debug_log_output_field_kaiseki_tab
            
##-------------------start-of-kijiku_clear_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            def kijiku_clear_button_click() -> typing.Tuple[None, str, gr.File, str, str, str]:

                """
                
                Clears all fields on the Kijiku tab. As well as the input fields.

                Returns:
                input_txt_file_kijiku (gr.File) : An empty file.
                input_text_kijiku (str) : An empty string.
                kijiku_translated_text_output_field (str) : An empty string.
                je_check_text_field_kijiku (str) : An empty string.
                debug_log_output_field_kijiku_tab (str) : An empty string.

                """

                ## if clear button is clicked, we can assume that the translation is over, or that the user wants to cancel the translation
                self.is_translation_ongoing = False

                ## Same as above, we can assume that the user wants to cancel the translation
                FileEnsurer.do_interrupt = True

                input_file_kijiku = None

                input_text_kijiku = ""

                ## Also gonna want to reset the json input field to the default json file
                input_kijiku_rules_file = gr.File(value = FileEnsurer.config_kijiku_rules_path, label='Kijiku Rules File', file_count='single', file_types=['.json'], type='filepath')

                kijiku_translated_text_output_field = ""
                je_check_text_field_kijiku = ""
                debug_log_output_field_kijiku_tab = ""

                return input_file_kijiku, input_text_kijiku, input_kijiku_rules_file, kijiku_translated_text_output_field, je_check_text_field_kijiku, debug_log_output_field_kijiku_tab
            
##-------------------start-of-clear_log_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        
            def clear_log_button_click() -> typing.Tuple[str, str]:

                """

                Clears the logs on the log tab.

                Returns:
                debug_log_output_field_log_tab (str) : An empty string.
                error_log (str) : An empty string.

                """

                debug_log_output_field_log_tab = ""
                error_log = ""

                return debug_log_output_field_log_tab, error_log

##-------------------start-of-apply_new_kijiku_settings()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            def apply_new_kijiku_settings(input_kijiku_rules_file:gr.File,
                                        model:str,
                                        system_message:str,
                                        temperature:str,
                                        top_p:str,
                                        n:str,
                                        stream:str, 
                                        stop:str, 
                                        logit_bias:str, 
                                        max_tokens:str, 
                                        presence_penalty:str, 
                                        frequency_penalty:str, 
                                        message_mode:str, 
                                        num_lines:str,
                                        sentence_fragmenter_mode:str,
                                        je_check_mode:str,
                                        num_malformed_batch:str,
                                        batch_retry_timeout:str,
                                        num_concurrent_batches:str) -> None:
                
                """

                Applies the new kijiku settings to the uploaded kijiku rules file.

                Parameters:
                input_kijiku_rules_file (gr.File) : The input kijiku rules file.
                model (str) : The model.
                system_message (str) : The system message.
                temperature (str) : The temperature.
                top_p (str) : The top p.
                n (str) : The n.
                stream (str) : The stream.
                stop (str) : The stop.
                logit_bias (str) : The logit bias.
                max_tokens (str) : The max tokens.
                presence_penalty (str) : The presence penalty.
                frequency_penalty (str) : The frequency penalty.
                message_mode (str) : The message mode.
                num_lines (str) : The number of lines.
                sentence_fragmenter_mode (str) : The sentence fragmenter mode.
                je_check_mode (str) : The je check mode.
                num_malformed_batch (str) : The number of malformed batch retries.
                batch_retry_timeout (str) : The batch retry timeout.
                num_concurrent_batches (str) : The number of concurrent batches.


                """

                if(input_kijiku_rules_file is None):
                    raise gr.Error("No Kijiku Rules File Selected. Cannot apply settings.")

                ## build the new kijiku settings list so we can create a key-value pair list
                settings_list = [model, 
                                system_message, 
                                temperature, 
                                top_p, 
                                n, 
                                stream, 
                                stop, 
                                logit_bias, 
                                max_tokens, 
                                presence_penalty, 
                                frequency_penalty, 
                                message_mode, 
                                num_lines,
                                sentence_fragmenter_mode,
                                je_check_mode,
                                num_malformed_batch,
                                batch_retry_timeout,
                                num_concurrent_batches]
                
                ## create the new key-value pair list
                new_key_value_tuple_pairs = create_new_key_value_tuple_pairs(settings_list)

                try:
                    ## and then have the GuiJsonUtil apply the new kijiku settings
                    GuiJsonUtil.update_kijiku_settings_with_new_values(input_kijiku_rules_file, new_key_value_tuple_pairs)

                except:
                    raise gr.Error("Invalid Kijiku Settings")

                gr.Info("Kijiku Settings Applied")
            
##-------------------start-of-refresh_kijiku_settings_fields()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            def refresh_kijiku_settings_fields(input_kijiku_rules_file:gr.File) -> typing.Tuple[str, str, float, float, str, str, str, str, str, float, float, int, str, int, int, str, str, str]:

                """
                
                Refreshes the kijiku settings fields with the values from the kijiku rules file.

                Parameters:
                input_kijiku_rules_file (gr.File) : The input kijiku rules file.

                Returns:
                model_input_field_value (str) : The new model input field value.
                system_message_input_field_value (str) : The new system message input field value.
                temperature_input_field_value (float) : The new temperature input field value.
                top_p_input_field_value (float) : The new top p input field value.
                n_input_field_value (str) : The new n input field value.
                stream_input_field_value (str) : The new stream input field value.
                stop_input_field_value (str) : The new stop input field value.
                logit_bias_input_field_value (str) : The new logit bias input field value.
                max_tokens_input_field_value (str) : The new max tokens input field value.
                presence_penalty_input_field_value (float) : The new presence penalty input field value.
                frequency_penalty_input_field_value (float) : The new frequency penalty input field value.
                message_mode_input_field_value (int) : The new message mode input field value.
                num_lines_input_field_value (str) : The new num lines input field value.
                sentence_fragmenter_mode_input_field_value (int) : The new sentence fragmenter mode input field value.
                je_check_mode_input_field_value (int) : The new je check mode input field value.
                num_malformed_batch_retries_input_field_value (str) : The new num malformed batch retries input field value.
                batch_retry_timeout_input_field_value (str) : The new batch retry timeout input field value.
                num_concurrent_batches_input_field_value (str) : The new num concurrent batches input field value.

                """


                if(input_kijiku_rules_file is None):
                    raise gr.Error("No Kijiku Rules File Selected. Cannot refresh settings.")

                ## assume that the user has uploaded a valid kijiku rules file, if it's not, that's on them
                try:
                    GuiJsonUtil.current_kijiku_rules = gui_get_json_from_file(input_kijiku_rules_file)

                    ## update the default values on the Kijiku Settings tab manually
                    model_input_field_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("model"))
                    system_message_input_field_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("system_message"))
                    temperature_input_field_value = float(GuiJsonUtil.fetch_kijiku_setting_key_values("temp"))
                    top_p_input_field_value = float(GuiJsonUtil.fetch_kijiku_setting_key_values("top_p"))
                    n_input_field_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("n"))
                    stream_input_field_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("stream"))
                    stop_input_field_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("stop"))
                    logit_bias_input_field_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("logit_bias"))
                    max_tokens_input_field_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("max_tokens"))
                    presence_penalty_input_field_value = float(GuiJsonUtil.fetch_kijiku_setting_key_values("presence_penalty"))
                    frequency_penalty_input_field_value = float(GuiJsonUtil.fetch_kijiku_setting_key_values("frequency_penalty"))
                    message_mode_input_field_value = int(GuiJsonUtil.fetch_kijiku_setting_key_values("message_mode")) 
                    num_lines_input_field_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("num_lines"))
                    sentence_fragmenter_mode_input_field_value = int(GuiJsonUtil.fetch_kijiku_setting_key_values("sentence_fragmenter_mode"))
                    je_check_mode_input_field_value = int(GuiJsonUtil.fetch_kijiku_setting_key_values("je_check_mode"))
                    num_malformed_batch_retries_input_field_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("num_malformed_batch_retries"))
                    batch_retry_timeout_input_field_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("batch_retry_timeout"))
                    num_concurrent_batches_input_field_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("num_concurrent_batches"))

                except:

                    GuiJsonUtil.current_kijiku_rules = JsonHandler.current_kijiku_rules
                    raise gr.Error("Invalid Custom Kijiku Rules File")
                
                return model_input_field_value, system_message_input_field_value, temperature_input_field_value, top_p_input_field_value, n_input_field_value, stream_input_field_value, stop_input_field_value, logit_bias_input_field_value, max_tokens_input_field_value, presence_penalty_input_field_value, frequency_penalty_input_field_value, message_mode_input_field_value, num_lines_input_field_value, sentence_fragmenter_mode_input_field_value, je_check_mode_input_field_value, num_malformed_batch_retries_input_field_value, batch_retry_timeout_input_field_value, num_concurrent_batches_input_field_value
            
##-------------------start-of-clear_kijiku_settings_input_fields()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        
            def clear_kijiku_settings_input_fields() -> typing.Tuple[None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]:                                                                     

                """

                Resets the kijiku settings input fields to None.

                """

                model_input_field_value = None
                system_message_input_field_value = None
                temperature_input_field_value = None
                top_p_input_field_value = None
                n_input_field_value = None
                stream_input_field_value = None
                stop_input_field_value = None
                logit_bias_input_field_value = None
                max_tokens_input_field_value = None
                presence_penalty_input_field_value = None
                frequency_penalty_input_field_value = None
                message_mode_input_field_value = None
                num_lines_input_field_value = None
                sentence_fragmenter_mode_input_field_value = None
                je_check_mode_input_field_value = None
                num_malformed_batch_retries_input_field_value = None
                batch_retry_timeout_input_field_value = None
                num_concurrent_batches_input_field_value = None

                return model_input_field_value, system_message_input_field_value, temperature_input_field_value, top_p_input_field_value, n_input_field_value, stream_input_field_value, stop_input_field_value, logit_bias_input_field_value, max_tokens_input_field_value, presence_penalty_input_field_value, frequency_penalty_input_field_value, message_mode_input_field_value, num_lines_input_field_value, sentence_fragmenter_mode_input_field_value, je_check_mode_input_field_value, num_malformed_batch_retries_input_field_value, batch_retry_timeout_input_field_value, num_concurrent_batches_input_field_value

##-------------------start-of-fetch_log_content()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            def fetch_debug_log_content() -> typing.Tuple[str, str]:
            
                """
                
                Fetches the log content from the log file.

                Returns:
                log_text (str) : The log text.
                error_log (str) : The error log.

                """

                log_text = FileEnsurer.standard_read_file(Logger.log_file_path)
                error_log = FileEnsurer.standard_read_file(FileEnsurer.error_log_path)

                return log_text, error_log
            
##-------------------start-of-send_to_kairyou()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            def send_to_kairyou(input_text:str) -> str:

                """
                
                Sends the indexed text to Kairyou.

                Parameters:
                input_text (str) : The input text.

                Returns:
                input_text (str) : The input text.

                """

                if(input_text == ""):
                    gr.Warning("No indexed text to send to Kairyou")
                    return ""
                
                else:
                    gr.Info("Indexed text copied to Kairyou")
                    return input_text
                
##-------------------start-of-send_to_kaiseki()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
                
            def send_to_kaiseki(input_text:str) -> str:

                """"
                
                Sends the preprocessed text to Kaiseki.

                Parameters:
                input_text (str) : The input text.

                Returns:
                input_text (str) : The input text.

                """

                if(input_text == ""):
                    gr.Warning("No preprocessed text to send to Kaiseki")
                    return ""
                
                else:
                    gr.Info("Preprocessed text copied to Kaiseki")
                    return input_text
                
##-------------------start-of-send_to_kijiku()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
                
            def send_to_kijiku(input_text:str) -> str:

                """
                
                Sends the preprocessed text to Kijiku.

                Parameters:
                input_text (str) : The input text.

                Returns:
                input_text (str) : The input text.

                """

                if(input_text == ""):
                    gr.Warning("No preprocessed text to send to Kijiku")
                    return ""
                
                else:
                    gr.Info("Preprocessed text copied to Kijiku")
                    return input_text

##-------------------start-of-Listener-Declaration---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

##-------------------start-of-load()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.gui.load(webgui_update_check)

##-------------------start-of-indexing_run_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.indexing_run_button.click(indexing_run_button_click,
                                            inputs=[
                                                self.input_txt_file_indexing, ## input txt file to index
                                                self.input_json_file_indexing, ## input json file
                                                self.knowledge_base_file, ## knowledge base file
                                                self.knowledge_base_directory], ## knowledge base directory

                                            outputs=[
                                                self.indexing_output_field, ## indexed text
                                                self.indexing_results_output_field, ## indexing results
                                                self.debug_log_output_field_indexing_tab, ## debug log on indexing tab
                                                self.debug_log_output_field_log_tab]) ## debug log on log tab


##-------------------start-of-preprocessing_run_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.preprocessing_run_button.click(fn=preprocessing_run_button_click, 
                                                inputs=[
                                                    self.input_txt_file_preprocessing, ## input txt file to preprocess
                                                    self.input_json_file_preprocessing, ## replacements json file
                                                    self.input_text_kairyou], ## input text to preprocess                                                                        

                                                outputs=[
                                                    self.preprocess_output_field,  ## preprocessed text
                                                    self.preprocessing_results_output_field,  ## kairyou results
                                                    self.debug_log_output_field_preprocess_tab, ## debug log on preprocess tab
                                                    self.debug_log_output_field_log_tab]) ## debug log on log tab

##-------------------start-of-kaiseki_translate_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            ## for the actual translation, and the je check text
            kaiseki_translation_process = self.translate_button_kaiseki.click(kaiseki_translate_button_click,
                                                inputs=[
                                                    self.input_txt_file_kaiseki, ## input txt file to translate
                                                    self.input_text_kaiseki, ## input text to translate
                                                    self.kaiseki_api_key_input], ## api key input
                                                
                                                outputs=[
                                                    self.output_field_kaiseki, ## translated text
                                                    self.kaiseki_je_check_text_field, ## je check text field on kaiseki tab
                                                    self.debug_log_output_field_log_tab]) ## debug log on log tab
            ## for the kaiseki debug log
            self.translate_button_kaiseki.click(fn=fetch_log_content,
                                                inputs=[],

                                                outputs=[self.debug_log_output_field_kaiseki_tab], ## debug log on kaiseki tab

                                                every=.1) ## update every 100ms
            

##-------------------start-of-kijiku_translate_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            ## for the actual translation, and the je check text
            kijiku_translation_process = self.translate_button_kijiku.click(kijiku_translate_button_click,
                                                inputs=[
                                                    self.input_txt_file_kijiku, ## input txt file to translate
                                                    self.input_text_kijiku, ## input text to translate
                                                    self.kijiku_api_key_input], ## api key input
                                                
                                                outputs=[
                                                    self.kijiku_translated_text_output_field, ## translated text
                                                    self.kijiku_je_check_text_field, ## je check text field on kijiku tab
                                                    self.debug_log_output_field_log_tab])
            ## for the kijiku debug log
            self.translate_button_kijiku.click(fn=fetch_log_content,
                                                inputs=[],

                                                outputs=[self.debug_log_output_field_kijiku_tab], ## debug log on kijiku tab

                                                every=.1) ## update every 100ms
            

##-------------------start-of-kijiku_calculate_costs_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            self.calculate_costs_button_kijiku.click(kijiku_calculate_costs_button_click,
                                                        inputs=[
                                                            self.input_txt_file_kijiku, ## input txt file to calculate costs
                                                            self.input_text_kijiku], ## input text to calculate costs
                
                                                        outputs=[self.kijiku_translated_text_output_field]) ## functions as an output field for the cost output field
            
##-------------------start-of-indexing_clear_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.indexing_clear_button.click(indexing_clear_button_click,
                                            inputs=[],
                                            
                                            outputs=[
                                                self.input_txt_file_indexing, ## input txt file
                                                self.input_json_file_indexing, ## input json file
                                                self.knowledge_base_file, ## knowledge base file
                                                self.knowledge_base_directory, ## knowledge base directory
                                                self.indexing_output_field, ## indexing output field
                                                self.indexing_results_output_field, ## indexing results output field
                                                self.debug_log_output_field_indexing_tab]) ## debug log on indexing tab
            
##-------------------start-of-preprocessing_clear_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.preprocessing_clear_button.click(preprocessing_clear_button_click,
                                                  inputs=[],

                                                  outputs=[
                                                      self.input_txt_file_preprocessing, ## input txt file
                                                      self.input_json_file_preprocessing, ## input json file
                                                      self.input_text_kairyou, ## input text
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
                                                self.kaiseki_je_check_text_field, ## je check text field on kaiseki tab
                                                self.debug_log_output_field_kaiseki_tab], ## debug log on kaiseki tab

                                            cancels=kaiseki_translation_process) ## cancels the translation process
##-------------------start-of-clear_button_kijiku_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            self.clear_button_kijiku.click(kijiku_clear_button_click,
                                            inputs=[],

                                            outputs=[
                                                self.input_txt_file_kijiku, ## input txt file
                                                self.input_text_kijiku, ## input text
                                                self.input_kijiku_rules_file, ## kijiku rules file
                                                self.kijiku_translated_text_output_field, ## translation output field
                                                self.kijiku_je_check_text_field, ## je check text field on kijiku tab
                                                self.debug_log_output_field_kijiku_tab], ## debug log on kijiku tab
            
                                            cancels=kijiku_translation_process)
##-------------------start-of-clear_log_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.clear_log_button.click(clear_log_button_click,
                                        inputs=[],

                                        outputs=[
                                            self.debug_log_output_field_log_tab,
                                            self.error_log])
            
##-------------------start-of-apply_new_kijiku_settings()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            self.apply_changes_button.click(apply_new_kijiku_settings,
                                            inputs=[
                                                self.input_kijiku_rules_file, ## kijiku rules file
                                                self.model_input_field, ## model input field
                                                self.system_message_input_field, ## system message input field
                                                self.temperature_input_field, ## temperature input field
                                                self.top_p_input_field, ## top p input field
                                                self.n_input_field, ## n input field
                                                self.stream_input_field, ## stream input field
                                                self.stop_input_field, ## stop input field
                                                self.logit_bias_input_field, ## logit bias input field
                                                self.max_tokens_input_field, ## max tokens input field
                                                self.presence_penalty_input_field, ## presence penalty input field
                                                self.frequency_penalty_input_field, ## frequency penalty input field
                                                self.message_mode_input_field, ## message mode input field
                                                self.num_lines_input_field, ## num lines input field
                                                self.sentence_fragmenter_mode_input_field, ## sentence fragmenter mode input field
                                                self.je_check_mode_input_field, ## je check mode input field
                                                self.num_malformed_batch_retries_input_field, ## num malformed batch retries input field
                                                self.batch_retry_timeout_input_field, ## batch retry timeout input field
                                                self.num_concurrent_batches_input_field], ## num concurrent batches input field
                                            
                                            outputs=[])

##-------------------start-of-discard_changes_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            self.discard_changes_button.click(refresh_kijiku_settings_fields,
                                              inputs=[self.input_kijiku_rules_file],
                                              
                                              outputs=[
                                                self.model_input_field, ## model input field
                                                self.system_message_input_field, ## system message input field
                                                self.temperature_input_field, ## temperature input field
                                                self.top_p_input_field, ## top p input field
                                                self.n_input_field, ## n input field
                                                self.stream_input_field, ## stream input field
                                                self.stop_input_field, ## stop input field
                                                self.logit_bias_input_field, ## logit bias input field
                                                self.max_tokens_input_field, ## max tokens input field
                                                self.presence_penalty_input_field, ## presence penalty input field
                                                self.frequency_penalty_input_field, ## frequency penalty input field
                                                self.message_mode_input_field, ## message mode input field
                                                self.num_lines_input_field, ## num lines input field
                                                self.sentence_fragmenter_mode_input_field, ## sentence fragmenter mode input field
                                                self.je_check_mode_input_field, ## je check mode input field
                                                self.num_malformed_batch_retries_input_field, ## num malformed batch retries input field
                                                self.batch_retry_timeout_input_field, ## batch retry timeout input field
                                                self.num_concurrent_batches_input_field]) ## num concurrent batches input field


##-------------------start-of-input_kijiku_rules_file_upload()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            self.input_kijiku_rules_file.upload(refresh_kijiku_settings_fields,
                                                inputs=[self.input_kijiku_rules_file],
                                                
                                                outputs=[
                                                    self.model_input_field, ## model input field
                                                    self.system_message_input_field, ## system message input field
                                                    self.temperature_input_field, ## temperature input field
                                                    self.top_p_input_field, ## top p input field
                                                    self.n_input_field, ## n input field
                                                    self.stream_input_field, ## stream input field
                                                    self.stop_input_field, ## stop input field
                                                    self.logit_bias_input_field, ## logit bias input field
                                                    self.max_tokens_input_field, ## max tokens input field
                                                    self.presence_penalty_input_field, ## presence penalty input field
                                                    self.frequency_penalty_input_field, ## frequency penalty input field
                                                    self.message_mode_input_field, ## message mode input field
                                                    self.num_lines_input_field, ## num lines input field
                                                    self.sentence_fragmenter_mode_input_field, ## sentence fragmenter mode input field
                                                    self.je_check_mode_input_field, ## je check mode input field
                                                    self.num_malformed_batch_retries_input_field, ## num malformed batch retries input field
                                                    self.batch_retry_timeout_input_field, ## batch retry timeout input field
                                                    self.num_concurrent_batches_input_field]) ## num concurrent batches input field
            
            self.input_kijiku_rules_file.clear(clear_kijiku_settings_input_fields,
                                                inputs=[],
                                                
                                                outputs=[
                                                    self.model_input_field, ## model input field
                                                    self.system_message_input_field, ## system message input field
                                                    self.temperature_input_field, ## temperature input field
                                                    self.top_p_input_field, ## top p input field
                                                    self.n_input_field, ## n input field
                                                    self.stream_input_field, ## stream input field
                                                    self.stop_input_field, ## stop input field
                                                    self.logit_bias_input_field, ## logit bias input field
                                                    self.max_tokens_input_field, ## max tokens input field
                                                    self.presence_penalty_input_field, ## presence penalty input field
                                                    self.frequency_penalty_input_field, ## frequency penalty input field
                                                    self.message_mode_input_field, ## message mode input field
                                                    self.num_lines_input_field, ## num lines input field
                                                    self.sentence_fragmenter_mode_input_field, ## sentence fragmenter mode input field
                                                    self.je_check_mode_input_field, ## je check mode input field
                                                    self.num_malformed_batch_retries_input_field, ## num malformed batch retries input field
                                                    self.batch_retry_timeout_input_field, ## batch retry timeout input field
                                                    self.num_concurrent_batches_input_field]) ## num concurrent batches input field

##-------------------start-of-logging_tab.select()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.logging_tab.select(fetch_debug_log_content,
                                    inputs=[],
                                    
                                    outputs=[self.debug_log_output_field_log_tab, self.error_log])
            
##-------------------start-of-save_to_file_indexed_text_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            self.save_to_file_indexed_text.click(lambda text: text, ## save text as is
                inputs=[self.indexing_output_field], ## input text to save

                outputs=[], ## no outputs

                ## javascript code that allows us to save textbox contents to a file
                js=(self.save_as_js).replace("downloaded_text.txt", "indexed_text.txt")
            )

##-------------------start-of-save_to_file_indexing_results_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            self.save_to_file_indexing_results.click(lambda text: text, ## save text as is
                inputs=[self.indexing_results_output_field], ## input text to save

                outputs=[], ## no outputs

                ## javascript code that allows us to save textbox contents to a file
                js=(self.save_as_js).replace("downloaded_text.txt", "indexing_results.txt")
            )

##-------------------start-of-save_to_file_indexing_debug_log_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            self.save_to_file_debug_log_indexing_tab.click(lambda text: text, ## save text as is
                inputs=[self.debug_log_output_field_indexing_tab], ## input text to save

                outputs=[], ## no outputs

                ## javascript code that allows us to save textbox contents to a file
                js=(self.save_as_js).replace("downloaded_text.txt", "indexing_debug_log.txt")
            )
            
##-------------------start-of-save_to_file_preprocessing_results_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.save_to_file_preprocessed_text.click(lambda text: text, ## save text as is
                inputs=[self.preprocess_output_field],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                js=(self.save_as_js).replace("downloaded_text.txt", "preprocessed_text.txt")
            )
            
##-------------------start-of-save_to_file_preprocessing_results_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.save_to_file_preprocessing_results.click(lambda text: text, ## save text as is
                inputs=[self.preprocessing_results_output_field],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                js=(self.save_as_js).replace("downloaded_text.txt", "preprocessing_results.txt")
            )

##-------------------start-of-save_to_file_debug_log_processing_tab_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.save_to_file_debug_log_preprocessing_tab.click(lambda text: text, ## save text as is
                inputs=[self.debug_log_output_field_preprocess_tab],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                js=(self.save_as_js).replace("downloaded_text.txt", "processing_debug_log.txt")
            )

##-------------------start-of-save_to_file_kaiseki_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.save_to_file_kaiseki.click(lambda text: text, ## save text as is
                inputs=[self.output_field_kaiseki],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                js=(self.save_as_js).replace("downloaded_text.txt", "translated_text.txt")
            )

##-------------------start-of-save_to_file_je_check_text_kaiseki_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.save_to_file_je_check_text_kaiseki.click(lambda text: text, ## save text as is
                inputs=[self.kaiseki_je_check_text_field],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                js=(self.save_as_js).replace("downloaded_text.txt", "je_check_text.txt")
            )

##-------------------start-of-save_to_file_debug_log_kaiseki_tab_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.save_to_file_debug_log_kaiseki_tab.click(lambda text: text, ## save text as is
                inputs=[self.debug_log_output_field_kaiseki_tab],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                js=(self.save_as_js).replace("downloaded_text.txt", "debug_log.txt")
            )

##-------------------start-of-save_to_file_kijiku_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            self.save_to_file_kijiku.click(lambda text: text, ## save text as is
                inputs=[self.kijiku_translated_text_output_field],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                js=(self.save_as_js).replace("downloaded_text.txt", "translated_text.txt")
            )

##-------------------start-of-save_to_file_je_check_text_kijiku_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            self.save_to_file_je_check_text_kijiku.click(lambda text: text, ## save text as is
                inputs=[self.kijiku_je_check_text_field],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                js=(self.save_as_js).replace("downloaded_text.txt", "je_check_text.txt")
            )

##-------------------start-of-save_to_file_debug_log_kijiku_tab_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            self.save_to_file_debug_log_kijiku_tab.click(lambda text: text, ## save text as is
                inputs=[self.debug_log_output_field_kijiku_tab],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                js=(self.save_as_js).replace("downloaded_text.txt", "debug_log.txt")
            )

##-------------------start-of-save_to_file_debug_log_logging_tab_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.save_to_file_debug_log_logging_tab.click(lambda text: text, ## save text as is
                inputs=[self.debug_log_output_field_log_tab],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                js=(self.save_as_js).replace("downloaded_text.txt", "debug_log_all.txt")
            )

##-------------------start-of-save_to_file_error_log_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.save_to_file_error_log.click(lambda text: text, ## save text as is
                inputs=[self.error_log],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                js=(self.save_as_js).replace("downloaded_text.txt", "error_log.txt")
            )

##-------------------start-of-send_to_x_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.send_to_kairyou.click(fn=send_to_kairyou, 
                                        inputs=[self.indexing_output_field],
                                        outputs=[self.input_text_kairyou])
                                        
            self.send_to_kaiseki.click(fn=send_to_kaiseki,
                                        inputs=[self.preprocess_output_field],
                                        outputs=[self.input_text_kaiseki])
            
            self.send_to_kijiku.click(fn=send_to_kijiku,
                                        inputs=[self.preprocess_output_field],
                                        outputs=[self.input_text_kijiku])

##-------------------start-of-launch()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------                

    def launch(self):

        """

        Launches the GUI.

        """

        Kudasai.boot()

        GuiJsonUtil.current_kijiku_rules = JsonHandler.current_kijiku_rules

        self.build_gui()
        self.gui.queue().launch(inbrowser=True, show_error=True, show_api=False, favicon_path=FileEnsurer.favicon_path)

##-------------------start-of-main()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

if(__name__ == '__main__'):

    try:

        kudasai_gui = KudasaiGUI()
        kudasai_gui.launch()

        Logger.push_batch()

    except Exception as e:

        FileEnsurer.handle_critical_exception(e)
