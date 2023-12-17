## built-in libraries
import typing
import base64

## third-party libraries
import gradio as gr

## custom modules
from modules.common.toolkit import Toolkit
from modules.common.logger import Logger
from modules.common.file_ensurer import FileEnsurer

from modules.gui.gui_file_util import gui_get_text_from_file, gui_get_json_from_file

from models.kairyou import Kairyou
from models.kaiseki import Kaiseki

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

    is_translation_ongoing = False

##-------------------start-of-build_gui()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def build_gui(self):

        """

        Builds the GUI.

        """

        with gr.Blocks() as self.gui:

##-------------------start-of-Utility-Functions---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

##-------------------start-of-fetch_log_content()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            def fetch_log_content():

                """
                
                Fetches the log content from the log file and displays it in the debug log field on the current translation tab.

                Returns:
                log_text (str) : The log text.

                """

                if(self.is_translation_ongoing == False):
                    return "No translation ongoing"

                if(Logger.current_batch == ""):
                    return "No log content found."
                
                return Logger.current_batch
            
##-------------------start-of-get_saved_kaiseki_api_key()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            def get_saved_kaiseki_api_key():

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
                
            def get_saved_kijiku_api_key():

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
            
##-------------------start-of-GUI-Structure---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

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
                            self.input_txt_file_kaiseki = gr.File(label='TXT file with Japanese Text', file_count='single', file_types=['.txt'], type='file', interactive=True)
                            self.input_text_kaiseki = gr.Textbox(label='Japanese Text', placeholder='Use this or the text file input, if you provide both, Kudasai will use the file input.', lines=10, show_label=True, interactive=True, type='text')


                            with gr.Row():
                                self.api_key_input = gr.Textbox(label='API Key', value=get_saved_kaiseki_api_key, lines=1, show_label=True, interactive=True)

                            with gr.Row():
                                self.translate_button_kaiseki = gr.Button('Translate')
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
                            self.debug_log_output_field_kaiseki_tab = gr.Textbox(label='Debug Log', lines=29,max_lines=29, interactive=False, show_copy_button=True, elem_id='debug_log_output_field_kaiseki_tab')

                            with gr.Row():
                                self.save_to_file_debug_log_kaiseki_tab = gr.Button('Save As')


                ## tab 4 | Translation Model 2 | Kijiku
                with gr.Tab("Translation With OpenAI | Kijiku") as self.kijiku_tab:
                    with gr.Row():

                        ## input file or text input, gui allows for both but will prioritize file input
                        with gr.Column():
                            self.input_txt_file_kijiku = gr.File(label='TXT file with Japanese Text', file_count='single', file_types=['.txt'], type='file', interactive=True)
                            self.input_text_kijiku = gr.Textbox(label='Japanese Text', placeholder='Use this or the text file input, if you provide both, Kudasai will use the file input.', lines=10, show_label=True, interactive=True, type='text')
                            self.input_kijiku_rules_file = gr.File(value = FileEnsurer.config_kijiku_rules_path, label='Kijiku Rules File', file_count='single', file_types=['.json'], type='file')

                            with gr.Row():
                                self.api_key_input = gr.Textbox(label='API Key', value=get_saved_kijiku_api_key, lines=1, max_lines=2, show_label=True, interactive=True)

                            with gr.Row():
                                self.translate_button_kijiku = gr.Button('Translate')
                                self.clear_button_kijiku = gr.Button('Clear', variant='stop')

                        ## output fields
                        with gr.Column():
                            self.output_field_kijiku = gr.Textbox(label='Translated Text', lines=29,max_lines=29, interactive=False, show_copy_button=True)

                            with gr.Row():
                                self.save_to_file_kijiku = gr.Button('Save As')

                        with gr.Column():
                            self.kijiku_je_check_text_field = gr.Textbox(label='JE Check Text', lines=29,max_lines=29, interactive=False, show_copy_button=True)

                            with gr.Row():
                                self.save_to_file_je_check_text_kijiku = gr.Button('Save As')

                        with gr.Column():
                            self.debug_log_output_field_kijiku_tab = gr.Textbox(label='Debug Log', lines=29,max_lines=29, interactive=False, show_copy_button=True, elem_id='debug_log_output_field_kijiku_tab')

                            with gr.Row():
                                self.save_to_file_debug_log_kijiku_tab = gr.Button('Save As')


                ## tab 5 | Kijiku Settings
                with gr.Tab("Kijiku Settings") as self.kijiku_settings_tab:
                    with gr.Row():

                        with gr.Column():
                            self.model_input_field = gr.Textbox(label='Model', info="ID of the model to use. As of right now, Kijiku only works with 'chat' models.", lines=1, max_lines=1, show_label=True, interactive=True)
                            self.temperature_input_field = gr.Textbox(label='Temperature', info="What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. Lower values are typically better for translation.", lines=1, max_lines=1, show_label=True, interactive=True)

                    with gr.Row():
                        self.apply_changes_button = gr.Button('Apply Changes')
                        self.discard_changes_button = gr.Button('Discard Changes', variant='stop')


                ## tab 6 | Logging
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

                Returns:
                text_to_preprocess (str) : The preprocessed text.
                preprocessing_log (str) : The preprocessing log.
                log_text (str) : The log text for the Kairyou tab.
                log_text (str) : The log text for the log tab.

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
                        ## Kairyou doesn't have any advanced logging, so we can just return the log text for both the log tab and the preprocess tab, no need to do what we did for the Kaiseki tab or Kijiku tab
                        return Kairyou.text_to_preprocess, preprocessing_log, log_text, log_text
  
                    else:
                        raise gr.Error("No JSON file selected")
                
                else:
                    raise gr.Error("No TXT file selected")
                
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

                ## in case of subsequent runs, we need to clear the batch
                Logger.clear_batch()

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
                    Kaiseki.setup_api_key(str(api_key_input))

                except:
                    raise gr.Error("Invalid API key")
                

                Kaiseki.text_to_translate  = [line for line in str(text_to_translate).splitlines()]

                Kaiseki.commence_translation()
                Kaiseki.write_kaiseki_results()

                ## Log text is cleared from the client, so we need to get it from the log file
                log_text = FileEnsurer.standard_read_file(Logger.log_file_path)

                ## je check text and translated text are lists of strings, so we need to convert them to strings
                translated_text = "\n".join(Kaiseki.translated_text)
                je_check_text = "\n".join(Kaiseki.je_check_text)

                return translated_text, je_check_text, log_text
            
##-------------------start-of-kijiku_translate_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            def kijiku_translate_button_click(input_txt_file:gr.File, input_text:gr.Textbox, api_key_input:gr.Textbox, input_kijiku_rules_file:gr.File) -> typing.Tuple[str, str, str]:

                """
                
                Translates the text in the input_txt_file or input_text using the OpenAI API. If no txt file or text is selected, an error is raised. If no API key is provided or the API key is invalid, an error is raised.
                Displays the translated text, and the debug log.

                Parameters:
                input_txt_file (gr.File) : The input txt file.
                input_text (gr.Textbox) : The input text.
                api_key_input (gr.Textbox) : The API key input.
                input_kijiku_rules_file (gr.File) : The kijiku rules file.

                Returns:
                translated_text (str) : The translated text.
                je_check_text (str) : The je check text.
                log_text (str) : The log text for the Log tab.
                
                """

                return "", "", ""

##-------------------start-of-preprocessing_clear_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------                

            def preprocessing_clear_button_click() -> typing.Tuple[None, None, str, str, str]:

                """

                Clears all fields on the preprocessing tab. As well as the input fields.

                Returns:
                input_txt_file (gr.File) : An empty file.
                input_json_file (gr.File) : An empty file.
                preprocess_output_field (str) : An empty string.
                preprocessing_results_output_field (str) : An empty string.
                debug_log_output_field_preprocess_tab (str) : An empty string.

                """

                input_txt_file = None
                input_json_file = None

                preprocess_output_field = ""
                preprocessing_results_output_field = ""
                debug_log_output_field_preprocess_tab = ""

                return input_txt_file, input_json_file, preprocess_output_field, preprocessing_results_output_field, debug_log_output_field_preprocess_tab
            
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
                output_field_kijiku (str) : An empty string.
                je_check_text_field_kijiku (str) : An empty string.
                debug_log_output_field_kijiku_tab (str) : An empty string.

                """

                ## if clear button is clicked, we can assume that the translation is over, or that the user wants to cancel the translation
                self.is_translation_ongoing = False

                input_file_kijiku = None

                input_text_kijiku = ""

                input_kijiku_rules_file = gr.File(value = FileEnsurer.config_kijiku_rules_path, label='Kijiku Rules File', file_count='single', file_types=['.json'], type='file')

                output_field_kijiku = ""
                je_check_text_field_kijiku = ""
                debug_log_output_field_kijiku_tab = ""

                return input_file_kijiku, input_text_kijiku, input_kijiku_rules_file, output_field_kijiku, je_check_text_field_kijiku, debug_log_output_field_kijiku_tab
            
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
            
##-------------------start-of-Listener-Declaration---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

##-------------------start-of-preprocessing_run_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.preprocessing_run_button.click(fn=preprocessing_run_button_click, 
                                                inputs=[
                                                    self.input_txt_file_preprocessing, ## input txt file to preprocess
                                                    self.input_json_file], ## replacements json file
                                                                                           
                                                outputs=[
                                                    self.preprocess_output_field,  ## preprocessed text
                                                    self.preprocessing_results_output_field,  ## kairyou results
                                                    self.debug_log_output_field_preprocess_tab, ## debug log on preprocess tab
                                                    self.debug_log_output_field_log_tab]) ## debug log on log tab

##-------------------start-of-kaiseki_translate_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            ## for the actual translation, and the je check text
            self.translate_button_kaiseki.click(kaiseki_translate_button_click,
                                                inputs=[
                                                    self.input_txt_file_kaiseki, ## input txt file to translate
                                                    self.input_text_kaiseki, ## input text to translate
                                                    self.api_key_input], ## api key input
                                                
                                                outputs=[
                                                    self.output_field_kaiseki, ## translated text
                                                    self.kaiseki_je_check_text_field]) ## je check text field on kaiseki tab
            
            ## for the kaiseki debug log
            self.translate_button_kaiseki.click(fn=fetch_log_content,
                                                inputs=[],

                                                outputs=[self.debug_log_output_field_kaiseki_tab], ## debug log on kaiseki tab

                                                every=.1) ## update every 100ms
            

##-------------------start-of-kijiku_translate_button_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            ## for the actual translation, and the je check text
            self.translate_button_kijiku.click(kijiku_translate_button_click,
                                                inputs=[
                                                    self.input_txt_file_kijiku, ## input txt file to translate
                                                    self.input_text_kijiku, ## input text to translate
                                                    self.api_key_input, ## api key input
                                                    self.input_kijiku_rules_file], ## kijiku rules file
                                                
                                                outputs=[
                                                    self.output_field_kijiku, ## translated text
                                                    self.kijiku_je_check_text_field]) ## je check text field on kijiku tab
            
            ## for the kijiku debug log
            self.translate_button_kijiku.click(fn=fetch_log_content,
                                                inputs=[],

                                                outputs=[self.debug_log_output_field_kijiku_tab], ## debug log on kijiku tab

                                                every=.1) ## update every 100ms
            
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
                                                self.kaiseki_je_check_text_field, ## je check text field on kaiseki tab
                                                self.debug_log_output_field_kaiseki_tab]) ## debug log on kaiseki tab
            
##-------------------start-of-clear_button_kijiku_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            self.clear_button_kijiku.click(kijiku_clear_button_click,
                                            inputs=[],

                                            outputs=[
                                                self.input_txt_file_kijiku, ## input txt file
                                                self.input_text_kijiku, ## input text
                                                self.input_kijiku_rules_file, ## kijiku rules file
                                                self.output_field_kijiku, ## translation output field
                                                self.kijiku_je_check_text_field, ## je check text field on kijiku tab
                                                self.debug_log_output_field_kijiku_tab]) ## debug log on kijiku tab
            
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

##-------------------start-of-save_to_file_je_check_text_kaiseki_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.save_to_file_je_check_text_kaiseki.click(lambda text: text, ## save text as is
                inputs=[self.kaiseki_je_check_text_field],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                _js=(self.save_as_js).replace("downloaded_text.txt", "je_check_text.txt")
            )

##-------------------start-of-save_to_file_debug_log_kaiseki_tab_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            self.save_to_file_debug_log_kaiseki_tab.click(lambda text: text, ## save text as is
                inputs=[self.debug_log_output_field_kaiseki_tab],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                _js=(self.save_as_js).replace("downloaded_text.txt", "debug_log.txt")
            )

##-------------------start-of-save_to_file_kijiku_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            self.save_to_file_kijiku.click(lambda text: text, ## save text as is
                inputs=[self.output_field_kijiku],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                _js=(self.save_as_js).replace("downloaded_text.txt", "translated_text.txt")
            )

##-------------------start-of-save_to_file_je_check_text_kijiku_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            self.save_to_file_je_check_text_kijiku.click(lambda text: text, ## save text as is
                inputs=[self.kijiku_je_check_text_field],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                _js=(self.save_as_js).replace("downloaded_text.txt", "je_check_text.txt")
            )

##-------------------start-of-save_to_file_debug_log_kijiku_tab_click()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
            self.save_to_file_debug_log_kijiku_tab.click(lambda text: text, ## save text as is
                inputs=[self.debug_log_output_field_kijiku_tab],

                outputs=[],

                ## javascript code that allows us to save textbox contents to a file
                _js=(self.save_as_js).replace("downloaded_text.txt", "debug_log.txt")
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

        Kudasai.boot()

        self.build_gui()
        self.gui.queue().launch(inbrowser=True, show_error=True)

##-------------------start-of-main()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

if(__name__ == '__main__'):

    try:

        kudasai_gui = KudasaiGUI()
        kudasai_gui.launch()

        Logger.push_batch()

    except Exception as e:

        FileEnsurer.handle_critical_exception(e)