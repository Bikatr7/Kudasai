## built-in libraries
import typing
import base64

## third-party libraries
import gradio as gr

from kairyou import Indexer
from kairyou import Kairyou
from kairyou import InvalidReplacementJsonKeys

from easytl import EasyTL, ALLOWED_GEMINI_MODELS, ALLOWED_OPENAI_MODELS

## custom modules
from modules.common.toolkit import Toolkit
from modules.common.logger import Logger
from modules.common.file_ensurer import FileEnsurer

from modules.gui.gui_file_util import gui_get_text_from_file, gui_get_json_from_file
from modules.gui.gui_json_util import GuiJsonUtil

from handlers.json_handler import JsonHandler

from models.kaiseki import Kaiseki
from models.kijiku import Kijiku

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
                
##-------------------start-of-get_saved_openai_api_key()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
                
            def get_saved_openai_api_key() -> str:

                """
                
                Gets the saved openai api key from the config folder, if it exists.

                Returns:
                api_key (str) : The api key.

                """

                try:
                    ## Api key is encoded in base 64 so we need to decode it before returning
                    return base64.b64decode(FileEnsurer.standard_read_file(FileEnsurer.openai_api_key_path).encode('utf-8')).decode('utf-8')
                
                except:
                    return ""
                
##-------------------start-of-get_saved_gemini_api_key()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
                
            def get_saved_gemini_api_key() -> str:

                """
                
                Gets the saved gemini api key from the config folder, if it exists.

                Returns:
                api_key (str) : The api key.

                """

                try:
                    ## Api key is encoded in base 64 so we need to decode it before returning
                    return base64.b64decode(FileEnsurer.standard_read_file(FileEnsurer.gemini_api_key_path).encode('utf-8')).decode('utf-8')
                
                except:
                    return ""
                
##-------------------start-of-set_kijiku_api_key()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
                
            async def set_kijiku_api_key(api_key) -> None:

                """

                Sets the kijiku api key.

                Parameters:
                api_key (str) : The api key.

                """

                ## next api key
                try:
                    if(Kijiku.LLM_TYPE == "openai"):
                        EasyTL.set_api_key(Kijiku.LLM_TYPE, str(api_key))
                        is_valid, e = EasyTL.test_api_key_validity(Kijiku.LLM_TYPE)


                    else:

                        EasyTL.set_api_key(Kijiku.LLM_TYPE, str(api_key))
                        is_valid, e = EasyTL.test_api_key_validity(Kijiku.LLM_TYPE)

                    if(is_valid == False and e is not None):
                        raise e
                    
                except:
                    raise gr.Error("Invalid API key")
                
##-------------------start-of-update_kijiku_api_key()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
                
            def update_kijiku_api_key(api_key) -> None:

                """

                Updates the kijiku api key.

                Parameters:
                api_key (str) : The api key.

                """

                ## also gonna want to update the api key file with the new api key
                if(Kijiku.LLM_TYPE == "openai"):
                    path_to_api_key = FileEnsurer.openai_api_key_path

                else:
                    path_to_api_key = FileEnsurer.gemini_api_key_path

                FileEnsurer.standard_overwrite_file(path_to_api_key, base64.b64encode(str(api_key).encode('utf-8')).decode('utf-8'), omit=True)

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
                    0: "prompt_assembly_mode",
                    1: "number_of_lines_per_batch",
                    2: "sentence_fragmenter_mode",
                    3: "je_check_mode",
                    4: "number_of_malformed_batch_retries",
                    5: "batch_retry_timeout",
                    6: "number_of_concurrent_batches",
                    7: "openai_model",
                    8: "openai_system_message",
                    9: "openai_temperature",
                    10: "openai_top_p",
                    11: "openai_n",
                    12: "openai_stream",
                    13: "openai_stop",
                    14: "openai_logit_bias",
                    15: "openai_max_tokens",
                    16: "openai_presence_penalty",
                    17: "openai_frequency_penalty",
                    18: "gemini_model",
                    19: "gemini_prompt",
                    20: "gemini_temperature",
                    21: "gemini_top_p",
                    22: "gemini_top_k",
                    23: "gemini_candidate_count",
                    24: "gemini_stream",
                    25: "gemini_stop_sequences",
                    26: "gemini_max_output_tokens"
                }

                for index, setting in enumerate(kijiku_settings):
                    key = kijiku_settings_key_names.get(index)

                    key_value_tuple_pairs.append((key, setting))

                return key_value_tuple_pairs
            
##-------------------start-of-GUI-Structure---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            ## tab 1 | Main
            with gr.Tab("Kudasai") as self.kudasai_tab:

                ## tab 2 | indexing
                with gr.Tab("Indexing | Kairyou") as self.indexing_tab:
                    with gr.Row():

                        ## input fields, text input for indexing, and replacement json file input.
                        with gr.Column():
                            self.input_txt_file_indexing = gr.File(label='TXT file with Japanese Text', file_count='single', file_types=['.txt'], type='filepath')
                            self.input_json_file_indexing = gr.File(label='Replacements JSON file', file_count='single', file_types=['.json'], type='filepath')
                            self.input_knowledge_base_file = gr.File(label='Knowledge Base Single File', file_count='single', file_types=['.txt'], type='filepath')
                            self.input_knowledge_base_directory = gr.File(label='Knowledge Base Directory', file_count='directory', type='filepath')

                            ## run and clear buttons
                            with gr.Row():
                                self.indexing_run_button = gr.Button('Run', variant='primary')
                                self.indexing_clear_button = gr.Button('Clear', variant='stop')

                            with gr.Row():
                                self.send_to_kairyou_button = gr.Button('Send to Kairyou (Preprocessing)')

                        ## output fields
                        with gr.Column():
                            self.indexing_output_field  = gr.Textbox(label='Indexed text', lines=56, max_lines=56, show_label=True, interactive=False, show_copy_button=True)

                            with gr.Row():
                                self.save_to_file_indexed_text = gr.Button('Save As')
                            
                        with gr.Column():
                            self.indexing_results_output_field = gr.Textbox(label='Indexing Results', lines=56, max_lines=56, interactive=False, show_copy_button=True)

                            with gr.Row():
                                self.save_to_file_indexing_results = gr.Button('Save As')

                        with gr.Column():
                            self.debug_log_output_field_indexing_tab = gr.Textbox(label='Debug Log', lines=56, max_lines=56, interactive=False, show_copy_button=True)

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
                                self.send_to_kaiseki_button = gr.Button('Send to Kaiseki (DeepL)')
                                self.send_to_kijiku_button = gr.Button('Send to Kijiku (LLMs)')

                        ## output fields
                        with gr.Column():
                            self.preprocessing_output_field  = gr.Textbox(label='Preprocessed text', lines=44, max_lines=44, show_label=True, interactive=False, show_copy_button=True)

                            with gr.Row():
                                self.save_to_file_preprocessed_text = gr.Button('Save As')
                            
                        with gr.Column():
                            self.preprocessing_results_output_field = gr.Textbox(label='Preprocessing Results', lines=44, max_lines=44, interactive=False, show_copy_button=True)

                            with gr.Row():
                                self.save_to_file_preprocessing_results = gr.Button('Save As')

                        with gr.Column():
                            self.debug_log_output_field_preprocess_tab = gr.Textbox(label='Debug Log', lines=44, max_lines=44, interactive=False, show_copy_button=True)

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
                                self.kaiseki_api_key_input_field = gr.Textbox(label='API Key', value=get_saved_kaiseki_api_key, lines=1, show_label=True, interactive=True, type='password')

                            with gr.Row():
                                self.kaiseki_translate_button = gr.Button('Translate', variant="primary")
                                self.kaiseki_clear_button = gr.Button('Clear', variant='stop')

                        ## output fields
                        with gr.Column():
                            self.kaiseki_translated_text_output_field = gr.Textbox(label='Translated Text', lines=31,max_lines=31, interactive=False, show_copy_button=True)

                            with gr.Row():
                                self.save_to_file_kaiseki_translated_text = gr.Button('Save As')

                        with gr.Column():
                            self.kaiseki_je_check_text_output_field = gr.Textbox(label='JE Check Text', lines=31,max_lines=31, interactive=False, show_copy_button=True)

                            with gr.Row():
                                self.save_to_file_kaiseki_je_check_text = gr.Button('Save As')

                        with gr.Column():
                            self.kaiseki_debug_log_output_field = gr.Textbox(label='Debug Log', lines=31,max_lines=31, interactive=False, show_copy_button=True)

                            with gr.Row():
                                self.save_to_file_debug_log_kaiseki_tab = gr.Button('Save As')

                ## tab 5 | Translation Model 2 | Kijiku
                with gr.Tab("Translation With LLMs | Kijiku") as self.kijiku_tab:
                    with gr.Row():

                        ## input file or text input, gui allows for both but will prioritize file input
                        with gr.Column():
                            self.input_txt_file_kijiku = gr.File(label='TXT file with Japanese Text', file_count='single', file_types=['.txt'], type='filepath', interactive=True)
                            self.input_text_kijiku = gr.Textbox(label='Japanese Text', placeholder='Use this or the text file input, if you provide both, Kudasai will use the file input.', lines=10, show_label=True, interactive=True, type='text')
                            self.input_kijiku_rules_file = gr.File(value = FileEnsurer.config_kijiku_rules_path, label='Kijiku Rules File', file_count='single', file_types=['.json'], type='filepath')

                            with gr.Row():
                                self.llm_option_dropdown = gr.Dropdown(label='LLM Option', choices=["OpenAI", "Gemini"], value="OpenAI", show_label=True, interactive=True)
                            
                            with gr.Row():
                                self.kijiku_api_key_input = gr.Textbox(label='API Key', value=get_saved_openai_api_key, lines=1, max_lines=2, show_label=True, interactive=True, type='password')

                            with gr.Row():
                                self.kijiku_translate_button = gr.Button('Translate', variant="primary")
                                self.kijiku_calculate_costs_button = gr.Button('Calculate Costs', variant='secondary')

                            with gr.Row():
                                self.kijiku_clear_button = gr.Button('Clear', variant='stop')

                        ## output fields
                        with gr.Column():
                            self.kijiku_translated_text_output_field = gr.Textbox(label='Translated Text', lines=43,max_lines=43, interactive=False, show_copy_button=True)

                            with gr.Row():
                                self.save_to_file_kijiku_translated_text = gr.Button('Save As')

                        with gr.Column():
                            self.kijiku_je_check_text_output_field = gr.Textbox(label='JE Check Text', lines=43,max_lines=43, interactive=False, show_copy_button=True)

                            with gr.Row():
                                self.save_to_file_kijiku_je_check_text = gr.Button('Save As')

                        with gr.Column():
                            self.kijiku_debug_log_output_field = gr.Textbox(label='Debug Log', lines=43, max_lines=43, interactive=False, show_copy_button=True)

                            with gr.Row():
                                self.save_to_file_debug_log_kijiku_tab = gr.Button('Save As')

                ## tab 6 | Kijiku Settings
                with gr.Tab("Kijiku Settings") as self.kijiku_settings_tab:
                    with gr.Row():

                        with gr.Column():
                            gr.Markdown("Kijiku Settings")
                            gr.Markdown("See https://github.com/Bikatr7/Kudasai/blob/main/README.md#kijiku-settings for further details")
                            gr.Markdown("These settings are used for both OpenAI and Gemini, but some settings are ignored by one or the other. For example, Gemini ignores prompt assembly mode.")


                            self.prompt_assembly_mode_input_field = gr.Dropdown(label='Prompt Assembly Mode',
                                                                                value=int(GuiJsonUtil.fetch_kijiku_setting_key_values("base kijiku settings","prompt_assembly_mode")),
                                                                                choices=[1,2],
                                                                                info="1 or 2. 1 means the system message will actually be treated as a system message. 2 means it'll be treated as a user message. 1 is recommend for gpt-4 otherwise either works. For Gemini, this setting is ignored.",
                                                                                show_label=True,
                                                                                interactive=True,
                                                                                elem_id="prompt_assembly_mode")
                            
                            self.number_of_lines_per_batch_input_field = gr.Textbox(label='Number of Lines Per Batch',
                                                                                    value=(GuiJsonUtil.fetch_kijiku_setting_key_values("base kijiku settings","number_of_lines_per_batch")),
                                                                                    info="The number of lines to be built into a prompt at once. Theoretically, more lines would be more cost effective, but other complications may occur with higher lines. So far been tested up to 48.",
                                                                                    lines=1,
                                                                                    max_lines=1,
                                                                                    show_label=True,
                                                                                    interactive=True,
                                                                                    elem_id="number_of_lines_per_batch",
                                                                                    show_copy_button=True)
                            
                            self.sentence_fragmenter_mode_input_field = gr.Dropdown(label='Sentence Fragmenter Mode',
                                                                                    value=int(GuiJsonUtil.fetch_kijiku_setting_key_values("base kijiku settings","sentence_fragmenter_mode")),
                                                                                    choices=[1,2],
                                                                                    info="1 or 2  (1 - via regex and other nonsense) 2 - None (Takes formatting and text directly from API return)) the API can sometimes return a result on a single line, so this determines the way Kijiku fragments the sentences if at all. Use 2 for newer models.",
                                                                                    show_label=True,
                                                                                    interactive=True,
                                                                                    elem_id="sentence_fragmenter_mode")
                            
                            self.je_check_mode_input_field = gr.Dropdown(label='JE Check Mode',
                                                                        value=int(GuiJsonUtil.fetch_kijiku_setting_key_values("base kijiku settings","je_check_mode")),
                                                                        choices=[1,2],
                                                                        info="1 or 2, 1 will print out the jap then the english below separated by ---, 2 will attempt to pair the english and jap sentences, placing the jap above the eng. If it cannot, it will default to 1. Use 2 for newer models.",
                                                                        show_label=True,
                                                                        interactive=True,
                                                                        elem_id="je_check_mode")
                            
                            self.number_of_malformed_batch_retries_input_field = gr.Textbox(label="Number Of Malformed Batch Retries",
                                                                                value=GuiJsonUtil.fetch_kijiku_setting_key_values("base kijiku settings","number_of_malformed_batch_retries"),
                                                                                info="(Malformed batch is when je-fixing fails) How many times Kijiku will attempt to mend a malformed batch (mending is resending the request), only for gpt4. Be careful with increasing as cost increases at (cost * length * n) at worst case. This setting is ignored if je_check_mode is set to 1.",
                                                                                lines=1,
                                                                                max_lines=1,
                                                                                show_label=True,
                                                                                interactive=True,
                                                                                elem_id="number_of_malformed_batch_retries",
                                                                                show_copy_button=True)
                                                        
                            self.batch_retry_timeout_input_field = gr.Textbox(label="Batch Retry Timeout",
                                                                            value=GuiJsonUtil.fetch_kijiku_setting_key_values("base kijiku settings","batch_retry_timeout"),
                                                                            info="How long Kijiku will try to translate a batch in seconds, if a requests exceeds this duration, Kijiku will leave it untranslated.",
                                                                            lines=1,
                                                                            max_lines=1,
                                                                            show_label=True,
                                                                            interactive=True,
                                                                            elem_id="batch_retry_timeout",
                                                                            show_copy_button=True)

                            self.number_of_concurrent_batches_input_field = gr.Textbox(label="Number Of Concurrent Batches",
                                                                                       value=GuiJsonUtil.fetch_kijiku_setting_key_values("base kijiku settings","number_of_concurrent_batches"),
                                                                                        info="How many translations batches Kijiku will send to the translation API at a time. For OpenAI, be conservative as rate-limiting is aggressive, I'd suggest 3-5. For Gemini, do not exceed 60.",
                                                                                        lines=1,
                                                                                        max_lines=1,
                                                                                        show_label=True,
                                                                                        interactive=True,
                                                                                        elem_id="number_of_concurrent_batches",
                                                                                        show_copy_button=True)

                        with gr.Column(): 
                            gr.Markdown("OpenAI API Settings")
                            gr.Markdown("See https://platform.openai.com/docs/api-reference/chat/create for further details")
                            gr.Markdown("openai_stream, openai_logit_bias, openai_stop and openai_n are included for completion's sake, current versions of Kudasai will hardcode their values when validating the Kijiku_rule.json to their default values. As different values for these settings do not have a use case in Kudasai's current implementation.")

                            self.openai_model_input_field = gr.Dropdown(label="OpenAI Model",
                                                                        value=str(GuiJsonUtil.fetch_kijiku_setting_key_values("openai settings","openai_model")),
                                                                        choices=[model for model in ALLOWED_OPENAI_MODELS],
                                                                        info="ID of the model to use. Kijiku only works with 'chat' models.",
                                                                        show_label=True,
                                                                        interactive=True,
                                                                        elem_id="openai_model")
                            
                            self.openai_system_message_input_field = gr.Textbox(label="OpenAI System Message",
                                                                            value=str(GuiJsonUtil.fetch_kijiku_setting_key_values("openai settings","openai_system_message")),
                                                                            info="Instructions to the model. Basically tells the model how to translate.",
                                                                            lines=1,
                                                                            max_lines=1,
                                                                            show_label=True,
                                                                            interactive=True,
                                                                            elem_id="openai_system_message",
                                                                            show_copy_button=True)
                            
                            self.openai_temperature_input_field = gr.Slider(label="OpenAI Temperature",
                                                                        value=float(GuiJsonUtil.fetch_kijiku_setting_key_values("openai settings","openai_temperature")),
                                                                        minimum=0.0,
                                                                        maximum=2.0,
                                                                        info="What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. Lower values are typically better for translation.",
                                                                        show_label=True,
                                                                        interactive=True,
                                                                        elem_id="openai_temperature")
                            
                            self.openai_top_p_input_field = gr.Slider(label="OpenAI Top P",
                                                                    value=float(GuiJsonUtil.fetch_kijiku_setting_key_values("openai settings","openai_top_p")),
                                                                    minimum=0.0,
                                                                    maximum=1.0,
                                                                    info="An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. I generally recommend altering this or temperature but not both.",
                                                                    show_label=True,
                                                                    interactive=True,
                                                                    elem_id="openai_top_p")
                            
                            self.openai_n_input_field = gr.Textbox(label="OpenAI N",
                                                                value=str(GuiJsonUtil.fetch_kijiku_setting_key_values("openai settings","openai_n")),
                                                                info="How many chat completion choices to generate for each input message. Do not change this.",
                                                                show_label=True,
                                                                interactive=False,
                                                                elem_id="openai_n",
                                                                show_copy_button=True)
                            
                            self.openai_stream_input_field = gr.Textbox(label="OpenAI Stream",
                                                                    value=str(GuiJsonUtil.fetch_kijiku_setting_key_values("openai settings","openai_stream")),
                                                                    info="If set, partial message deltas will be sent, like in ChatGPT. Tokens will be sent as data-only server-sent events as they become available, with the stream terminated by a data: [DONE] message. See the OpenAI python library on GitHub for example code. Do not change this.",
                                                                    show_label=True,
                                                                    interactive=False,
                                                                    elem_id="openai_stream",
                                                                    show_copy_button=True)
                            
                            self.openai_stop_input_field = gr.Textbox(label="OpenAI Stop",
                                                                    value=str(GuiJsonUtil.fetch_kijiku_setting_key_values("openai settings","openai_stop")),
                                                                    info="Up to 4 sequences where the API will stop generating further tokens. Do not change this.",
                                                                    show_label=True,
                                                                    interactive=False,
                                                                    elem_id="openai_stop",
                                                                    show_copy_button=True)
                            
                            self.openai_logit_bias_input_field = gr.Textbox(label="OpenAI Logit Bias",
                                                                        value=str(GuiJsonUtil.fetch_kijiku_setting_key_values("openai settings","openai_logit_bias")),
                                                                        info="Modifies the likelihood of specified tokens appearing in the completion. Do not change this.",
                                                                        show_label=True,
                                                                        interactive=False,
                                                                        elem_id="openai_logit_bias",
                                                                        show_copy_button=True)
                            
                            self.openai_max_tokens_input_field = gr.Textbox(label="OpenAI Max Tokens",
                                                                        value=str(GuiJsonUtil.fetch_kijiku_setting_key_values("openai settings","openai_max_tokens")),
                                                                        info="The maximum number of tokens to generate in the chat completion. The total length of input tokens and generated tokens is limited by the model's context length. I wouldn't recommend changing this. Is none by default. If you change to an integer, make sure it doesn't exceed that model's context length or your request will fail and repeat till timeout.",
                                                                        lines=1,
                                                                        max_lines=1,
                                                                        show_label=True,
                                                                        interactive=True,
                                                                        elem_id="openai_max_tokens",
                                                                        show_copy_button=True)
                            
                            self.openai_presence_penalty_input_field = gr.Slider(label="OpenAI Presence Penalty",
                                                                            value=float(GuiJsonUtil.fetch_kijiku_setting_key_values("openai settings","openai_presence_penalty")),
                                                                            info="Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics. While negative values encourage repetition. Should leave this at 0.0.",
                                                                            minimum=-2.0,
                                                                            maximum=2.0,
                                                                            show_label=True,
                                                                            interactive=True,
                                                                            elem_id="openai_presence_penalty")
                            
                            self.openai_frequency_penalty_input_field = gr.Slider(label="OpenAI Frequency Penalty",
                                                                            value=float(GuiJsonUtil.fetch_kijiku_setting_key_values("openai settings","openai_frequency_penalty")),
                                                                            info="Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim. Negative values encourage repetition. Should leave this at 0.0.",
                                                                            minimum=-2.0,
                                                                            maximum=2.0,
                                                                            show_label=True,
                                                                            interactive=True,
                                                                            elem_id="openai_frequency_penalty")

                        with gr.Column():
                            gr.Markdown("Gemini API Settings")
                            gr.Markdown("https://ai.google.dev/docs/concepts#model-parameters for further details")
                            gr.Markdown("gemini_stream, gemini_stop_sequences and gemini_candidate_count are included for completion's sake, current versions of Kudasai will hardcode their values when validating the Kijiku_rule.json to their default values. As different values for these settings do not have a use case in Kudasai's current implementation.")
                                

                            self.gemini_model_input_field = gr.Dropdown(label="Gemini Model",
                                                                        value=str(GuiJsonUtil.fetch_kijiku_setting_key_values("gemini settings","gemini_model")),
                                                                        choices=[model for model in ALLOWED_GEMINI_MODELS],
                                                                        info="The model to use. Currently only supports gemini-pro and gemini-pro-vision, the 1.0 model and it's aliases.",
                                                                        show_label=True,
                                                                        interactive=True,
                                                                        elem_id="gemini_model")

                            self.gemini_prompt_input_field = gr.Textbox(label="Gemini Prompt",
                                                                    value=str(GuiJsonUtil.fetch_kijiku_setting_key_values("gemini settings","gemini_prompt")),
                                                                    info="Instructions to the model. Basically tells the model how to translate.",
                                                                    lines=1,
                                                                    max_lines=1,
                                                                    show_label=True,
                                                                    interactive=True,
                                                                    elem_id="gemini_prompt",
                                                                    show_copy_button=True)
                            
                            self.gemini_temperature_input_field = gr.Slider(label="Gemini Temperature",
                                                                        value=float(GuiJsonUtil.fetch_kijiku_setting_key_values("gemini settings","gemini_temperature")),
                                                                        minimum=0.0,
                                                                        maximum=2.0,
                                                                        info="What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. Lower values are typically better for translation.",
                                                                        show_label=True,
                                                                        interactive=True,
                                                                        elem_id="gemini_temperature")
                            
                            self.gemini_top_p_input_field = gr.Textbox(label="Gemini Top P",
                                                                    value=str(GuiJsonUtil.fetch_kijiku_setting_key_values("gemini settings","gemini_top_p")),
                                                                    info="An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. I generally recommend altering this or temperature but not both.",
                                                                    lines=1,
                                                                    max_lines=1,
                                                                    show_label=True,
                                                                    interactive=True,
                                                                    elem_id="gemini_top_p",
                                                                    show_copy_button=True)
                            
                            self.gemini_top_k_input_field = gr.Textbox(label="Gemini Top K",
                                                                    value=str(GuiJsonUtil.fetch_kijiku_setting_key_values("gemini settings","gemini_top_k")),
                                                                    info="Determines the number of most probable tokens to consider for each selection step. A higher value increases diversity, a lower value makes the output more deterministic.",
                                                                    lines=1,
                                                                    max_lines=1,
                                                                    show_label=True,
                                                                    interactive=True,
                                                                    elem_id="gemini_top_k",
                                                                    show_copy_button=True)

                            self.gemini_candidate_count_input_field = gr.Textbox(label="Gemini Candidate Count",
                                                                                value=str(GuiJsonUtil.fetch_kijiku_setting_key_values("gemini settings","gemini_candidate_count")),
                                                                                info="The number of candidates to generate for each input message. Do not change this.",
                                                                                lines=1,
                                                                                max_lines=1,
                                                                                show_label=True,
                                                                                interactive=False,
                                                                                elem_id="gemini_candidate_count",
                                                                                show_copy_button=True)

                            self.gemini_stream_input_field = gr.Textbox(label="Gemini Stream",
                                                                    value=str(GuiJsonUtil.fetch_kijiku_setting_key_values("gemini settings","gemini_stream")),
                                                                    info="If set, partial message deltas will be sent, like in Gemini chat. Tokens will be sent as data-only server-sent events as they become available, with the stream terminated by a data: [DONE] message. See the OpenAI python library on GitHub for example code. Do not change this.",
                                                                    lines=1,
                                                                    max_lines=1,
                                                                    show_label=True,
                                                                    interactive=False,
                                                                    elem_id="gemini_stream",
                                                                    show_copy_button=True)
                            
                            self.gemini_stop_sequences_input_field = gr.Textbox(label="Gemini Stop Sequences",
                                                                            value=str(GuiJsonUtil.fetch_kijiku_setting_key_values("gemini settings","gemini_stop_sequences")),
                                                                            info="Up to 4 sequences where the API will stop generating further tokens. Do not change this.",
                                                                            lines=1,
                                                                            max_lines=1,
                                                                            show_label=True,
                                                                            interactive=False,
                                                                            elem_id="gemini_stop_sequences",
                                                                            show_copy_button=True)

                            self.gemini_max_output_tokens_input_field = gr.Textbox(label="Gemini Max Output Tokens",
                                                                                value=str(GuiJsonUtil.fetch_kijiku_setting_key_values("gemini settings","gemini_max_output_tokens")),
                                                                                info="The maximum number of tokens to generate in the chat completion. The total length of input tokens and generated tokens is limited by the model's context length. I wouldn't recommend changing this. Is none by default. If you change to an integer, make sure it doesn't exceed that model's context length or your request will fail and repeat till timeout.",
                                                                                lines=1,
                                                                                max_lines=1,
                                                                                show_label=True,
                                                                                interactive=True,
                                                                                elem_id="gemini_max_output_tokens",
                                                                                show_copy_button=True)
                        

                    with gr.Row():
                        self.kijiku_settings_reset_to_default_button = gr.Button('Reset to Default', variant='secondary')
                        self.kijiku_settings_discard_changes_button = gr.Button('Discard Changes', variant='stop')

                    with gr.Row():
                        self.kijiku_settings_apply_changes_button = gr.Button('Apply Changes', variant='primary')

                ## tab 7 | Logging
                with gr.Tab("Logging") as self.logging_tab:

                    with gr.Row():
                        self.logging_tab_debug_log_output_field = gr.Textbox(label='Debug Log', lines=10, interactive=False, show_copy_button=True)

                    with gr.Row():
                        self.save_to_file_debug_log_logging_tab = gr.Button('Save As')

                    with gr.Row():
                        self.logging_tab_error_log_output_field = gr.Textbox(label='Error Log', lines=10, interactive=False, show_copy_button=True)

                    with gr.Row():
                        self.save_to_file_error_log_logging_tab = gr.Button('Save As')

                    with gr.Row():
                        self.logging_clear_logs_button = gr.Button('Clear Logs', variant='stop')

##-------------------start-of-Listener-Functions---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            def webgui_update_check() -> None:

                """
                
                Checks for if a Kudasai update is available.

                """

                Kudasai.connection, update_prompt = Toolkit.check_update()

                if(update_prompt != ""):
                    gr.Info("Update available, see https://github.com/Bikatr7/Kudasai/releases/latest/ for more information.")

                if(Kudasai.connection == False):
                    gr.Warning("No internet connection, Auto-MTL features disabled (Indexing and Preprocessing still functional). Please reload the page when you have an internet connection.")

##-------------------start-of-index()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
                    
            def index(input_txt_file:gr.File, input_json_file_preprocessing:gr.File, input_knowledge_base_file:gr.File, input_knowledge_base_directory:typing.List[str]) -> typing.Tuple[str, str, str, str, str]:
                    
                """
                
                Runs the indexing and displays the results in the indexing output field. If no txt file is selected, an error is raised. If no json file is selected, an error is raised. If no knowledge base file or directory is selected, an error is raised.
                Knowledge base file or directory must be selected, but not both.
                Also displays the indexing results, the debug log, and the error log.

                Parameters:
                input_txt_file (gr.File) : The input txt file.
                input_json_file_preprocessing (gr.File) : The input json file.
                input_knowledge_base_file (gr.File) : The knowledge base file.
                input_knowledge_base_directory (typing.List[str]) : List of knowledge base file paths.

                Returns:
                indexed_text (str) : The indexed text.
                indexing_log (str) : The indexing log.
                log_text (str) : The log text for the Indexing tab.
                log_text (str) : The log text for the log tab.
                error_log (str) : The error log for the log tab.

                """

                if(input_txt_file is not None):

                    if(input_json_file_preprocessing is not None):

                        ## must be one, but not both
                        if(input_knowledge_base_file is not None or input_knowledge_base_directory is not None) and not (input_knowledge_base_file is not None and input_knowledge_base_directory is not None):


                            ## looks like file will just be the file path
                            ## but directory will be a list of file paths, I can't think of a workaround right now, so will have to update kairyou to accept a list of file paths. 
                            ## wait nvm im a genius, let's just read all the files and concatenate them into one string lmfao

                            ## index does not produce an error log
                            error_log = ""

                            knowledge_base_paths = []
                            knowledge_base_string = ""

                            text_to_index = gui_get_text_from_file(input_txt_file)
                            replacements = gui_get_json_from_file(input_json_file_preprocessing)

                            if(input_knowledge_base_file is not None):
                                knowledge_base_paths.append(input_knowledge_base_file)

                            else:
                                knowledge_base_paths = [file for file in input_knowledge_base_directory]

                            for file in knowledge_base_paths:
                                knowledge_base_string += gui_get_text_from_file(file)

                            gr.Info("Indexing may take a while, please be patient.")

                            unique_names, indexing_log = Indexer.index(text_to_index, knowledge_base_string, replacements)

                            ## Indexer does not directly log anything, in case of anything else touching it, we will grab the log from the log file
                            log_text = FileEnsurer.standard_read_file(Logger.log_file_path)

                            indexed_text = Kudasai.mark_indexed_names(text_to_index, unique_names)

                            return indexed_text, indexing_log, log_text, log_text, error_log

                        else:
                            raise gr.Error("No knowledge base file or directory selected (or both selected, select one or the other)")
                    
                    else:
                        raise gr.Error("No JSON file selected")
                    
                else:
                    raise gr.Error("No TXT file selected")

##-------------------start-of-preprocess()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            def preprocess(input_txt_file:gr.File, input_json_file_preprocessing:gr.File, input_text_field_contents:str) -> typing.Tuple[str, str, str, str, str]:

                """

                Runs the preprocessing and displays the results in the preprocessing output field. If no txt file is selected, an error is raised. If no json file is selected, an error is raised.
                Also displays the preprocessing results, the debug log, and the error log.
                Prioritizes the txt file input over the text input field.

                Parameters:
                input_txt_file (gr.File) : The input txt file.
                input_json_file_preprocessing (gr.File) : The input json file.
                input_text (str) : The input text.

                Returns:
                text_to_preprocess (str) : The preprocessed text.
                preprocessing_log (str) : The preprocessing log.
                log_text (str) : The log text for the Kairyou tab.
                log_text (str) : The log text for the log tab.
                error_log (str) : The error log for the log tab.

                """

                if(input_txt_file == None and input_text_field_contents == ""):
                    raise gr.Error("No TXT file selected and no text input")

                if(input_json_file_preprocessing is not None):

                    if(input_txt_file is not None):
                        text_to_preprocess = gui_get_text_from_file(input_txt_file)

                    else:
                        text_to_preprocess = input_text_field_contents

                    replacements = gui_get_json_from_file(input_json_file_preprocessing)

                    try:

                        preprocessed_text, preprocessing_log, error_log =  Kairyou.preprocess(text_to_preprocess, replacements)

                    except InvalidReplacementJsonKeys:
                        raise gr.Error("Invalid JSON file, please ensure that the JSON file contains the correct keys See: https://github.com/Bikatr7/Kairyou?tab=readme-ov-file#usage")

                    timestamp = Toolkit.get_timestamp(is_archival=True)

                    FileEnsurer.write_kairyou_results(preprocessed_text, preprocessing_log, error_log, timestamp)

                    log_text = FileEnsurer.standard_read_file(Logger.log_file_path)

                    return preprocessed_text, preprocessing_log, log_text, log_text, error_log
            
                else:
                    raise gr.Error("No JSON file selected")
                
##-------------------start-of-kaiseki_translate_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            def translate_with_kaiseki(input_txt_file:gr.File, input_text:str, api_key_input:str) -> typing.Tuple[str, str, str, str]:

                """
                
                Translates the text in the input_txt_file or input_text using the DeepL API. If no txt file or text is selected, an error is raised. If no API key is provided or the API key is invalid, an error is raised.
                Displays the translated text, the debug log, and the error log.

                Parameters:
                input_txt_file (gr.File) : The input txt file.
                input_text (str) : The input text.
                api_key_input (str) : The API key input.

                Returns:
                translated_text (str) : The translated text.
                je_check_text (str) : The je check text.
                log_text (str) : The log text for the Log tab.

                """

                if(Kudasai.connection == False):
                    raise gr.Error("No internet connection detected, please connect to the internet and reload the page to use translation features of Kudasai.")
                
                if(input_txt_file is None and input_text == ""):
                    raise gr.Error("No TXT file or text selected")
                
                if(api_key_input == ""):
                    raise gr.Error("No API key provided")

                ## in case of subsequent runs, we need to reset the static variables
                Kaiseki.reset_static_variables()

                ## start of translation, so we can assume that that we don't want to interrupt it
                FileEnsurer.do_interrupt = False

                ## if translate button is clicked, we can assume that the translation is ongoing
                self.is_translation_ongoing = True
                
                if(input_txt_file is not None):
                    text_to_translate = gui_get_text_from_file(input_txt_file)

                else:
                    text_to_translate = input_text

                try:
                    EasyTL.set_api_key("deepl", str(api_key_input))

                    is_valid, e = EasyTL.test_api_key_validity("deepl")

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

                error_text = FileEnsurer.standard_read_file(FileEnsurer.error_log_path)

                ## also gonna want to update the api key file with the new api key
                FileEnsurer.standard_overwrite_file(FileEnsurer.deepl_api_key_path, base64.b64encode(str(api_key_input).encode('utf-8')).decode('utf-8'), omit=True)

                return translated_text, je_check_text, log_text, error_text
            
##-------------------start-of-translate_with_kijiku()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            async def translate_with_kijiku(input_txt_file:gr.File, input_text:str, api_key:str, llm_type:str, kijiku_rules_file:gr.File) -> typing.Tuple[str, str, str, str]:

                """
                
                Translates the text in the input_txt_file or input_text using either OpenAI or Gemini. If no txt file or text is selected, an error is raised. If no API key is provided or the API key is invalid, an error is raised.
                Displays the translated text, the debug log, and the error log.

                Parameters:
                input_txt_file (gr.File) : The input txt file.
                input_text (gr.Textbox) : The input text.
                api_key_input (gr.Textbox) : The API key input.

                Returns:
                translated_text (str) : The translated text.
                je_check_text (str) : The je check text.
                log_text (str) : The log text for the Log tab.
                error_text (str) : The error text for the Log tab.
                
                """

                ## check if we have stuff to translate
                if(input_txt_file is None and input_text == ""):
                    raise gr.Error("No TXT file or text selected")
                
                if(api_key == ""):
                    raise gr.Error("No API key provided")
                
                if(kijiku_rules_file is None):
                    raise gr.Error("No Kijiku rules file selected")

                if(Kudasai.connection == False):
                    raise gr.Error("No internet connection detected, please connect to the internet and reload the page to use translation features of Kudasai.")

                ## in case of subsequent runs, we need to reset the static variables
                Kijiku.reset_static_variables()

                ## start of translation, so we can assume that that we don't want to interrupt it
                FileEnsurer.do_interrupt = False

                ## if translate button is clicked, we can assume that the translation is ongoing
                self.is_translation_ongoing = True

                ## first, set the json in the json handler to the json currently set as in gui_json_util
                JsonHandler.current_kijiku_rules = GuiJsonUtil.current_kijiku_rules

                ## next, set the llm type
                if(llm_type == "OpenAI"):
                    Kijiku.LLM_TYPE = "openai" 

                else:
                    Kijiku.LLM_TYPE = "gemini"

                ## api key as well
                await set_kijiku_api_key(api_key)
                
                if(input_txt_file is not None):
                    text_to_translate = gui_get_text_from_file(input_txt_file)
                
                else:
                    text_to_translate = input_text

                ## need to convert the text to translate to list of strings
                Kijiku.text_to_translate = [line for line in str(text_to_translate).splitlines()]

                ## commence translation
                await Kijiku.commence_translation(is_webgui=True)
                Kijiku.write_kijiku_results()

                ## je check text and translated text are lists of strings, so we need to convert them to strings
                translated_text = "\n".join(Kijiku.translated_text)
                je_check_text = "\n".join(Kijiku.je_check_text)

                ## Log text is cleared from the client, so we need to get it from the log file
                log_text = FileEnsurer.standard_read_file(Logger.log_file_path)

                error_text = FileEnsurer.standard_read_file(FileEnsurer.error_log_path)
                
                ## then overwrite the api key file with the new api key
                update_kijiku_api_key(api_key)

                return translated_text, je_check_text, log_text, error_text
            
##-------------------start-of-kijiku_calculate_costs_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            async def kijiku_calculate_costs_button_click(input_txt_file:str, input_text:str, llm_type:str, api_key:str, kijiku_rules_file:gr.File) -> str:


                """
                
                Calculates the cost of the text in the input_txt_file or input_text using the OpenAI API or Gemini API. If no txt file or text is selected, an error is raised.
                Displays the cost, and the debug log.

                Parameters:
                input_txt_file (gr.File) : The input txt file.
                input_text (str) : The input text.
                llm_type (str) : The language model type.
                api_key (str) : The

                Returns:
                cost_estimation (str) : The cost estimation formatted as a string.
                
                """

                if(input_txt_file is None and input_text == ""):
                    raise gr.Error("No TXT file or text selected")
                
                if(api_key == "" and llm_type != "OpenAI"):
                    raise gr.Error("No API key provided. Does not charge for cost estimation, but is required for Gemini Cost Calculation")
                
                if(Kudasai.connection == False and llm_type != "OpenAI"):
                    raise gr.Error("No internet connection detected, please connect to the internet and reload the page to calculate costs for Gemini")
                
                if(kijiku_rules_file is None):
                    raise gr.Error("No Kijiku rules file selected")
                
                ## in case of subsequent runs, we need to reset the static variables
                Kijiku.reset_static_variables()

                cost_estimation = ""

                ## first set the llm type
                if(llm_type == "OpenAI"):
                    Kijiku.LLM_TYPE = "openai"

                else:
                    Kijiku.LLM_TYPE = "gemini"


                await set_kijiku_api_key(api_key)

                model = GuiJsonUtil.fetch_kijiku_setting_key_values("openai settings","openai_model") if Kijiku.LLM_TYPE == "openai" else GuiJsonUtil.fetch_kijiku_setting_key_values("gemini settings","gemini_model")
                
                if(input_txt_file is not None):
                    text_to_translate = gui_get_text_from_file(input_txt_file)

                else:
                    text_to_translate = input_text

                translation_instructions = GuiJsonUtil.fetch_kijiku_setting_key_values("openai settings","openai_system_message") if Kijiku.LLM_TYPE == "openai" else GuiJsonUtil.fetch_kijiku_setting_key_values("gemini settings","gemini_prompt")

                num_tokens, estimated_cost, model = EasyTL.calculate_cost(text=text_to_translate, service=Kijiku.LLM_TYPE, model=model, translation_instructions=translation_instructions)

                if(Kijiku.LLM_TYPE == "gemini"):
                    cost_estimation = f"As of Kudasai {Toolkit.CURRENT_VERSION}, Gemini Pro is Free to use\n"

                cost_estimation += "Estimated number of tokens : " + str(num_tokens) + "\n" + "Estimated minimum cost : " + str(estimated_cost) + " USD"
                
                gr.Info(cost_estimation)

                update_kijiku_api_key(api_key)

                return cost_estimation
            
##-------------------start-of-clear_index_tab()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            def clear_index_tab() -> typing.Tuple[None, None, None, None, str, str, str]:


                """

                Clears all fields on the indexing tab. As well as the input fields.

                Returns:
                input_txt_file_indexing (gr.File) : An empty file.
                input_json_file_indexing (gr.File) : An empty file.
                input_knowledge_base_file (gr.File) : An empty file.
                indexing_output_field (str) : An empty string.
                indexing_results_output_field (str) : An empty string.
                debug_log_output_field_indexing_tab (str) : An empty string.

                """

                input_txt_file_indexing = None
                input_json_file_indexing = None
                input_knowledge_base_file = None
                input_knowledge_base_directory = None

                indexing_output_field = ""
                indexing_results_output_field = ""
                debug_log_output_field_indexing_tab = ""

                return input_txt_file_indexing, input_json_file_indexing, input_knowledge_base_file, input_knowledge_base_directory, indexing_output_field, indexing_results_output_field, debug_log_output_field_indexing_tab

##-------------------start-of-clear_preprocessing_tab()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------                

            def clear_preprocessing_tab() -> typing.Tuple[None, None, str, str, str, str]:

                """

                Clears all fields on the preprocessing tab. As well as the input fields.

                Returns:
                input_txt_file (gr.File) : An empty file.
                input_json_file_preprocessing (gr.File) : An empty file.
                preprocessing_output_field (str) : An empty string.
                preprocessing_results_output_field (str) : An empty string.
                debug_log_output_field_preprocess_tab (str) : An empty string.

                """

                input_txt_file = None
                input_json_file_preprocessing = None

                input_text = ""
                preprocessing_output_field = ""
                preprocessing_results_output_field = ""
                debug_log_output_field_preprocess_tab = ""

                return input_txt_file, input_json_file_preprocessing, input_text, preprocessing_output_field, preprocessing_results_output_field, debug_log_output_field_preprocess_tab
            
##-------------------start-of-kaiseki_run_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            def clear_kaiseki_tab() -> typing.Tuple[None, str, str, str, str]:

                """
                
                Clears all fields on the Kaiseki tab. As well as the input fields.

                Returns:
                input_txt_file_kaiseki (gr.File) : An empty file.
                input_text_kaiseki (str) : An empty string.
                kaiseki_translated_text_output_field (str) : An empty string.
                je_check_text_field_kaiseki (str) : An empty string.
                kaiseki_debug_log_output_field (str) : An empty string.

                """

                ## if clear button is clicked, we can assume that the translation is over, or that the user wants to cancel the translation
                self.is_translation_ongoing = False

                ## Same as above, we can assume that the user wants to cancel the translation if it's ongoing
                FileEnsurer.do_interrupt = True
                
                input_file_kaiseki = None

                input_text_kaiseki = ""

                kaiseki_translated_text_output_field = ""
                je_check_text_field_kaiseki = ""
                kaiseki_debug_log_output_field = ""

                return input_file_kaiseki, input_text_kaiseki, kaiseki_translated_text_output_field, je_check_text_field_kaiseki, kaiseki_debug_log_output_field
            
##-------------------start-of-clear_kijiku_tab()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            def clear_kijiku_tab() -> typing.Tuple[None, str, gr.File, str, str, str]:

                """
                
                Clears all fields on the Kijiku tab. As well as the input fields.

                Returns:
                input_txt_file_kijiku (gr.File) : An empty file.
                input_text_kijiku (str) : An empty string.
                kijiku_translated_text_output_field (str) : An empty string.
                je_check_text_field_kijiku (str) : An empty string.
                kijiku_debug_log_output_field (str) : An empty string.

                """

                ## if clear button is clicked, we can assume that the translation is over, or that the user wants to cancel the translation
                self.is_translation_ongoing = False

                ## Same as above, we can assume that the user wants to cancel the translation if it's ongoing
                FileEnsurer.do_interrupt = True

                input_file_kijiku = None

                input_text_kijiku = ""

                ## Also gonna want to reset the json input field to the default json file
                input_kijiku_rules_file = gr.File(value = FileEnsurer.config_kijiku_rules_path, label='Kijiku Rules File', file_count='single', file_types=['.json'], type='filepath')

                kijiku_translated_text_output_field = ""
                je_check_text_field_kijiku = ""
                kijiku_debug_log_output_field = ""

                return input_file_kijiku, input_text_kijiku, input_kijiku_rules_file, kijiku_translated_text_output_field, je_check_text_field_kijiku, kijiku_debug_log_output_field
            
##-------------------start-of-clear_log_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        
            def clear_log_button_click() -> typing.Tuple[str, str]:

                """

                Clears the logs on the log tab.

                Returns:
                logging_tab_debug_log_output_field (str) : An empty string.
                logging_tab_error_log_output_field (str) : An empty string.

                """

                ## also needs to clear the log and error log files
                FileEnsurer.standard_overwrite_file(Logger.log_file_path, "")
                FileEnsurer.standard_overwrite_file(FileEnsurer.error_log_path, "")

                logging_tab_debug_log_output_field = ""
                logging_tab_error_log_output_field = ""

                return logging_tab_debug_log_output_field, logging_tab_error_log_output_field

##-------------------start-of-apply_new_kijiku_settings()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            def apply_new_kijiku_settings(input_kijiku_rules_file:gr.File,
                                        prompt_assembly_mode:int,
                                        number_of_lines_per_batch:int,
                                        sentence_fragmenter_mode:int,
                                        je_check_mode:int,
                                        num_malformed_batch_retries:int,
                                        batch_retry_timeout:int,
                                        num_concurrent_batches:int,
                                        openai_model:str,
                                        openai_system_message:str,
                                        openai_temperature:float,
                                        openai_top_p:float,
                                        openai_n:str,
                                        openai_stream:str,
                                        openai_stop:str,
                                        openai_logit_bias:str,
                                        openai_max_tokens:str,
                                        openai_presence_penalty:float,
                                        openai_frequency_penalty:float,
                                        gemini_model:str,
                                        gemini_prompt:str,
                                        gemini_temperature:float,
                                        gemini_top_p:str,
                                        gemini_top_k:str,
                                        gemini_candidate_count:str,
                                        gemini_stream:str,
                                        gemini_stop_sequences:str,
                                        gemini_max_output_tokens:str) -> None:

                
                """

                Applies the new kijiku settings to the kijiku rules file.

                """

                if(input_kijiku_rules_file is None):
                    raise gr.Error("No Kijiku Rules File Selected. Cannot apply settings.")

                ## build the new kijiku settings list so we can create a key-value pair list
                settings_list = [
                    prompt_assembly_mode,
                    number_of_lines_per_batch,
                    sentence_fragmenter_mode,
                    je_check_mode,
                    num_malformed_batch_retries,
                    batch_retry_timeout,
                    num_concurrent_batches,
                    openai_model,
                    openai_system_message,
                    openai_temperature,
                    openai_top_p,
                    openai_n,
                    openai_stream,
                    openai_stop,
                    openai_logit_bias,
                    openai_max_tokens,
                    openai_presence_penalty,
                    openai_frequency_penalty,
                    gemini_model,
                    gemini_prompt,
                    gemini_temperature,
                    gemini_top_p,
                    gemini_top_k,
                    gemini_candidate_count,
                    gemini_stream,
                    gemini_stop_sequences,
                    gemini_max_output_tokens
                ]

                ## create the new key-value pair list
                new_key_value_tuple_pairs = create_new_key_value_tuple_pairs(settings_list)

                try:
                    ## and then have the GuiJsonUtil apply the new kijiku settings
                    GuiJsonUtil.update_kijiku_settings_with_new_values(input_kijiku_rules_file, new_key_value_tuple_pairs)

                except:
                    raise gr.Error("Invalid Kijiku Settings")

                gr.Info("Kijiku Settings Applied")

##-------------------start-of-reset_to_default_kijiku_settings()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            def reset_to_default_kijiku_settings(input_kijiku_rules_file:gr.File):

                """

                Resets the kijiku settings to the default values.

                """

                if(input_kijiku_rules_file is None):
                    raise gr.Error("No Kijiku Rules File Selected. Cannot reset settings.")

                GuiJsonUtil.current_kijiku_rules = FileEnsurer.DEFAULT_KIJIKU_RULES

                prompt_assembly_mode_value = int(GuiJsonUtil.fetch_kijiku_setting_key_values("base kijiku settings","prompt_assembly_mode"))
                number_of_lines_per_batch_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("base kijiku settings","number_of_lines_per_batch"))
                sentence_fragmenter_mode_value = int(GuiJsonUtil.fetch_kijiku_setting_key_values("base kijiku settings","sentence_fragmenter_mode"))
                je_check_mode_value = int(GuiJsonUtil.fetch_kijiku_setting_key_values("base kijiku settings","je_check_mode"))
                num_malformed_batch_retries_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("base kijiku settings","number_of_malformed_batch_retries"))
                batch_retry_timeout_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("base kijiku settings","batch_retry_timeout"))
                num_concurrent_batches_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("base kijiku settings","number_of_concurrent_batches"))

                openai_model_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("openai settings","openai_model"))
                openai_system_message_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("openai settings","openai_system_message"))
                openai_temperature_value = float(GuiJsonUtil.fetch_kijiku_setting_key_values("openai settings","openai_temperature"))
                openai_top_p_value = float(GuiJsonUtil.fetch_kijiku_setting_key_values("openai settings","openai_top_p"))
                openai_n_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("openai settings","openai_n"))
                openai_stream_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("openai settings","openai_stream"))
                openai_stop_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("openai settings","openai_stop"))
                openai_logit_bias_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("openai settings","openai_logit_bias"))
                openai_max_tokens_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("openai settings","openai_max_tokens"))
                openai_presence_penalty_value = float(GuiJsonUtil.fetch_kijiku_setting_key_values("openai settings","openai_presence_penalty"))
                openai_frequency_penalty_value = float(GuiJsonUtil.fetch_kijiku_setting_key_values("openai settings","openai_frequency_penalty"))

                gemini_model_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("gemini settings","gemini_model"))
                gemini_prompt_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("gemini settings","gemini_prompt"))
                gemini_temperature_value = float(GuiJsonUtil.fetch_kijiku_setting_key_values("gemini settings","gemini_temperature"))
                gemini_top_p_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("gemini settings","gemini_top_p"))
                gemini_top_k_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("gemini settings","gemini_top_k"))
                gemini_candidate_count_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("gemini settings","gemini_candidate_count"))
                gemini_stream_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("gemini settings","gemini_stream"))
                gemini_stop_sequences_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("gemini settings","gemini_stop_sequences"))
                gemini_max_output_tokens_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("gemini settings","gemini_max_output_tokens"))

                return_batch = [
                    prompt_assembly_mode_value,
                    number_of_lines_per_batch_value,
                    sentence_fragmenter_mode_value,
                    je_check_mode_value,
                    num_malformed_batch_retries_value,
                    batch_retry_timeout_value,
                    num_concurrent_batches_value,
                    openai_model_value,
                    openai_system_message_value,
                    openai_temperature_value,
                    openai_top_p_value,
                    openai_n_value,
                    openai_stream_value,
                    openai_stop_value,
                    openai_logit_bias_value,
                    openai_max_tokens_value,
                    openai_presence_penalty_value,
                    openai_frequency_penalty_value,
                    gemini_model_value,
                    gemini_prompt_value,
                    gemini_temperature_value,
                    gemini_top_p_value,
                    gemini_top_k_value,
                    gemini_candidate_count_value,
                    gemini_stream_value,
                    gemini_stop_sequences_value,
                    gemini_max_output_tokens_value
                ]

                gr.Info("Kijiku Settings Reset to Default")

                return return_batch

##-------------------start-of-refresh_kijiku_settings_fields()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            def refresh_kijiku_settings_fields(input_kijiku_rules_file:str):

                """

                Refreshes the kijiku settings fields with the values from the kijiku rules file.                

                """


                if(input_kijiku_rules_file is None):
                    raise gr.Error("No Kijiku Rules File Selected. Cannot refresh settings.")

                ## assume that the user has uploaded a valid kijiku rules file, if it's not, that's on them
                try:
                    GuiJsonUtil.current_kijiku_rules = gui_get_json_from_file(input_kijiku_rules_file)

                    ## update the default values on the Kijiku Settings tab manually
                    prompt_assembly_mode_value = int(GuiJsonUtil.fetch_kijiku_setting_key_values("base kijiku settings","prompt_assembly_mode"))
                    number_of_lines_per_batch_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("base kijiku settings","number_of_lines_per_batch"))
                    sentence_fragmenter_mode_value = int(GuiJsonUtil.fetch_kijiku_setting_key_values("base kijiku settings","sentence_fragmenter_mode"))
                    je_check_mode_value = int(GuiJsonUtil.fetch_kijiku_setting_key_values("base kijiku settings","je_check_mode"))
                    num_malformed_batch_retries_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("base kijiku settings","number_of_malformed_batch_retries"))
                    batch_retry_timeout_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("base kijiku settings","batch_retry_timeout"))
                    num_concurrent_batches_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("base kijiku settings","number_of_concurrent_batches"))

                    openai_model_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("openai settings","openai_model"))
                    openai_system_message_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("openai settings","openai_system_message"))
                    openai_temperature_value = float(GuiJsonUtil.fetch_kijiku_setting_key_values("openai settings","openai_temperature"))
                    openai_top_p_value = float(GuiJsonUtil.fetch_kijiku_setting_key_values("openai settings","openai_top_p"))
                    openai_n_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("openai settings","openai_n"))
                    openai_stream_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("openai settings","openai_stream"))
                    openai_stop_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("openai settings","openai_stop"))
                    openai_logit_bias_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("openai settings","openai_logit_bias"))
                    openai_max_tokens_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("openai settings","openai_max_tokens"))
                    openai_presence_penalty_value = float(GuiJsonUtil.fetch_kijiku_setting_key_values("openai settings","openai_presence_penalty"))
                    openai_frequency_penalty_value = float(GuiJsonUtil.fetch_kijiku_setting_key_values("openai settings","openai_frequency_penalty"))

                    gemini_model_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("gemini settings","gemini_model"))
                    gemini_prompt_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("gemini settings","gemini_prompt"))
                    gemini_temperature_value = float(GuiJsonUtil.fetch_kijiku_setting_key_values("gemini settings","gemini_temperature"))
                    gemini_top_p_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("gemini settings","gemini_top_p"))
                    gemini_top_k_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("gemini settings","gemini_top_k"))
                    gemini_candidate_count_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("gemini settings","gemini_candidate_count"))
                    gemini_stream_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("gemini settings","gemini_stream"))
                    gemini_stop_sequences_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("gemini settings","gemini_stop_sequences"))
                    gemini_max_output_tokens_value = str(GuiJsonUtil.fetch_kijiku_setting_key_values("gemini settings","gemini_max_output_tokens"))

                    return_batch = [
                        prompt_assembly_mode_value,
                        number_of_lines_per_batch_value,
                        sentence_fragmenter_mode_value,
                        je_check_mode_value,
                        num_malformed_batch_retries_value,
                        batch_retry_timeout_value,
                        num_concurrent_batches_value,
                        openai_model_value,
                        openai_system_message_value,
                        openai_temperature_value,
                        openai_top_p_value,
                        openai_n_value,
                        openai_stream_value,
                        openai_stop_value,
                        openai_logit_bias_value,
                        openai_max_tokens_value,
                        openai_presence_penalty_value,
                        openai_frequency_penalty_value,
                        gemini_model_value,
                        gemini_prompt_value,
                        gemini_temperature_value,
                        gemini_top_p_value,
                        gemini_top_k_value,
                        gemini_candidate_count_value,
                        gemini_stream_value,
                        gemini_stop_sequences_value,
                        gemini_max_output_tokens_value
                    ]

                except:

                    GuiJsonUtil.current_kijiku_rules = JsonHandler.current_kijiku_rules
                    raise gr.Error("Invalid Custom Kijiku Rules File")
                
                return return_batch

##-------------------start-of-clear_kijiku_settings_input_fields()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        
            def clear_kijiku_settings_input_fields():                                                                  

                """

                Resets the kijiku settings input fields to None.

                """

                input_kijiku_rules_file = None

                prompt_assembly_mode_value = None
                number_of_lines_per_batch_value = None
                sentence_fragmenter_mode_value = None
                je_check_mode_value = None
                num_malformed_batch_retries_value = None
                batch_retry_timeout_value = None
                num_concurrent_batches_value = None
                
                openai_model_value = None
                openai_system_message_value = None
                openai_temperature_value = None
                openai_top_p_value = None
                openai_n_value = None
                openai_stream_value = None
                openai_stop_value = None
                openai_logit_bias_value = None
                openai_max_tokens_value = None
                openai_presence_penalty_value = None
                openai_frequency_penalty_value = None
                
                gemini_model_value = None
                gemini_prompt_value = None
                gemini_temperature_value = None
                gemini_top_p_value = None
                gemini_top_k_value = None
                gemini_candidate_count_value = None
                gemini_stream_value = None
                gemini_stop_sequences_value = None
                gemini_max_output_tokens_value = None

                return input_kijiku_rules_file, prompt_assembly_mode_value, number_of_lines_per_batch_value, sentence_fragmenter_mode_value, je_check_mode_value, num_malformed_batch_retries_value, batch_retry_timeout_value, num_concurrent_batches_value, openai_model_value, openai_system_message_value, openai_temperature_value, openai_top_p_value, openai_n_value, openai_stream_value, openai_stop_value, openai_logit_bias_value, openai_max_tokens_value, openai_presence_penalty_value, openai_frequency_penalty_value, gemini_model_value, gemini_prompt_value, gemini_temperature_value, gemini_top_p_value, gemini_top_k_value, gemini_candidate_count_value, gemini_stream_value, gemini_stop_sequences_value, gemini_max_output_tokens_value

##-------------------start-of-fetch_log_content()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            def fetch_debug_log_content() -> typing.Tuple[str, str]:
            
                """
                
                Fetches the log content from the log file.

                Returns:
                log_text (str) : The log text.
                logging_tab_error_log_output_field (str) : The error log.

                """

                log_text = FileEnsurer.standard_read_file(Logger.log_file_path)
                logging_tab_error_log_output_field = FileEnsurer.standard_read_file(FileEnsurer.error_log_path)

                return log_text, logging_tab_error_log_output_field
            
##-------------------start-of-send_to_kairyou_button()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            def send_to_kairyou_button(input_text:str) -> str:

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
                
##-------------------start-of-send_to_kaiseki_button()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
                
            def send_to_kaiseki_button(input_text:str) -> str:

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
                
##-------------------start-of-send_to_kijiku_button()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
                
            def send_to_kijiku_button(input_text:str) -> str:

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
                
##-------------------start-of-switch_kijiku_api_key_value()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
                
            def switch_kijiku_api_key_value(llm_type) -> str:

                """
                
                Switches the LLM type value.

                Parameters:
                llm_type (str) : The LLM type.

                Returns:
                llm_type (str) : The LLM type.

                """

                if(llm_type == "OpenAI"):
                    return get_saved_openai_api_key()
                
                else:
                    return get_saved_gemini_api_key()
                
##-------------------start-of-Listener-Declaration---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

##-------------------start-of-load()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.gui.load(webgui_update_check)

            self.gui.load(FileEnsurer.purge_storage)

##-------------------start-of-index()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.indexing_run_button.click(index,
                                            inputs=[
                                                self.input_txt_file_indexing, ## input txt file to index
                                                self.input_json_file_indexing, ## input json file
                                                self.input_knowledge_base_file, ## knowledge base file
                                                self.input_knowledge_base_directory], ## knowledge base directory

                                            outputs=[
                                                self.indexing_output_field, ## indexed text
                                                self.indexing_results_output_field, ## indexing results
                                                self.debug_log_output_field_indexing_tab, ## debug log on indexing tab
                                                self.logging_tab_debug_log_output_field, ## debug log on log tab
                                                self.logging_tab_error_log_output_field])

##-------------------start-of-preprocess()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.preprocessing_run_button.click(fn=preprocess, 
                                                inputs=[
                                                    self.input_txt_file_preprocessing, ## input txt file to preprocess
                                                    self.input_json_file_preprocessing, ## replacements json file
                                                    self.input_text_kairyou], ## input text to preprocess                                                                        

                                                outputs=[
                                                    self.preprocessing_output_field,  ## preprocessed text
                                                    self.preprocessing_results_output_field,  ## kairyou results
                                                    self.debug_log_output_field_preprocess_tab, ## debug log on preprocess tab
                                                    self.logging_tab_debug_log_output_field, ## debug log on log tab
                                                    self.logging_tab_error_log_output_field]) ## error log on log tab
            

            
##-------------------start-of-kaiseki_translate_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            ## for the actual translation, and the je check text
            kaiseki_translation_process = self.kaiseki_translate_button.click(translate_with_kaiseki,
                                                inputs=[
                                                    self.input_txt_file_kaiseki, ## input txt file to translate
                                                    self.input_text_kaiseki, ## input text to translate
                                                    self.kaiseki_api_key_input_field], ## api key input
                                                
                                                outputs=[
                                                    self.kaiseki_translated_text_output_field, ## translated text
                                                    self.kaiseki_je_check_text_output_field, ## je check text field on kaiseki tab
                                                    self.logging_tab_debug_log_output_field, ## debug log on log tab
                                                    self.logging_tab_error_log_output_field]) ## error log on log tab
            ## for the kaiseki debug log
            self.kaiseki_translate_button.click(fn=fetch_log_content,
                                                inputs=[],

                                                outputs=[self.kaiseki_debug_log_output_field], ## debug log on kaiseki tab

                                                every=.1) ## update every 100ms
            

##-------------------start-of-translate_with_kijiku()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            ## for the actual translation, and the je check text
            kijiku_translation_process = self.kijiku_translate_button.click(translate_with_kijiku,
                                                inputs=[
                                                    self.input_txt_file_kijiku, ## input txt file to translate
                                                    self.input_text_kijiku, ## input text to translate
                                                    self.kijiku_api_key_input, ## api key input
                                                    self.llm_option_dropdown, ## llm option dropdown
                                                    self.input_kijiku_rules_file], ## kijiku rules file
                                                
                                                outputs=[
                                                    self.kijiku_translated_text_output_field, ## translated text
                                                    self.kijiku_je_check_text_output_field, ## je check text field on kijiku tab
                                                    self.logging_tab_debug_log_output_field , ## debug log on log tab
                                                    self.logging_tab_error_log_output_field]) ## error log on log tab
            ## for the kijiku debug log
            self.kijiku_translate_button.click(fn=fetch_log_content,
                                                inputs=[],

                                                outputs=[self.kijiku_debug_log_output_field], ## debug log on kijiku tab

                                                every=.1) ## update every 100ms
            

##-------------------start-of-kijiku_calculate_costs_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            self.kijiku_calculate_costs_button.click(kijiku_calculate_costs_button_click,
                                                        inputs=[
                                                            self.input_txt_file_kijiku, ## input txt file to calculate costs
                                                            self.input_text_kijiku,
                                                            self.llm_option_dropdown,
                                                            self.kijiku_api_key_input,
                                                            self.input_kijiku_rules_file], ## kijiku rules file
                
                                                        outputs=[self.kijiku_translated_text_output_field]) ## functions as an output field for the cost output field
            
##-------------------start-of-clear_index_tab()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.indexing_clear_button.click(clear_index_tab,
                                            inputs=[],
                                            
                                            outputs=[
                                                self.input_txt_file_indexing, ## input txt file
                                                self.input_json_file_indexing, ## input json file
                                                self.input_knowledge_base_file, ## knowledge base file
                                                self.input_knowledge_base_directory, ## knowledge base directory
                                                self.indexing_output_field, ## indexing output field
                                                self.indexing_results_output_field, ## indexing results output field
                                                self.debug_log_output_field_indexing_tab]) ## debug log on indexing tab
            
##-------------------start-of-clear_preprocessing_tab()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.preprocessing_clear_button.click(clear_preprocessing_tab,
                                                  inputs=[],

                                                  outputs=[
                                                      self.input_txt_file_preprocessing, ## input txt file
                                                      self.input_json_file_preprocessing, ## input json file
                                                      self.input_text_kairyou, ## input text
                                                      self.preprocessing_output_field, ## preprocessed text output field
                                                      self.preprocessing_results_output_field, ## preprocessing results output field
                                                      self.debug_log_output_field_preprocess_tab])## debug log on preprocess tab

##-------------------start-of-clear_button_kaiseki_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.kaiseki_clear_button.click(clear_kaiseki_tab,
                                            inputs=[],

                                            outputs=[
                                                self.input_txt_file_kaiseki, ## input txt file
                                                self.input_text_kaiseki, ## input text
                                                self.kaiseki_translated_text_output_field, ## translation output field
                                                self.kaiseki_je_check_text_output_field, ## je check text field on kaiseki tab
                                                self.kaiseki_debug_log_output_field], ## debug log on kaiseki tab

                                            cancels=kaiseki_translation_process) ## cancels the translation process
##-------------------start-of-clear_button_kijiku_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            self.kijiku_clear_button.click(clear_kijiku_tab,
                                            inputs=[],

                                            outputs=[
                                                self.input_txt_file_kijiku, ## input txt file
                                                self.input_text_kijiku, ## input text
                                                self.input_kijiku_rules_file, ## kijiku rules file
                                                self.kijiku_translated_text_output_field, ## translation output field
                                                self.kijiku_je_check_text_output_field, ## je check text field on kijiku tab
                                                self.kijiku_debug_log_output_field], ## debug log on kijiku tab
            
                                            cancels=kijiku_translation_process)
##-------------------start-of-clear_log_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.logging_clear_logs_button.click(clear_log_button_click,
                                        inputs=[],

                                        outputs=[
                                            self.logging_tab_debug_log_output_field,
                                            self.logging_tab_error_log_output_field])
            
##-------------------start-of-apply_new_kijiku_settings()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            self.kijiku_settings_apply_changes_button.click(apply_new_kijiku_settings,
                                            inputs=[
                                                self.input_kijiku_rules_file, ## kijiku rules file
                                                self.prompt_assembly_mode_input_field, ## prompt assembly mode input field
                                                self.number_of_lines_per_batch_input_field, ## num lines input field
                                                self.sentence_fragmenter_mode_input_field, ## sentence fragmenter mode input field
                                                self.je_check_mode_input_field, ## je check mode input field
                                                self.number_of_malformed_batch_retries_input_field, ## num malformed batch retries input field
                                                self.batch_retry_timeout_input_field, ## batch retry timeout input field
                                                self.number_of_concurrent_batches_input_field, ## num concurrent batches input field
                                                self.openai_model_input_field, ## openai model input field
                                                self.openai_system_message_input_field, ## openai system message input field
                                                self.openai_temperature_input_field, ## openai temperature input field
                                                self.openai_top_p_input_field, ## openai top p input field
                                                self.openai_n_input_field, ## openai n input field
                                                self.openai_stream_input_field, ## openai stream input field
                                                self.openai_stop_input_field, ## openai stop input field
                                                self.openai_logit_bias_input_field, ## openai logit bias input field
                                                self.openai_max_tokens_input_field, ## openai max tokens input field
                                                self.openai_presence_penalty_input_field, ## openai presence penalty input field
                                                self.openai_frequency_penalty_input_field, ## openai frequency penalty input field
                                                self.gemini_model_input_field, ## gemini model input field
                                                self.gemini_prompt_input_field, ## gemini prompt input field
                                                self.gemini_temperature_input_field, ## gemini temperature input field
                                                self.gemini_top_p_input_field, ## gemini top p input field
                                                self.gemini_top_k_input_field, ## gemini top k input field
                                                self.gemini_candidate_count_input_field, ## gemini candidate count input field
                                                self.gemini_stream_input_field, ## gemini stream input field
                                                self.gemini_stop_sequences_input_field, ## gemini stop sequences input field
                                                self.gemini_max_output_tokens_input_field], ## gemini max output tokens input field
                                            
                                            outputs=[])
            
##-------------------start-of-reset_to_default_kijiku_settings_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            self.kijiku_settings_reset_to_default_button.click(reset_to_default_kijiku_settings,
                                                inputs=[self.input_kijiku_rules_file],
                                                
                                                outputs=[
                                                        self.prompt_assembly_mode_input_field, ## prompt assembly mode input field
                                                        self.number_of_lines_per_batch_input_field, ## num lines input field
                                                        self.sentence_fragmenter_mode_input_field, ## sentence fragmenter mode input field
                                                        self.je_check_mode_input_field, ## je check mode input field
                                                        self.number_of_malformed_batch_retries_input_field, ## num malformed batch retries input field
                                                        self.batch_retry_timeout_input_field, ## batch retry timeout input field
                                                        self.number_of_concurrent_batches_input_field, ## num concurrent batches input field
                                                        self.openai_model_input_field, ## openai model input field
                                                        self.openai_system_message_input_field, ## openai system message input field
                                                        self.openai_temperature_input_field, ## openai temperature input field
                                                        self.openai_top_p_input_field, ## openai top p input field
                                                        self.openai_n_input_field, ## openai n input field
                                                        self.openai_stream_input_field, ## openai stream input field
                                                        self.openai_stop_input_field, ## openai stop input field
                                                        self.openai_logit_bias_input_field, ## openai logit bias input field
                                                        self.openai_max_tokens_input_field, ## openai max tokens input field
                                                        self.openai_presence_penalty_input_field, ## openai presence penalty input field
                                                        self.openai_frequency_penalty_input_field, ## openai frequency penalty input field
                                                        self.gemini_model_input_field, ## gemini model input field
                                                        self.gemini_prompt_input_field, ## gemini prompt input field
                                                        self.gemini_temperature_input_field, ## gemini temperature input field
                                                        self.gemini_top_p_input_field, ## gemini top p input field
                                                        self.gemini_top_k_input_field, ## gemini top k input field
                                                        self.gemini_candidate_count_input_field, ## gemini candidate count input field
                                                        self.gemini_stream_input_field, ## gemini stream input field
                                                        self.gemini_stop_sequences_input_field, ## gemini stop sequences input field
                                                        self.gemini_max_output_tokens_input_field])

##-------------------start-of-discard_changes_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            self.kijiku_settings_discard_changes_button.click(refresh_kijiku_settings_fields,
                                              inputs=[self.input_kijiku_rules_file],
                                              
                                              outputs=[
                                                    self.prompt_assembly_mode_input_field, ## prompt assembly mode input field
                                                    self.number_of_lines_per_batch_input_field, ## num lines input field
                                                    self.sentence_fragmenter_mode_input_field, ## sentence fragmenter mode input field
                                                    self.je_check_mode_input_field, ## je check mode input field
                                                    self.number_of_malformed_batch_retries_input_field, ## num malformed batch retries input field
                                                    self.batch_retry_timeout_input_field, ## batch retry timeout input field
                                                    self.number_of_concurrent_batches_input_field, ## num concurrent batches input field
                                                    self.openai_model_input_field, ## openai model input field
                                                    self.openai_system_message_input_field, ## openai system message input field
                                                    self.openai_temperature_input_field, ## openai temperature input field
                                                    self.openai_top_p_input_field, ## openai top p input field
                                                    self.openai_n_input_field, ## openai n input field
                                                    self.openai_stream_input_field, ## openai stream input field
                                                    self.openai_stop_input_field, ## openai stop input field
                                                    self.openai_logit_bias_input_field, ## openai logit bias input field
                                                    self.openai_max_tokens_input_field, ## openai max tokens input field
                                                    self.openai_presence_penalty_input_field, ## openai presence penalty input field
                                                    self.openai_frequency_penalty_input_field, ## openai frequency penalty input field
                                                    self.gemini_model_input_field, ## gemini model input field
                                                    self.gemini_prompt_input_field, ## gemini prompt input field
                                                    self.gemini_temperature_input_field, ## gemini temperature input field
                                                    self.gemini_top_p_input_field, ## gemini top p input field
                                                    self.gemini_top_k_input_field, ## gemini top k input field
                                                    self.gemini_candidate_count_input_field, ## gemini candidate count input field
                                                    self.gemini_stream_input_field, ## gemini stream input field
                                                    self.gemini_stop_sequences_input_field, ## gemini stop sequences input field
                                                    self.gemini_max_output_tokens_input_field]) ## gemini max output tokens input field


##-------------------start-of-input_kijiku_rules_file_upload()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            self.input_kijiku_rules_file.upload(refresh_kijiku_settings_fields,
                                                inputs=[self.input_kijiku_rules_file],
                                                
                                                outputs=[
                                                    self.prompt_assembly_mode_input_field, ## prompt assembly mode input field
                                                    self.number_of_lines_per_batch_input_field, ## num lines input field
                                                    self.sentence_fragmenter_mode_input_field, ## sentence fragmenter mode input field
                                                    self.je_check_mode_input_field, ## je check mode input field
                                                    self.number_of_malformed_batch_retries_input_field, ## num malformed batch retries input field
                                                    self.batch_retry_timeout_input_field, ## batch retry timeout input field
                                                    self.number_of_concurrent_batches_input_field, ## num concurrent batches input field
                                                    self.openai_model_input_field, ## openai model input field
                                                    self.openai_system_message_input_field, ## openai system message input field
                                                    self.openai_temperature_input_field, ## openai temperature input field
                                                    self.openai_top_p_input_field, ## openai top p input field
                                                    self.openai_n_input_field, ## openai n input field
                                                    self.openai_stream_input_field, ## openai stream input field
                                                    self.openai_stop_input_field, ## openai stop input field
                                                    self.openai_logit_bias_input_field, ## openai logit bias input field
                                                    self.openai_max_tokens_input_field, ## openai max tokens input field
                                                    self.openai_presence_penalty_input_field, ## openai presence penalty input field
                                                    self.openai_frequency_penalty_input_field, ## openai frequency penalty input field
                                                    self.gemini_model_input_field, ## gemini model input field
                                                    self.gemini_prompt_input_field, ## gemini prompt input field
                                                    self.gemini_temperature_input_field, ## gemini temperature input field
                                                    self.gemini_top_p_input_field, ## gemini top p input field
                                                    self.gemini_top_k_input_field, ## gemini top k input field
                                                    self.gemini_candidate_count_input_field, ## gemini candidate count input field
                                                    self.gemini_stream_input_field, ## gemini stream input field
                                                    self.gemini_stop_sequences_input_field, ## gemini stop sequences input field
                                                    self.gemini_max_output_tokens_input_field]) 
            
            self.input_kijiku_rules_file.clear(clear_kijiku_settings_input_fields,
                                                inputs=[],
                                                
                                                outputs=[
                                                    self.input_kijiku_rules_file, ## kijiku rules file
                                                    self.prompt_assembly_mode_input_field, ## prompt assembly mode input field
                                                    self.number_of_lines_per_batch_input_field, ## num lines input field
                                                    self.sentence_fragmenter_mode_input_field, ## sentence fragmenter mode input field
                                                    self.je_check_mode_input_field, ## je check mode input field
                                                    self.number_of_malformed_batch_retries_input_field, ## num malformed batch retries input field
                                                    self.batch_retry_timeout_input_field, ## batch retry timeout input field
                                                    self.number_of_concurrent_batches_input_field, ## num concurrent batches input field
                                                    self.openai_model_input_field, ## openai model input field
                                                    self.openai_system_message_input_field, ## openai system message input field
                                                    self.openai_temperature_input_field, ## openai temperature input field
                                                    self.openai_top_p_input_field, ## openai top p input field
                                                    self.openai_n_input_field, ## openai n input field
                                                    self.openai_stream_input_field, ## openai stream input field
                                                    self.openai_stop_input_field, ## openai stop input field
                                                    self.openai_logit_bias_input_field, ## openai logit bias input field
                                                    self.openai_max_tokens_input_field, ## openai max tokens input field
                                                    self.openai_presence_penalty_input_field, ## openai presence penalty input field
                                                    self.openai_frequency_penalty_input_field, ## openai frequency penalty input field
                                                    self.gemini_model_input_field, ## gemini model input field
                                                    self.gemini_prompt_input_field, ## gemini prompt input field
                                                    self.gemini_temperature_input_field, ## gemini temperature input field
                                                    self.gemini_top_p_input_field, ## gemini top p input field
                                                    self.gemini_top_k_input_field, ## gemini top k input field
                                                    self.gemini_candidate_count_input_field, ## gemini candidate count input field
                                                    self.gemini_stream_input_field, ## gemini stream input field
                                                    self.gemini_stop_sequences_input_field, ## gemini stop sequences input field
                                                    self.gemini_max_output_tokens_input_field])

##-------------------start-of-logging_tab.select()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.logging_tab.select(fetch_debug_log_content,
                                    inputs=[],
                                    
                                    outputs=[self.logging_tab_debug_log_output_field, self.logging_tab_error_log_output_field])
            
##-------------------start-of-kijiku_api_key_input.change()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.llm_option_dropdown.change(switch_kijiku_api_key_value,
                                             inputs=[self.llm_option_dropdown],
                                            
                                            outputs=[self.kijiku_api_key_input])
            
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
                inputs=[self.preprocessing_output_field],

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
                js=(self.save_as_js).replace("downloaded_text.txt", "preprocessing_debug_log_.txt")
            )

##-------------------start-of-save_to_file_kaiseki_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.save_to_file_kaiseki_translated_text.click(lambda text: text, ## save text as is
                inputs=[self.kaiseki_translated_text_output_field],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                js=(self.save_as_js).replace("downloaded_text.txt", "translated_text_kaiseki.txt")
            )

##-------------------start-of-save_to_file_je_check_text_kaiseki_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.save_to_file_kaiseki_je_check_text.click(lambda text: text, ## save text as is
                inputs=[self.kaiseki_je_check_text_output_field],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                js=(self.save_as_js).replace("downloaded_text.txt", "je_check_text_kaiseki.txt")
            )

##-------------------start-of-save_to_file_debug_log_kaiseki_tab_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.save_to_file_debug_log_kaiseki_tab.click(lambda text: text, ## save text as is
                inputs=[self.kaiseki_debug_log_output_field],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                js=(self.save_as_js).replace("downloaded_text.txt", "debug_log_kaiseki.txt")
            )

##-------------------start-of-save_to_file_kijiku_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            self.save_to_file_kijiku_translated_text.click(lambda text: text, ## save text as is
                inputs=[self.kijiku_translated_text_output_field],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                js=(self.save_as_js).replace("downloaded_text.txt", "translated_text_kijiku.txt")
            )

##-------------------start-of-save_to_file_je_check_text_kijiku_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            self.save_to_file_kijiku_je_check_text.click(lambda text: text, ## save text as is
                inputs=[self.kijiku_je_check_text_output_field],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                js=(self.save_as_js).replace("downloaded_text.txt", "je_check_text_kijiku.txt")
            )

##-------------------start-of-save_to_file_debug_log_kijiku_tab_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            self.save_to_file_debug_log_kijiku_tab.click(lambda text: text, ## save text as is
                inputs=[self.kijiku_debug_log_output_field],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                js=(self.save_as_js).replace("downloaded_text.txt", "debug_log_kijiku.txt")
            )

##-------------------start-of-save_to_file_debug_log_logging_tab_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.save_to_file_debug_log_logging_tab.click(lambda text: text, ## save text as is
                inputs=[self.logging_tab_debug_log_output_field],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                js=(self.save_as_js).replace("downloaded_text.txt", "debug_log_all.txt")
            )

##-------------------start-of-save_to_file_error_log_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.save_to_file_error_log_logging_tab.click(lambda text: text, ## save text as is
                inputs=[self.logging_tab_error_log_output_field],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                js=(self.save_as_js).replace("downloaded_text.txt", "error_log.txt")
            )

##-------------------start-of-send_to_x_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.send_to_kairyou_button.click(fn=send_to_kairyou_button, 
                                        inputs=[self.indexing_output_field],
                                        outputs=[self.input_text_kairyou])
                                        
            self.send_to_kaiseki_button.click(fn=send_to_kaiseki_button,
                                        inputs=[self.preprocessing_output_field],
                                        outputs=[self.input_text_kaiseki])
            
            self.send_to_kijiku_button.click(fn=send_to_kijiku_button,
                                        inputs=[self.preprocessing_output_field],
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