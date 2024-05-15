## built-in libraries
import typing
import base64

## third-party libraries
import gradio as gr

from kairyou import Indexer
from kairyou import Kairyou
from kairyou import InvalidReplacementJsonKeys
from kairyou.util import _validate_replacement_json

from easytl import EasyTL, ALLOWED_GEMINI_MODELS, ALLOWED_OPENAI_MODELS

## custom modules
from modules.common.toolkit import Toolkit
from modules.common.file_ensurer import FileEnsurer

from modules.gui.gui_file_util import gui_get_text_from_file, gui_get_json_from_file
from modules.gui.gui_json_util import GuiJsonUtil

from handlers.json_handler import JsonHandler

from modules.common.translator import Translator

from kudasai import Kudasai

##-------------------start-of-KudasaiGUI---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class KudasaiGUI:

    """
    
    KudasaiGUI is a class that contains the GUI for Kudasai.

    """

    ## scary javascript code that allows us to save textbox contents to a file
    with open(FileEnsurer.js_save_to_file_path, 'r', encoding='utf-8') as f:
        js_save_to_file = f.read()

    ## used for whether the debug log tab for Translator should be actively refreshing based of Logger.current_batch
    is_translation_ongoing = False

    with open(FileEnsurer.translation_settings_description_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    description_dict = {
        "prompt_assembly_mode": lines[4-1].strip(),
        "number_of_lines_per_batch": lines[6-1].strip(),
        "sentence_fragmenter_mode": lines[8-1].strip(),
        "je_check_mode": lines[10-1].strip(),
        "number_of_malformed_batch_retries": lines[12-1].strip(),
        "batch_retry_timeout": lines[14-1].strip(),
        "number_of_concurrent_batches": lines[16-1].strip(),
        "openai_help_link": lines[19-1].strip(),
        "openai_model": lines[21-1].strip(),
        "openai_system_message": lines[23-1].strip(),
        "openai_temperature": lines[25-1].strip(),
        "openai_top_p": lines[27-1].strip(),
        "openai_n": lines[29-1].strip(),
        "openai_stream": lines[31-1].strip(),
        "openai_stop": lines[33-1].strip(),
        "openai_logit_bias": lines[35-1].strip(),
        "openai_max_tokens": lines[37-1].strip(),
        "openai_presence_penalty": lines[39-1].strip(),
        "openai_frequency_penalty": lines[41-1].strip(),
        "openai_disclaimer": lines[43-1].strip(),
        "gemini_help_link": lines[46-1].strip(),
        "gemini_model": lines[48-1].strip(),
        "gemini_prompt": lines[50-1].strip(),
        "gemini_temperature": lines[52-1].strip(),
        "gemini_top_p": lines[54-1].strip(),
        "gemini_top_k": lines[56-1].strip(),
        "gemini_candidate_count": lines[58-1].strip(),
        "gemini_stream": lines[60-1].strip(),
        "gemini_stop_sequences": lines[62-1].strip(),
        "gemini_max_output_tokens": lines[64-1].strip(),
        "gemini_disclaimer": lines[66-1].strip(),
        "deepl_help_link": lines[69-1].strip(),
        "deepl_context": lines[71-1].strip(),
        "deepl_split_sentences": lines[73-1].strip(),
        "deepl_preserve_formatting": lines[75-1].strip(),
        "deepl_formality": lines[77-1].strip(),
    }

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

                with open(FileEnsurer.debug_log_path, 'r', encoding='utf-8') as f:
                    log_text = f.read()
                
                return log_text
            

##-------------------start-of-get_saved_api_key()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            @staticmethod
            def get_saved_api_key(service_name:typing.Literal["openai","gemini","deepl"]) -> str:

                """
                Gets the saved api key from the config folder, if it exists.

                Parameters:
                service_name (str): The name of the service (e.g., "deepl", "openai", "gemini").

                Returns:
                api_key (str) : The api key.

                """

                service_to_path = {
                    "openai": FileEnsurer.openai_api_key_path,
                    "gemini": FileEnsurer.gemini_api_key_path,
                    "deepl": FileEnsurer.deepl_api_key_path
                }

                api_key_path = service_to_path.get(service_name, "")


                try:
                    ## Api key is encoded in base 64 so we need to decode it before returning
                    return base64.b64decode(FileEnsurer.standard_read_file(api_key_path).encode('utf-8')).decode('utf-8')
                
                except:
                    return ""
                
##-------------------start-of-set_translator_api_key()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
                
            async def set_translator_api_key(api_key) -> None:

                """

                Sets the translator api key.

                Parameters:
                api_key (str) : The api key.

                """

                try:

                    EasyTL.set_credentials(Translator.TRANSLATION_METHOD, str(api_key))
                    is_valid, e = EasyTL.test_credentials(Translator.TRANSLATION_METHOD)


                    if(is_valid == False and e is not None):
                        raise e
                    
                except:
                    raise gr.Error("Invalid API key")
                
##-------------------start-of-update_translator_api_key()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
                
            def update_translator_api_key(api_key) -> None:

                """

                Updates the translator api key.

                Parameters:
                api_key (str) : The api key.

                """

                method_to_path = {
                    "openai": FileEnsurer.openai_api_key_path,
                    "gemini": FileEnsurer.gemini_api_key_path,
                    "deepl": FileEnsurer.deepl_api_key_path
                }

                path_to_api_key = method_to_path.get(Translator.TRANSLATION_METHOD, None)

                assert path_to_api_key is not None, "Invalid translation method"

                FileEnsurer.standard_overwrite_file(path_to_api_key, base64.b64encode(str(api_key).encode('utf-8')).decode('utf-8'), omit=True)

##-------------------start-of-create_new_key_value_tuple_pairs()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------    

            def create_new_key_value_tuple_pairs(translation_settings:typing.List[str]) -> typing.List[typing.Tuple[str, str]]:
                
                """

                Applies the new translation to the uploaded translation_settings.json file.

                Parameters:
                translation_settings (typing.List[typing.Union[gr.Textbox,gr.Slider,gr.Dropdown]]) : The translation settings.

                Returns:
                key_value_tuple_pairs (typing.List[typing.Tuple[str, str]]) : The new key value tuple pairs.

                """

                key_value_tuple_pairs = []
                
                translation_settings_key_names = {
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
                    26: "gemini_max_output_tokens",
                    27: "deepl_context",
                    28: "deepl_split_sentences",
                    29: "deepl_preserve_formatting",
                    30: "deepl_formality",
                }

                for index, setting in enumerate(translation_settings):
                    key = translation_settings_key_names.get(index)

                    key_value_tuple_pairs.append((key, setting))

                return key_value_tuple_pairs
            
##-------------------start-of-GUI-Structure---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            ## tab 1 | Main
            with gr.Tab("Kudasai") as self.kudasai_tab:

                ## tab 2 | indexing
                with gr.Tab("Name Indexing | Kairyou") as self.indexing_tab:
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
                                self.send_to_kairyou_button = gr.Button('Send to Preprocessing (Kairyou)')

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
                with gr.Tab("Text Preprocessing | Kairyou") as self.preprocessing_tab:
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
                                self.send_to_translator_button = gr.Button('Send to Translator')

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

                ## tab 4 | Translation
                with gr.Tab("Text Translation | Translator") as self.translator_tab:
                    with gr.Row():

                        ## input file or text input, gui allows for both but will prioritize file input
                        with gr.Column():
                            self.input_txt_file_translator = gr.File(label='TXT file with Japanese Text', file_count='single', file_types=['.txt'], type='filepath', interactive=True)
                            self.input_text_translator = gr.Textbox(label='Japanese Text', placeholder='Use this or the text file input, if you provide both, Kudasai will use the file input.', lines=10, show_label=True, interactive=True, type='text')
                            self.input_translation_rules_file = gr.File(value = FileEnsurer.config_translation_settings_path, label='Translation Settings File', file_count='single', file_types=['.json'], type='filepath')

                            with gr.Row():
                                self.llm_option_dropdown = gr.Dropdown(label='Translation Method', choices=["OpenAI", "Gemini", "DeepL"], value="OpenAI", show_label=True, interactive=True)
                            
                            with gr.Row():
                                self.translator_api_key_input = gr.Textbox(label='API Key', value=get_saved_api_key("openai"), lines=1, max_lines=2, show_label=True, interactive=True, type='password')

                            with gr.Row():
                                self.translator_translate_button = gr.Button('Translate', variant="primary")
                                self.translator_calculate_cost_button = gr.Button('Calculate Cost', variant='secondary')

                            with gr.Row():
                                self.translator_clear_button = gr.Button('Clear', variant='stop')

                        ## output fields
                        with gr.Column():
                            self.translator_translated_text_output_field = gr.Textbox(label='Translated Text', lines=43,max_lines=43, interactive=False, show_copy_button=True)

                            with gr.Row():
                                self.save_to_file_translator_translated_text = gr.Button('Save As')

                        with gr.Column():
                            self.translator_je_check_text_output_field = gr.Textbox(label='JE Check Text', lines=43,max_lines=43, interactive=False, show_copy_button=True)

                            with gr.Row():
                                self.save_to_file_translator_je_check_text = gr.Button('Save As')

                        with gr.Column():
                            self.translator_debug_log_output_field = gr.Textbox(label='Debug Log', lines=43, max_lines=43, interactive=False, show_copy_button=True)

                            with gr.Row():
                                self.save_to_file_debug_log_translator_tab = gr.Button('Save As')

                ## tab 5 | Settings
                with gr.Tab("Translation Settings") as self.translation_settings_tab:
                    with gr.Row():

                        with gr.Column():
                            gr.Markdown("Base Translation Settings")
                            gr.Markdown("These settings are used for OpenAI, Gemini, and DeepL.")
                            gr.Markdown("Please ensure to thoroughly read and understand these settings before making any modifications. Each setting has a specific impact on the translation methods. Some settings may affect one or two translation methods, but not the others. Incorrect adjustments could lead to unexpected results or errors in the translation process.")


                            self.prompt_assembly_mode_input_field = gr.Dropdown(label='Prompt Assembly Mode',
                                                                                value=int(GuiJsonUtil.fetch_translation_settings_key_values("base translation settings","prompt_assembly_mode")),
                                                                                choices=[1,2],
                                                                                info=KudasaiGUI.description_dict.get("prompt_assembly_mode", "An error occurred while fetching the description for this setting."),
                                                                                show_label=True,
                                                                                interactive=True,
                                                                                elem_id="prompt_assembly_mode")
                            
                            self.number_of_lines_per_batch_input_field = gr.Textbox(label='Number of Lines Per Batch',
                                                                                    value=(GuiJsonUtil.fetch_translation_settings_key_values("base translation settings","number_of_lines_per_batch")),
                                                                                    info=KudasaiGUI.description_dict.get("number_of_lines_per_batch"),
                                                                                    lines=1,
                                                                                    max_lines=1,
                                                                                    show_label=True,
                                                                                    interactive=True,
                                                                                    elem_id="number_of_lines_per_batch",
                                                                                    show_copy_button=True)
                            
                            self.sentence_fragmenter_mode_input_field = gr.Dropdown(label='Sentence Fragmenter Mode',
                                                                                    value=int(GuiJsonUtil.fetch_translation_settings_key_values("base translation settings","sentence_fragmenter_mode")),
                                                                                    choices=[1,2],
                                                                                    info=KudasaiGUI.description_dict.get("sentence_fragmenter_mode"),
                                                                                    show_label=True,
                                                                                    interactive=True,
                                                                                    elem_id="sentence_fragmenter_mode")
                            
                            self.je_check_mode_input_field = gr.Dropdown(label='JE Check Mode',
                                                                        value=int(GuiJsonUtil.fetch_translation_settings_key_values("base translation settings","je_check_mode")),
                                                                        choices=[1,2],
                                                                        info=KudasaiGUI.description_dict.get("je_check_mode"),
                                                                        show_label=True,
                                                                        interactive=True,
                                                                        elem_id="je_check_mode")
                            
                            self.number_of_malformed_batch_retries_input_field = gr.Textbox(label="Number Of Malformed Batch Retries",
                                                                                value=GuiJsonUtil.fetch_translation_settings_key_values("base translation settings","number_of_malformed_batch_retries"),
                                                                                info=KudasaiGUI.description_dict.get("number_of_malformed_batch_retries"),
                                                                                lines=1,
                                                                                max_lines=1,
                                                                                show_label=True,
                                                                                interactive=True,
                                                                                elem_id="number_of_malformed_batch_retries",
                                                                                show_copy_button=True)
                                                        
                            self.batch_retry_timeout_input_field = gr.Textbox(label="Batch Retry Timeout",
                                                                            value=GuiJsonUtil.fetch_translation_settings_key_values("base translation settings","batch_retry_timeout"),
                                                                            info=KudasaiGUI.description_dict.get("batch_retry_timeout"),
                                                                            lines=1,
                                                                            max_lines=1,
                                                                            show_label=True,
                                                                            interactive=True,
                                                                            elem_id="batch_retry_timeout",
                                                                            show_copy_button=True)

                            self.number_of_concurrent_batches_input_field = gr.Textbox(label="Number Of Concurrent Batches",
                                                                                       value=GuiJsonUtil.fetch_translation_settings_key_values("base translation settings","number_of_concurrent_batches"),
                                                                                        info=KudasaiGUI.description_dict.get("number_of_concurrent_batches"),
                                                                                        lines=1,
                                                                                        max_lines=1,
                                                                                        show_label=True,
                                                                                        interactive=True,
                                                                                        elem_id="number_of_concurrent_batches",
                                                                                        show_copy_button=True)

                        with gr.Column(): 

                            ## all these need to be changed later as well

                            gr.Markdown("OpenAI API Settings")
                            gr.Markdown(str(KudasaiGUI.description_dict.get("openai_help_link")))
                            gr.Markdown(str(KudasaiGUI.description_dict.get("openai_disclaimer")))

                            self.openai_model_input_field = gr.Dropdown(label="OpenAI Model",
                                                                        value=str(GuiJsonUtil.fetch_translation_settings_key_values("openai settings","openai_model")),
                                                                        choices=[model for model in ALLOWED_OPENAI_MODELS],
                                                                        info=KudasaiGUI.description_dict.get("openai_model"),
                                                                        show_label=True,
                                                                        interactive=True,
                                                                        elem_id="openai_model")
                            
                            self.openai_system_message_input_field = gr.Textbox(label="OpenAI System Message",
                                                                            value=str(GuiJsonUtil.fetch_translation_settings_key_values("openai settings","openai_system_message")),
                                                                            info=KudasaiGUI.description_dict.get("openai_system_message"),
                                                                            lines=1,
                                                                            max_lines=1,
                                                                            show_label=True,
                                                                            interactive=True,
                                                                            elem_id="openai_system_message",
                                                                            show_copy_button=True)
                            
                            self.openai_temperature_input_field = gr.Slider(label="OpenAI Temperature",
                                                                        value=float(GuiJsonUtil.fetch_translation_settings_key_values("openai settings","openai_temperature")),
                                                                        minimum=0.0,
                                                                        maximum=2.0,
                                                                        info=KudasaiGUI.description_dict.get("openai_temperature"),
                                                                        interactive=True,
                                                                        elem_id="openai_temperature")
                            
                            self.openai_top_p_input_field = gr.Slider(label="OpenAI Top P",
                                                                    value=float(GuiJsonUtil.fetch_translation_settings_key_values("openai settings","openai_top_p")),
                                                                    minimum=0.0,
                                                                    maximum=1.0,
                                                                    info=KudasaiGUI.description_dict.get("openai_top_p"),
                                                                    show_label=True,
                                                                    interactive=True,
                                                                    elem_id="openai_top_p")
                            
                            self.openai_n_input_field = gr.Textbox(label="OpenAI N",
                                                                value=str(GuiJsonUtil.fetch_translation_settings_key_values("openai settings","openai_n")),
                                                                info=KudasaiGUI.description_dict.get("openai_n"),
                                                                show_label=True,
                                                                interactive=False,
                                                                elem_id="openai_n",
                                                                show_copy_button=True)
                            
                            self.openai_stream_input_field = gr.Textbox(label="OpenAI Stream",
                                                                    value=str(GuiJsonUtil.fetch_translation_settings_key_values("openai settings","openai_stream")),
                                                                    info=KudasaiGUI.description_dict.get("openai_stream"),
                                                                    show_label=True,
                                                                    interactive=False,
                                                                    elem_id="openai_stream",
                                                                    show_copy_button=True)
                            
                            self.openai_stop_input_field = gr.Textbox(label="OpenAI Stop",
                                                                    value=str(GuiJsonUtil.fetch_translation_settings_key_values("openai settings","openai_stop")),
                                                                    info=KudasaiGUI.description_dict.get("openai_stop"),
                                                                    show_label=True,
                                                                    interactive=False,
                                                                    elem_id="openai_stop",
                                                                    show_copy_button=True)
                            
                            self.openai_logit_bias_input_field = gr.Textbox(label="OpenAI Logit Bias",
                                                                        value=str(GuiJsonUtil.fetch_translation_settings_key_values("openai settings","openai_logit_bias")),
                                                                        info=KudasaiGUI.description_dict.get("openai_logit_bias"),
                                                                        show_label=True,
                                                                        interactive=False,
                                                                        elem_id="openai_logit_bias",
                                                                        show_copy_button=True)
                            
                            self.openai_max_tokens_input_field = gr.Textbox(label="OpenAI Max Tokens",
                                                                        value=str(GuiJsonUtil.fetch_translation_settings_key_values("openai settings","openai_max_tokens")),
                                                                        info=KudasaiGUI.description_dict.get("openai_max_tokens"),
                                                                        lines=1,
                                                                        max_lines=1,
                                                                        show_label=True,
                                                                        interactive=True,
                                                                        elem_id="openai_max_tokens",
                                                                        show_copy_button=True)
                            
                            self.openai_presence_penalty_input_field = gr.Slider(label="OpenAI Presence Penalty",
                                                                        value=float(GuiJsonUtil.fetch_translation_settings_key_values("openai settings","openai_presence_penalty")),
                                                                        info=KudasaiGUI.description_dict.get("openai_presence_penalty"),
                                                                        minimum=-2.0,
                                                                        maximum=2.0,
                                                                        show_label=True,
                                                                        interactive=True,
                                                                        elem_id="openai_presence_penalty")
                            
                            self.openai_frequency_penalty_input_field = gr.Slider(label="OpenAI Frequency Penalty",
                                                                        value=float(GuiJsonUtil.fetch_translation_settings_key_values("openai settings","openai_frequency_penalty")),
                                                                        info=KudasaiGUI.description_dict.get("openai_frequency_penalty"),
                                                                        minimum=-2.0,
                                                                        maximum=2.0,
                                                                        show_label=True,
                                                                        interactive=True,
                                                                        elem_id="openai_frequency_penalty")

                    with gr.Row():

                        with gr.Column():

                            gr.Markdown("Gemini API Settings")
                            gr.Markdown(str(KudasaiGUI.description_dict.get("gemini_help_link")))
                            gr.Markdown(str(KudasaiGUI.description_dict.get("gemini_disclaimer")))

                            self.gemini_model_input_field = gr.Dropdown(label="Gemini Model",
                                                                        value=str(GuiJsonUtil.fetch_translation_settings_key_values("gemini settings","gemini_model")),
                                                                        choices=[model for model in ALLOWED_GEMINI_MODELS],
                                                                        info=KudasaiGUI.description_dict.get("gemini_model"),
                                                                        show_label=True,
                                                                        interactive=True,
                                                                        elem_id="gemini_model")

                            self.gemini_prompt_input_field = gr.Textbox(label="Gemini Prompt",
                                                                    value=str(GuiJsonUtil.fetch_translation_settings_key_values("gemini settings","gemini_prompt")),
                                                                    info=KudasaiGUI.description_dict.get("gemini_prompt"),
                                                                    lines=1,
                                                                    max_lines=1,
                                                                    show_label=True,
                                                                    interactive=True,
                                                                    elem_id="gemini_prompt",
                                                                    show_copy_button=True)
                            
                            self.gemini_temperature_input_field = gr.Slider(label="Gemini Temperature",
                                                                        value=float(GuiJsonUtil.fetch_translation_settings_key_values("gemini settings","gemini_temperature")),
                                                                        minimum=0.0,
                                                                        maximum=2.0,
                                                                        info=KudasaiGUI.description_dict.get("gemini_temperature"),
                                                                        show_label=True,
                                                                        interactive=True,
                                                                        elem_id="gemini_temperature")
                            
                            self.gemini_top_p_input_field = gr.Textbox(label="Gemini Top P",
                                                                    value=str(GuiJsonUtil.fetch_translation_settings_key_values("gemini settings","gemini_top_p")),
                                                                    info=KudasaiGUI.description_dict.get("gemini_top_p"),
                                                                    lines=1,
                                                                    max_lines=1,
                                                                    show_label=True,
                                                                    interactive=True,
                                                                    elem_id="gemini_top_p",
                                                                    show_copy_button=True)
                            
                            self.gemini_top_k_input_field = gr.Textbox(label="Gemini Top K",
                                                                    value=str(GuiJsonUtil.fetch_translation_settings_key_values("gemini settings","gemini_top_k")),
                                                                    info=KudasaiGUI.description_dict.get("gemini_top_k"),
                                                                    lines=1,
                                                                    max_lines=1,
                                                                    show_label=True,
                                                                    interactive=True,
                                                                    elem_id="gemini_top_k",
                                                                    show_copy_button=True)

                            self.gemini_candidate_count_input_field = gr.Textbox(label="Gemini Candidate Count",
                                                                                value=str(GuiJsonUtil.fetch_translation_settings_key_values("gemini settings","gemini_candidate_count")),
                                                                                info=KudasaiGUI.description_dict.get("gemini_candidate_count"),
                                                                                lines=1,
                                                                                max_lines=1,
                                                                                show_label=True,
                                                                                interactive=False,
                                                                                elem_id="gemini_candidate_count",
                                                                                show_copy_button=True)

                            self.gemini_stream_input_field = gr.Textbox(label="Gemini Stream",
                                                                    value=str(GuiJsonUtil.fetch_translation_settings_key_values("gemini settings","gemini_stream")),
                                                                    info=KudasaiGUI.description_dict.get("gemini_stream"),
                                                                    lines=1,
                                                                    max_lines=1,
                                                                    show_label=True,
                                                                    interactive=False,
                                                                    elem_id="gemini_stream",
                                                                    show_copy_button=True)
                            
                            self.gemini_stop_sequences_input_field = gr.Textbox(label="Gemini Stop Sequences",
                                                                            value=str(GuiJsonUtil.fetch_translation_settings_key_values("gemini settings","gemini_stop_sequences")),
                                                                            info=KudasaiGUI.description_dict.get("gemini_stop_sequences"),
                                                                            lines=1,
                                                                            max_lines=1,
                                                                            show_label=True,
                                                                            interactive=False,
                                                                            elem_id="gemini_stop_sequences",
                                                                            show_copy_button=True)

                            self.gemini_max_output_tokens_input_field = gr.Textbox(label="Gemini Max Output Tokens",
                                                                                value=str(GuiJsonUtil.fetch_translation_settings_key_values("gemini settings","gemini_max_output_tokens")),
                                                                                info=KudasaiGUI.description_dict.get("gemini_max_output_tokens"),
                                                                                lines=1,
                                                                                max_lines=1,
                                                                                show_label=True,
                                                                                interactive=True,
                                                                                elem_id="gemini_max_output_tokens",
                                                                                show_copy_button=True)
                            
                        with gr.Column():
                                    
                                gr.Markdown("DeepL API Settings")
                                gr.Markdown(str(KudasaiGUI.description_dict.get("deepl_help_link")))
                                gr.Markdown("DeepL API settings are not as extensive as OpenAI and Gemini, a lot of the settings are simply not included for Kudasai as they do not have a decent use case to warrant their inclusion. Settings may be added in the future if a use case is found or is suggested.")

                                self.deepl_context_input_field = gr.Textbox(label="DeepL Context",
                                                                        value=str(GuiJsonUtil.fetch_translation_settings_key_values("deepl settings","deepl_context")),
                                                                        info=KudasaiGUI.description_dict.get("deepl_context"),
                                                                        lines=1,
                                                                        max_lines=1,
                                                                        show_label=True,
                                                                        interactive=True,
                                                                        elem_id="deepl_context",
                                                                        show_copy_button=True)
                                
                                self.deepl_split_sentences_input_field = gr.Dropdown(label="DeepL Split Sentences",
                                                                                value=str(GuiJsonUtil.fetch_translation_settings_key_values("deepl settings","deepl_split_sentences")),
                                                                                choices=['OFF', 'ALL', 'NO_NEWLINES'],
                                                                                info=KudasaiGUI.description_dict.get("deepl_split_sentences"),
                                                                                show_label=True,
                                                                                interactive=True,
                                                                                elem_id="deepl_split_sentences")
                                
                                self.deepl_preserve_formatting_input_field = gr.Checkbox(label="DeepL Preserve Formatting",
                                                                                    value=bool(GuiJsonUtil.fetch_translation_settings_key_values("deepl settings","deepl_preserve_formatting")),
                                                                                    info=KudasaiGUI.description_dict.get("deepl_preserve_formatting"),
                                                                                    show_label=True,
                                                                                    interactive=True,
                                                                                    elem_id="deepl_preserve_formatting")
                                
                                self.deepl_formality_input_field = gr.Dropdown(label="DeepL Formality",
                                                                            value=str(GuiJsonUtil.fetch_translation_settings_key_values("deepl settings","deepl_formality")),
                                                                            choices=['default', 'more', 'less', 'prefer_more', 'prefer_less'],
                                                                            info=KudasaiGUI.description_dict.get("deepl_formality"),
                                                                            show_label=True,
                                                                            interactive=True,
                                                                            elem_id="deepl_formality")
                        

                    with gr.Row():
                        self.translation_settings_reset_to_default_button = gr.Button('Reset to Default', variant='secondary')
                        self.translation_settings_discard_changes_button = gr.Button('Discard Changes', variant='stop')

                    with gr.Row():
                        self.translation_settings_apply_changes_button = gr.Button('Apply Changes', variant='primary')

                ## tab 6 | Logging
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

                Kudasai.connection, update_prompt = Toolkit.check_update(do_pause=False)

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
                            
                            ## DON"T DO THIS, THIS IS BAD PRACTICE, I'M JUST DOING BECAUSE I'M LAZY AND I MADE THE LIBRARY
                            try:
                                _validate_replacement_json(replacements)

                            except InvalidReplacementJsonKeys:
                                raise gr.Error("Invalid JSON file, please ensure that the JSON file contains the correct keys See https://github.com/Bikatr7/Kairyou for more information.")

                            if(input_knowledge_base_file is not None):
                                knowledge_base_paths.append(input_knowledge_base_file)

                            else:
                                knowledge_base_paths = [file for file in input_knowledge_base_directory]

                            for file in knowledge_base_paths:
                                knowledge_base_string += gui_get_text_from_file(file)

                            gr.Info("Indexing may take a while, please be patient.")

                            unique_names, indexing_log = Indexer.index(text_to_index, knowledge_base_string, replacements)

                            ## Indexer does not directly log anything, in case of anything else touching it, we will grab the log from the log file
                            log_text = FileEnsurer.standard_read_file(FileEnsurer.debug_log_path)

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
                        ## link needs to be updated later
                        raise gr.Error("Invalid JSON file, please ensure that the JSON file contains the correct keys See: https://github.com/Bikatr7/Kairyou?tab=readme-ov-file#usage")

                    timestamp = Toolkit.get_timestamp(is_archival=True)

                    FileEnsurer.write_kairyou_results(preprocessed_text, preprocessing_log, error_log, timestamp)

                    log_text = FileEnsurer.standard_read_file(FileEnsurer.debug_log_path)

                    return preprocessed_text, preprocessing_log, log_text, log_text, error_log
            
                else:
                    raise gr.Error("No JSON file selected")
                
##-------------------start-of-translate_with_translator()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            async def translate_with_translator(input_txt_file:gr.File, input_text:str, api_key:str, translation_method:str, translation_settings_file:gr.File) -> typing.Tuple[str, str, str, str]:

                """
                
                Translates the text in the input_txt_file or input_text using either OpenAI, Gemini, or DeepL. If no txt file or text is selected, an error is raised. If no API key is provided or the API key is invalid, an error is raised.
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
                
                if(translation_settings_file is None):
                    raise gr.Error("No Translation Settings File selected")

                if(Kudasai.connection == False):
                    raise gr.Error("No internet connection detected, please connect to the internet and reload the page to use translation features of Kudasai.")

                ## in case of subsequent runs, we need to reset the static variables
                Translator.reset_static_variables()

                ## start of translation, so we can assume that that we don't want to interrupt it
                FileEnsurer.do_interrupt = False

                ## if translate button is clicked, we can assume that the translation is ongoing
                self.is_translation_ongoing = True

                ## first, set the json in the json handler to the json currently set as in gui_json_util
                JsonHandler.current_translation_settings = GuiJsonUtil.current_translation_settings

                ## next, set the llm type
                if(translation_method == "OpenAI"):
                    Translator.TRANSLATION_METHOD = "openai" 

                elif(translation_method == "Gemini"):
                    Translator.TRANSLATION_METHOD = "gemini"

                else:
                    Translator.TRANSLATION_METHOD = "deepl"

                ## api key as well
                await set_translator_api_key(api_key)
                
                if(input_txt_file is not None):
                    text_to_translate = gui_get_text_from_file(input_txt_file)
                
                else:
                    text_to_translate = input_text

                ## need to convert the text to translate to list of strings
                Translator.text_to_translate = [line for line in str(text_to_translate).splitlines()]

                ## commence translation
                await Translator.commence_translation(is_webgui=True)

                Translator.write_translator_results()

                ## je check text and translated text are lists of strings, so we need to convert them to strings
                translated_text = "\n".join(Translator.translated_text)
                je_check_text = "\n".join(Translator.je_check_text)

                ## Log text is cleared from the client, so we need to get it from the log file
                log_text = FileEnsurer.standard_read_file(FileEnsurer.debug_log_path)

                error_text = FileEnsurer.standard_read_file(FileEnsurer.error_log_path)
                
                ## then overwrite the api key file with the new api key
                update_translator_api_key(api_key)

                return translated_text, je_check_text, log_text, error_text
            
##-------------------start-of translator_calculate_costs_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            async def translator_calculate_costs_button_click(input_txt_file:str, input_text:str, translation_method:str, api_key:str, translation_settings_file:gr.File) -> str:


                """
                
                Calculates the cost of the text in the input_txt_file or input_text using the OpenAI, Gemini, or DeepL APIs. If no txt file or text is selected, an error is raised.
                Displays the cost, and the debug log.

                Parameters:
                input_txt_file (gr.File) : The input txt file.
                input_text (str) : The input text.
                translation_method (str) : The language model type.
                api_key (str) : The

                Returns:
                cost_estimation (str) : The cost estimation formatted as a string.
                
                """

                if(input_txt_file is None and input_text == ""):
                    raise gr.Error("No TXT file or text selected")
                
                if(api_key == "" and translation_method not in ["OpenAI","DeepL"]):
                    raise gr.Error("No API key provided. Does not charge for cost estimation, but is required for Gemini Cost Calculation")
                
                if(Kudasai.connection == False and translation_method != "OpenAI"):
                    raise gr.Error("No internet connection detected, please connect to the internet and reload the page to calculate costs for Gemini")
                
                if(translation_settings_file is None):
                    raise gr.Error("No Translation Settings File selected")
                
                ## in case of subsequent runs, we need to reset the static variables
                Translator.reset_static_variables()

                cost_estimation = ""

                Translator.TRANSLATION_METHOD = str(translation_method.lower()) # type: ignore

                await set_translator_api_key(api_key)

                translation_methods = {
                    "openai": GuiJsonUtil.fetch_translation_settings_key_values("openai settings","openai_model"),
                    "gemini": GuiJsonUtil.fetch_translation_settings_key_values("gemini settings","gemini_model"),
                    "deepl": "deep"
                }

                model = translation_methods.get(Translator.TRANSLATION_METHOD) 

                if(input_txt_file is not None):
                    text_to_translate = gui_get_text_from_file(input_txt_file)

                else:
                    text_to_translate = input_text

                translation_instructions_dict = {
                    "openai": GuiJsonUtil.fetch_translation_settings_key_values("openai settings","openai_system_message"),
                    "gemini": GuiJsonUtil.fetch_translation_settings_key_values("gemini settings","gemini_prompt"),
                    "deepl": None
                }

                translation_instructions = translation_instructions_dict.get(Translator.TRANSLATION_METHOD)

                num_tokens, estimated_cost, model = EasyTL.calculate_cost(text=text_to_translate, service=Translator.TRANSLATION_METHOD, model=model, translation_instructions=translation_instructions)

                if(Translator.TRANSLATION_METHOD == "gemini"):
                    cost_estimation = f"As of Kudasai {Toolkit.CURRENT_VERSION}, Gemini Pro 1.0 is free to use under 15 requests per minute, Gemini Pro 1.5 is free to use under 2 requests per minute.\nIt is up to you to set these in the settings json.\n"

                token_type = "characters" if Translator.TRANSLATION_METHOD == "deepl" else "tokens"

                cost_estimation += f"Estimated number of {token_type} : {num_tokens}\nEstimated minimum cost : {estimated_cost} USD\nThis is a rough estimate, please remember to check actual cost on the appropriate platform when needed"
                
                gr.Info(cost_estimation)

                update_translator_api_key(api_key)

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
            
##-------------------start-of-clear_translator_tab()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            def clear_translator_tab() -> typing.Tuple[None, str, gr.File, str, str, str]:

                """
                
                Clears all fields on the Translator tab. As well as the input fields.

                Returns:
                input_txt_file_translator (gr.File) : An empty file.
                input_text_translator (str) : An empty string.
                translator_translated_text_output_field (str) : An empty string.
                je_check_text_field_translator (str) : An empty string.
                translator_debug_log_output_field (str) : An empty string.

                """

                ## if clear button is clicked, we can assume that the translation is over, or that the user wants to cancel the translation
                self.is_translation_ongoing = False

                ## Same as above, we can assume that the user wants to cancel the translation if it's ongoing
                FileEnsurer.do_interrupt = True

                input_file_translator = None

                input_text_translator = ""

                ## Also gonna want to reset the json input field to the default json file
                input_translation_rules_file = gr.File(value = FileEnsurer.config_translation_settings_path, label='Translation Settings File', file_count='single', file_types=['.json'], type='filepath')

                translator_translated_text_output_field = ""
                je_check_text_field_translator = ""
                translator_debug_log_output_field = ""

                return input_file_translator, input_text_translator, input_translation_rules_file, translator_translated_text_output_field, je_check_text_field_translator, translator_debug_log_output_field
            
##-------------------start-of-clear_log_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        
            def clear_log_button_click() -> typing.Tuple[str, str]:

                """

                Clears the logs on the log tab.

                Returns:
                logging_tab_debug_log_output_field (str) : An empty string.
                logging_tab_error_log_output_field (str) : An empty string.

                """

                ## also needs to clear the log and error log files
                FileEnsurer.standard_overwrite_file(FileEnsurer.debug_log_path, "")
                FileEnsurer.standard_overwrite_file(FileEnsurer.error_log_path, "")

                logging_tab_debug_log_output_field = ""
                logging_tab_error_log_output_field = ""

                return logging_tab_debug_log_output_field, logging_tab_error_log_output_field

##-------------------start-of-apply_new_translator_settings()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            def apply_new_translator_settings(
                                        input_translation_rules_file:gr.File,
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
                                        gemini_max_output_tokens:str,
                                        deepl_context:str,
                                        deepl_split_sentences:str,
                                        deepl_preserve_formatting:bool,
                                        deepl_formality:str) -> None:

                
                """

                Applies the new translation settings to the Translation Settings File.

                """

                if(input_translation_rules_file is None):
                    raise gr.Error("No Translation Settings File Selected. Cannot apply settings.")

                ## build the new translation settings list so we can create a key-value pair list
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
                    gemini_max_output_tokens,
                    deepl_context,
                    deepl_split_sentences,
                    deepl_preserve_formatting,
                    deepl_formality
                
                ]

                ## create the new key-value pair list
                new_key_value_tuple_pairs = create_new_key_value_tuple_pairs(settings_list)

                try:
                    ## and then have the GuiJsonUtil apply the new translator settings
                    GuiJsonUtil.update_translation_settings_with_new_values(input_translation_rules_file, new_key_value_tuple_pairs)

                except:
                    raise gr.Error("Invalid Translator Settings")

                gr.Info("Translator Settings Applied")

##-------------------start-of-reset_to_default_translation_settings()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            def reset_to_default_translation_settings(input_translation_rules_file:gr.File):

                """

                Resets the translation settings to the default values.

                """

                if(input_translation_rules_file is None):
                    raise gr.Error("No Translation Settings File Selected. Cannot reset settings.")

                GuiJsonUtil.current_translation_settings = FileEnsurer.DEFAULT_TRANSLATION_SETTING

                settings = [
                    ("base translation settings", "prompt_assembly_mode", int),
                    ("base translation settings", "number_of_lines_per_batch", str),
                    ("base translation settings", "sentence_fragmenter_mode", int),
                    ("base translation settings", "je_check_mode", int),
                    ("base translation settings", "number_of_malformed_batch_retries", str),
                    ("base translation settings", "batch_retry_timeout", str),
                    ("base translation settings", "number_of_concurrent_batches", str),
                    ("openai settings", "openai_model", str),
                    ("openai settings", "openai_system_message", str),
                    ("openai settings", "openai_temperature", float),
                    ("openai settings", "openai_top_p", float),
                    ("openai settings", "openai_n", str),
                    ("openai settings", "openai_stream", str),
                    ("openai settings", "openai_stop", str),
                    ("openai settings", "openai_logit_bias", str),
                    ("openai settings", "openai_max_tokens", str),
                    ("openai settings", "openai_presence_penalty", float),
                    ("openai settings", "openai_frequency_penalty", float),
                    ("gemini settings", "gemini_model", str),
                    ("gemini settings", "gemini_prompt", str),
                    ("gemini settings", "gemini_temperature", float),
                    ("gemini settings", "gemini_top_p", str),
                    ("gemini settings", "gemini_top_k", str),
                    ("gemini settings", "gemini_candidate_count", str),
                    ("gemini settings", "gemini_stream", str),
                    ("gemini settings", "gemini_stop_sequences", str),
                    ("gemini settings", "gemini_max_output_tokens", str),
                    ("deepl settings", "deepl_context", str),
                    ("deepl settings", "deepl_split_sentences", str),
                    ("deepl settings", "deepl_preserve_formatting", bool),
                    ("deepl settings", "deepl_formality", str),
                ]

                return_batch = [cast(GuiJsonUtil.fetch_translation_settings_key_values(setting, key)) for setting, key, cast in settings]

                gr.Info("Translator Settings Reset to Default. Make sure to press the Apply button to apply the changes.")

                return return_batch

##-------------------start-of-refresh_translation_settings_fields()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            def refresh_translation_settings_fields(input_translation_rules_file:str):

                """

                Refreshes the translation settings fields with the values from the Translation Settings File.                

                """


                if(input_translation_rules_file is None):
                    raise gr.Error("No Translation Settings File Selected. Cannot refresh settings.")
                
                try:
                    GuiJsonUtil.current_translation_settings = gui_get_json_from_file(input_translation_rules_file)
                
                    settings = [
                        ("base translation settings", "prompt_assembly_mode", int),
                        ("base translation settings", "number_of_lines_per_batch", str),
                        ("base translation settings", "sentence_fragmenter_mode", int),
                        ("base translation settings", "je_check_mode", int),
                        ("base translation settings", "number_of_malformed_batch_retries", str),
                        ("base translation settings", "batch_retry_timeout", str),
                        ("base translation settings", "number_of_concurrent_batches", str),
                        ("openai settings", "openai_model", str),
                        ("openai settings", "openai_system_message", str),
                        ("openai settings", "openai_temperature", float),
                        ("openai settings", "openai_top_p", float),
                        ("openai settings", "openai_n", str),
                        ("openai settings", "openai_stream", str),
                        ("openai settings", "openai_stop", str),
                        ("openai settings", "openai_logit_bias", str),
                        ("openai settings", "openai_max_tokens", str),
                        ("openai settings", "openai_presence_penalty", float),
                        ("openai settings", "openai_frequency_penalty", float),
                        ("gemini settings", "gemini_model", str),
                        ("gemini settings", "gemini_prompt", str),
                        ("gemini settings", "gemini_temperature", float),
                        ("gemini settings", "gemini_top_p", str),
                        ("gemini settings", "gemini_top_k", str),
                        ("gemini settings", "gemini_candidate_count", str),
                        ("gemini settings", "gemini_stream", str),
                        ("gemini settings", "gemini_stop_sequences", str),
                        ("gemini settings", "gemini_max_output_tokens", str),
                        ("deepl settings", "deepl_context", str),
                        ("deepl settings", "deepl_split_sentences", str),
                        ("deepl settings", "deepl_preserve_formatting", bool),
                        ("deepl settings", "deepl_formality", str),
                    ]
                
                    return_batch = [cast(GuiJsonUtil.fetch_translation_settings_key_values(setting, key)) for setting, key, cast in settings]
                
                except:
                    GuiJsonUtil.current_translation_settings = JsonHandler.current_translation_settings
                    raise gr.Error("Invalid Custom Translation Settings File")
                
                return return_batch

##-------------------start-of-clear_translation_settings_input_fields()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        
            def clear_translation_settings_input_fields():                                                                  

                """

                Resets the translation settings input fields to None.

                """


                settings = {
                    "input_translation_rules_file": None,
                    "prompt_assembly_mode_value": None,
                    "number_of_lines_per_batch_value": None,
                    "sentence_fragmenter_mode_value": None,
                    "je_check_mode_value": None,
                    "num_malformed_batch_retries_value": None,
                    "batch_retry_timeout_value": None,
                    "num_concurrent_batches_value": None,
                    "openai_model_value": None,
                    "openai_system_message_value": None,
                    "openai_temperature_value": None,
                    "openai_top_p_value": None,
                    "openai_n_value": None,
                    "openai_stream_value": None,
                    "openai_stop_value": None,
                    "openai_logit_bias_value": None,
                    "openai_max_tokens_value": None,
                    "openai_presence_penalty_value": None,
                    "openai_frequency_penalty_value": None,
                    "gemini_model_value": None,
                    "gemini_prompt_value": None,
                    "gemini_temperature_value": None,
                    "gemini_top_p_value": None,
                    "gemini_top_k_value": None,
                    "gemini_candidate_count_value": None,
                    "gemini_stream_value": None,
                    "gemini_stop_sequences_value": None,
                    "gemini_max_output_tokens_value": None,
                    "deepl_context": None,
                    "deepl_split_sentences": None,
                    "deepl_preserve_formatting": None,
                    "deepl_formality": None,
                }
                
                return settings
            
##-------------------start-of-fetch_log_content()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            def fetch_debug_log_content() -> typing.Tuple[str, str]:
            
                """
                
                Fetches the log content from the log file.

                Returns:
                log_text (str) : The log text.
                logging_tab_error_log_output_field (str) : The error log.

                """

                log_text = FileEnsurer.standard_read_file(FileEnsurer.debug_log_path)
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
                    gr.Warning("No indexed text to send to Preprocessor (Kairyou)")
                    return ""
                
                else:
                    gr.Info("Indexed text copied to Preprocessor (Kairyou)")
                    return input_text
                
##-------------------start-of-send_to_translator_button()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
                
            def send_to_translator_button(input_text:str) -> str:

                """

                Sends the preprocessed text to Translator.

                Parameters:
                input_text (str) : The input text.

                Returns:
                input_text (str) : The input text.

                """

                if(input_text == ""):
                    gr.Warning("No preprocessed text to send to Translator")
                    return ""
                
                else:
                    gr.Info("Preprocessed text copied to Translator")
                    return input_text
                
##-------------------start-of-switch_translator_api_key_type()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
                
            def switch_translator_api_key_type(translation_method:str) -> str:

                """
                
                Switches the api key type between OpenAI, Gemini, and DeepL.

                Parameters:
                translation_method (str) : The translation method

                Returns:
                api_key (str) : The api key.

                """

                return get_saved_api_key(translation_method.lower()) ## type: ignore
                
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
            

            
##-------------------start-of-translate_with_translator()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            ## for the actual translation, and the je check text
            translator_translate_process = self.translator_translate_button.click(translate_with_translator,
                                                inputs=[
                                                    self.input_txt_file_translator, ## input txt file to translate
                                                    self.input_text_translator, ## input text to translate
                                                    self.translator_api_key_input, ## api key input
                                                    self.llm_option_dropdown, ## Translation Method dropdown
                                                    self.input_translation_rules_file], ## Translation Settings File
                                                
                                                outputs=[
                                                    self.translator_translated_text_output_field, ## translated text
                                                    self.translator_je_check_text_output_field, ## je check text field on translator tab
                                                    self.logging_tab_debug_log_output_field , ## debug log on log tab
                                                    self.logging_tab_error_log_output_field]) ## error log on log tab
            ## for the debug log
            self.translator_translate_button.click(fn=fetch_log_content,
                                                inputs=[],

                                                outputs=[self.translator_debug_log_output_field], ## debug log on translator tab

                                                every=.1) ## update every 100ms
            

##-------------------start-of translator_calculate_costs_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            self.translator_calculate_cost_button.click(translator_calculate_costs_button_click,
                                                        inputs=[
                                                            self.input_txt_file_translator, ## input txt file to calculate costs
                                                            self.input_text_translator,
                                                            self.llm_option_dropdown,
                                                            self.translator_api_key_input,
                                                            self.input_translation_rules_file], ## Translation Settings File
                
                                                        outputs=[self.translator_translated_text_output_field]) ## functions as an output field for the cost output field
            
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

##-------------------start-of-clear_button_translator_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            self.translator_clear_button.click(clear_translator_tab,
                                            inputs=[],

                                            outputs=[
                                                self.input_txt_file_translator, ## input txt file
                                                self.input_text_translator, ## input text
                                                self.input_translation_rules_file, ## Translation Settings File
                                                self.translator_translated_text_output_field, ## translation output field
                                                self.translator_je_check_text_output_field, ## je check text field on translator tab
                                                self.translator_debug_log_output_field], ## debug log on translator tab
            
                                            cancels=translator_translate_process)
            
##-------------------start-of-clear_log_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.logging_clear_logs_button.click(clear_log_button_click,
                                        inputs=[],

                                        outputs=[
                                            self.logging_tab_debug_log_output_field,
                                            self.logging_tab_error_log_output_field])
            
##-------------------start-of-apply_new_translator_settings()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            self.translation_settings_apply_changes_button.click(apply_new_translator_settings,
                                            inputs=[
                                                self.input_translation_rules_file, ## Translation Settings File
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
                                                self.gemini_max_output_tokens_input_field, ## gemini max output tokens input field
                                                self.deepl_context_input_field, ## deepl context input field
                                                self.deepl_split_sentences_input_field, ## deepl split sentences input field
                                                self.deepl_preserve_formatting_input_field, ## deepl preserve formatting input field
                                                self.deepl_formality_input_field], ## deepl formality input field
                                            
                                            outputs=[])
            
##-------------------start-of-reset_to_default_translation_settings_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            self.translation_settings_reset_to_default_button.click(reset_to_default_translation_settings,
                                                inputs=[self.input_translation_rules_file],
                                                
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
                                                        self.gemini_max_output_tokens_input_field, ## gemini max output tokens input field
                                                        self.deepl_context_input_field, ## deepl context input field
                                                        self.deepl_split_sentences_input_field, ## deepl split sentences input field
                                                        self.deepl_preserve_formatting_input_field, ## deepl preserve formatting input field
                                                        self.deepl_formality_input_field])

##-------------------start-of-discard_changes_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            self.translation_settings_discard_changes_button.click(refresh_translation_settings_fields,
                                              inputs=[self.input_translation_rules_file],
                                              
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
                                                    self.gemini_max_output_tokens_input_field, ## gemini max output tokens input field
                                                    self.deepl_context_input_field, ## deepl context input field
                                                    self.deepl_split_sentences_input_field, ## deepl split sentences input field
                                                    self.deepl_preserve_formatting_input_field, ## deepl preserve formatting input field
                                                    self.deepl_formality_input_field]) ## deepl formality input field

##-------------------start-of-input_translator_rules_file_upload()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            self.input_translation_rules_file.upload(refresh_translation_settings_fields,
                                                inputs=[self.input_translation_rules_file],
                                                
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
                                                    self.gemini_max_output_tokens_input_field, ## gemini max output tokens input field
                                                    self.deepl_context_input_field, ## deepl context input field
                                                    self.deepl_split_sentences_input_field, ## deepl split sentences input field
                                                    self.deepl_preserve_formatting_input_field, ## deepl preserve formatting input field
                                                    self.deepl_formality_input_field]) ## deepl formality input field
            
            self.input_translation_rules_file.clear(clear_translation_settings_input_fields,
                                                inputs=[],
                                                
                                                outputs=[
                                                    self.input_translation_rules_file, ## Translation Settings File
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
                                                    self.gemini_max_output_tokens_input_field, ## gemini max output tokens input field
                                                    self.deepl_context_input_field, ## deepl context input field
                                                    self.deepl_split_sentences_input_field, ## deepl split sentences input field
                                                    self.deepl_preserve_formatting_input_field, ## deepl preserve formatting input field
                                                    self.deepl_formality_input_field]) ## deepl formality input field

##-------------------start-of-logging_tab.select()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.logging_tab.select(fetch_debug_log_content,
                                    inputs=[],
                                    
                                    outputs=[self.logging_tab_debug_log_output_field, self.logging_tab_error_log_output_field])
            
##-------------------start-of-translator_api_key_input.change()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.llm_option_dropdown.change(switch_translator_api_key_type,
                                             inputs=[self.llm_option_dropdown],
                                            
                                            outputs=[self.translator_api_key_input])
            
##-------------------start-of-save_to_file_indexed_text_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            self.save_to_file_indexed_text.click(lambda text: text, ## save text as is
                inputs=[self.indexing_output_field], ## input text to save

                outputs=[], ## no outputs

                ## javascript code that allows us to save textbox contents to a file
                js=(self.js_save_to_file).replace("downloaded_text.txt", "indexed_text.txt")
            )

##-------------------start-of-save_to_file_indexing_results_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            self.save_to_file_indexing_results.click(lambda text: text, ## save text as is
                inputs=[self.indexing_results_output_field], ## input text to save

                outputs=[], ## no outputs

                ## javascript code that allows us to save textbox contents to a file
                js=(self.js_save_to_file).replace("downloaded_text.txt", "indexing_results.txt")
            )

##-------------------start-of-save_to_file_indexing_debug_log_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            self.save_to_file_debug_log_indexing_tab.click(lambda text: text, ## save text as is
                inputs=[self.debug_log_output_field_indexing_tab], ## input text to save

                outputs=[], ## no outputs

                ## javascript code that allows us to save textbox contents to a file
                js=(self.js_save_to_file).replace("downloaded_text.txt", "indexing_debug_log.txt")
            )
            
##-------------------start-of-save_to_file_preprocessing_results_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.save_to_file_preprocessed_text.click(lambda text: text, ## save text as is
                inputs=[self.preprocessing_output_field],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                js=(self.js_save_to_file).replace("downloaded_text.txt", "preprocessed_text.txt")
            )
            
##-------------------start-of-save_to_file_preprocessing_results_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.save_to_file_preprocessing_results.click(lambda text: text, ## save text as is
                inputs=[self.preprocessing_results_output_field],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                js=(self.js_save_to_file).replace("downloaded_text.txt", "preprocessing_results.txt")
            )

##-------------------start-of-save_to_file_debug_log_processing_tab_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.save_to_file_debug_log_preprocessing_tab.click(lambda text: text, ## save text as is
                inputs=[self.debug_log_output_field_preprocess_tab],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                js=(self.js_save_to_file).replace("downloaded_text.txt", "preprocessing_debug_log_.txt")
            )

##-------------------start-of-save_to_file_translator_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            self.save_to_file_translator_translated_text.click(lambda text: text, ## save text as is
                inputs=[self.translator_translated_text_output_field],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                js=(self.js_save_to_file).replace("downloaded_text.txt", "translated_text_translator.txt")
            )

##-------------------start-of-save_to_file_je_check_text_translator_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            self.save_to_file_translator_je_check_text.click(lambda text: text, ## save text as is
                inputs=[self.translator_je_check_text_output_field],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                js=(self.js_save_to_file).replace("downloaded_text.txt", "je_check_text_translator.txt")
            )

##-------------------start-of-save_to_file_debug_log_translator_tab_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            self.save_to_file_debug_log_translator_tab.click(lambda text: text, ## save text as is
                inputs=[self.translator_debug_log_output_field],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                js=(self.js_save_to_file).replace("downloaded_text.txt", "debug_log_translator.txt")
            )

##-------------------start-of-save_to_file_debug_log_logging_tab_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.save_to_file_debug_log_logging_tab.click(lambda text: text, ## save text as is
                inputs=[self.logging_tab_debug_log_output_field],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                js=(self.js_save_to_file).replace("downloaded_text.txt", "debug_log_all.txt")
            )

##-------------------start-of-save_to_file_error_log_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.save_to_file_error_log_logging_tab.click(lambda text: text, ## save text as is
                inputs=[self.logging_tab_error_log_output_field],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                js=(self.js_save_to_file).replace("downloaded_text.txt", "error_log.txt")
            )

##-------------------start-of-send_to_x_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.send_to_kairyou_button.click(fn=send_to_kairyou_button, 
                                        inputs=[self.indexing_output_field],
                                        outputs=[self.input_text_kairyou])
                                                    
            self.send_to_translator_button.click(fn=send_to_translator_button,
                                        inputs=[self.preprocessing_output_field],
                                        outputs=[self.input_text_translator])

##-------------------start-of-launch()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------                

    def launch(self):

        """

        Launches the GUI.

        """

        Kudasai.boot()

        GuiJsonUtil.current_translation_settings = JsonHandler.current_translation_settings

        self.build_gui()
        self.gui.queue().launch(inbrowser=True, show_error=True, show_api=False, favicon_path=FileEnsurer.favicon_path)

##-------------------start-of-main()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

if(__name__ == '__main__'):

    try:

        kudasai_gui = KudasaiGUI()
        kudasai_gui.launch()

    except Exception as e:

        FileEnsurer.handle_critical_exception(e)