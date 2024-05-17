---------------------------------------------------------------------------------------------------------------------------------------------------
**Table of Contents**

- [**Notes**](#notes)
- [**Dependencies**](#dependencies)
- [**Quick Start**](#quick-start)
- [**Command Line Interface (CLI)**](#command-line-interface-cli)
  - [Usage](#usage)
    - [Preprocess Mode](#preprocess-mode)
    - [Translate Mode](#translate-mode)
  - [Additional Notes](#additional-notes)
- [**Preprocessing**](#preprocessing)
- [**Translator**](#translator)
- [**Translator Settings**](#translator-settings)
- [**Web GUI**](#web-gui)
- [**Hugging Face**](#hugging-face)
- [**License**](#license)
- [**Contact**](#contact)
- [**Acknowledgements**](#acknowledgements)

---------------------------------------------------------------------------------------------------------------------------------------------------
## **Notes**<a name="notes"></a>

Windows 10 and Linux Mint are the only tested operating systems, feel free to test on other operating systems and report back to me. I will do my best to fix any issues that arise.

To see the README for the Hugging Face hosted version of Kudasai, please see [here](https://huggingface.co/spaces/Bikatr7/Kudasai/blob/main/README.md). Further WebGUI documentation can be found there as well.

Python version: 3.10+

Streamlining Japanese-English Translation with Advanced Preprocessing and Integrated Translation Technologies.

Preprocessor and Translation logic is sourced from external packages, which I also designed, see [Kairyou](https://github.com/Bikatr7/Kairyou) and [EasyTL](https://github.com/Bikatr7/easytl) for more information.

Kudasai has a public trello board, you can find it [here](https://trello.com/b/Wsuwr24S/kudasai) to see what I'm working on and what's coming up.

Kudasai is proud to have been a Backdrop Build v3 Finalist:
https://backdropbuild.com/builds/v3/kudasai

---------------------------------------------------------------------------------------------------------------------------------------------------
## **Dependencies**<a name="dependencies"></a>

backoff==2.2.1

gradio==4.20.0

kairyou==1.5.0

easytl==0.3.3

or see requirements.txt

Also requires spacy's ja_core_news_lg model, which can be installed via the following command:

```bash
python -m spacy download ja_core_news_lg
```

or on Linux

```bash
python3 -m spacy download ja_core_news_lg
```

---------------------------------------------------------------------------------------------------------------------------------------------------
## **Quick Start**<a name="quick-start"></a>

Windows is assumed for the rest of this README, but the process should be similar for Linux. This is for the console version, for something less linear, see the [Web GUI](#webgui) section.

Due to PyPi limitations, you need to install SpaCy's JP Model, which can not be included automatically due to it being a direct dependency link which PyPi does not support. Make sure you do this after installing the requirements.txt file as it requires Kairyou/SpaCy to be installed first.

```bash
python -m spacy download ja_core_news_lg
```

Simply run Kudasai.py, enter a txt file path to the text you wish to preprocess/translate, and then insert a replacement json file path if you wish to use one. If you do not wish to use a replacement json file, you can simply input a blank space and Kudasai will skip preprocessing and go straight to translation.

Kudasai will offer to index the text, which is useful for finding new names to add to the replacement json file. This is optional and can be skipped.

After preprocessing is completed (if triggered), you will be prompted to choose a translation method.

You can choose between OpenAI, Gemini, and DeepL. Each have their own pros and cons, but OpenAI is the recommended translation method. DeepL and Gemini currently offer free versions, but all three require an api key, you will be prompted to enter this key when you choose to run the translation module.

Next, Kudasai will ask you to confirm it's settings. This can be overwhelming, but you can simply enter 1 to confirm and use the default settings. If you wish to change them, you can do so here.

See the [**Translator Settings**](#translator-settings) section for more information on Kudasai's Translation settings, but default should run fine. Inside the demo folder is a copy of the settings I use to translate COTE should you wish to use them. There is also a demo txt file in the demo folder that you can use to test Kudasai.

Kudasai will then ask if you want to change your api key, simply enter 2 for now. 

Next Kudasai will display an estimated cost of translation, this is based on the number of tokens in the preprocessed text as determined by tiktoken for OpenAI, by Google for Gemini, and by DeepL for DeepL. Kudasai will then prompt for confirmation, if this is fine, enter 1 to run the translation module otherwise 2 to exit.

Kudasai will then run the translation module and output the translated text and other logs to the output folder in the same directory as Kudasai.py.

These files are:

    "debug_log.txt" : A log of crucial information that occurred during Kudasai's run, useful for debugging or reporting issues as well as seeing what was done.

    "error_log.txt" : A log of errors that occurred during Kudasai's run if any, useful for debugging or reporting issues.

    "je_check_text.txt" : A log of the Japanese and English sentences that were paired together, useful for checking the accuracy of the translation and further editing of a machine translation.

    "preprocessed_text.txt" : The preprocessed text, the text output by Kairyou (preprocessor).

    "preprocessing_results.txt" : A log of the results of the preprocessing, shows what was replaced and how many times.

    "translated_text.txt" : The translated text, the text output by Kaiseki or Kijiku.

Old runs are stored in the archive folder in output as well.

If you have any questions, comments, or concerns, please feel free to open an issue.

---------------------------------------------------------------------------------------------------------------------------------------------------
## **Command Line Interface (CLI)**<a name="cli"></a>

Kudasai provides a Command Line Interface (CLI) for preprocessing and translating text files. This section details how to use the CLI, including the required and optional arguments for each mode.

### Usage

The CLI supports two modes: `preprocess` and `translate`. Each mode requires specific arguments to function properly.

#### Preprocess Mode

The `preprocess` mode preprocesses the text file using the provided replacement JSON file. 

**Command Structure:**

```bash
python path_to_kudasai.py preprocess <input_file> <replacement_json> [<knowledge_base>]
```

**Required Arguments:**
- `<input_file>`: Path to the text file to preprocess.
- `<replacement_json>`: Path to the replacement JSON file.

**Optional Arguments:**
- `<knowledge_base>`: Path to the knowledge base file (directory, file, or text).

**Example:**

```bash
python C:\\path\\to\\kudasai.py preprocess "C:\\path\\to\\input_file.txt" "C:\\path\\to\\replacement_json.json" "C:\\path\\to\\knowledge_base"
```

#### Translate Mode

The `translate` mode translates the text file using the specified translation method.

**Command Structure:**

```bash
python path_to_kudasai.py translate <input_file> <translation_method> [<translation_settings_json>] [<api_key>]
```

**Required Arguments:**
- `<input_file>`: Path to the text file to translate.

**Optional Arguments:**
- `<translation_method>`: Translation method to use (`'deepl'`, `'openai'`, or `'gemini'`). Defaults to `'deepl'`.
- `<translation_settings_json>`: Path to the translation settings JSON file (overrides current settings).
- `<api_key>`: API key for the translation service. If not provided, it will use the in the settings directory or prompt for it if that's not found.

**Example:**

```bash
python C:\\path\\to\\kudasai.py translate "C:\\path\\to\\input_file.txt" gemini "C:\\path\\to\\translation_settings.json" "YOUR_API_KEY"
```

### Additional Notes
- All arguments should be enclosed in double quotes if they contain spaces. Double quotes are optional and will be stripped. Single quotes are not allowed.
- For more information, refer to the documentation at `README.md`.

---------------------------------------------------------------------------------------------------------------------------------------------------

## **Preprocessing**<a name="preprocessing"></a>

Preprocessing is the act of preparing text for translation by replacing certain words or phrases with their translated counterparts. 

Kudasai uses Kairyou for preprocessing, which is a powerful preprocessor that can replace text in a text file based on a json file. This is useful for replacing names, places, and other things that may not translate well or to simply speed up the translation process.

You can run the preprocessor by using the CLI or simply running kudasai.py as instructed in the [Quick Start](#quick-start) section.

Many replacement json files are included in the jsons folder, you can also make your own if you wish provided it follows the same format. See an example below
Kudasai/Kairyou works with both Kudasai and Fukuin Json's, the below is a Kudasai type json.

![Example JSON](https://i.imgur.com/u3FnUia.jpg)

---------------------------------------------------------------------------------------------------------------------------------------------------

## **Translator**<a name="translator"></a>

Kudasai uses EasyTL for translation, which is a versatile translation library that uses several translation APIs to translate text.

Kudasai currently supports OpenAI, Gemini, and DeepL for translation. OpenAI is the recommended translation method, but DeepL and Gemini are also good alternatives.

You can run the translator by running kudasai.py as instructed in the [Quick Start](#quick-start) section.

Note that you need an API key for OpenAI, Gemini, and DeepL. You will be prompted to enter this key when you choose to run the translation module.

The translator has a lot of settings, simply using the default settings is fine or the one provided in the demo folder. You can also change these manually when confirming your settings, as well as loading a custom json as your settings by pressing c at this window, with the settings in the script directory.

The settings are fairly complex, see the below section [Translator Settings](#translator-settings) for more information.

---------------------------------------------------------------------------------------------------------------------------------------------------

## **Translator Settings**<a name="translator-settings"></a>

(Fairly technical, can be abstracted away by using default settings or someone else's settings file.)

    Base Translation Settings:

    prompt_assembly_mode : 1 or 2. 1 means the system message will actually be treated as a system message. 2 means it'll be treated as a user message. 1 is recommend for gpt-4 otherwise either works. For Gemini & DeepL, this setting is ignored.

    number_of_lines_per_batch : The number of lines to be built into a prompt at once. Theoretically, more lines would be more cost effective, but other complications may occur with higher lines. So far been tested up to 48 by me.

    sentence_fragmenter_mode : 1 or 2  (1 - via regex and other nonsense) 2 - None (Takes formatting and text directly from API return)) the API can sometimes return a result on a single line, so this determines the way Kudasai fragments the sentences if at all. Use 2 for newer models and Deepl.

    je_check_mode : 1 or 2, 1 will print out the jap then the english below separated by ---, 2 will attempt to pair the english and jap sentences, placing the jap above the eng. If it cannot, it will default to 1. Use 2 for newer models and DeepL.

    number_of_malformed_batch_retries : (Malformed batch is when je-fixing fails) How many times Kudasai will attempt to mend a malformed batch (mending is resending the request). Be careful with increasing as cost increases at (cost * length * n) at worst case. This setting is ignored if je_check_mode is set to 1.

    batch_retry_timeout : How long Kudasai will try to translate a batch in seconds, if a requests exceeds this duration, Kudasai will leave it untranslated.

    number_of_concurrent_batches : How many translations batches Kudasai will send to the translation API at a time. For OpenAI, be conservative as rate-limiting is aggressive, I'd suggest 3-5. For Gemini, do not exceed 15 for 1.0 or 2 for 1.5. This setting more or less doesn't matter for DeepL.
    ----------------------------------------------------------------------------------
    Open AI Settings:
    See https://platform.openai.com/docs/api-reference/chat/create for further details
    ----------------------------------------------------------------------------------
    openai_model : ID of the model to use. Kudasai only works with 'chat' models.

    openai_system_message : Instructions to the model. Basically tells the model how to translate.

    openai_temperature : What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. Lower values are typically better for translation.

    openai_top_p : An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. I generally recommend altering this or temperature but not both.

    openai_n : How many chat completion choices to generate for each input message. Do not change this, as Kudasai will always use 1.

    openai_stream : If set, partial message deltas will be sent, like in ChatGPT. Tokens will be sent as data-only server-sent events as they become available, with the stream terminated by a data: [DONE] message. See the OpenAI python library on GitHub for example code. Do not change this as Kudasai does not support this feature.

    openai_stop : Up to 4 sequences where the API will stop generating further tokens. Do not change this as Kudasai does not support this feature.

    openai_logit_bias : Modifies the likelihood of specified tokens appearing in the completion. Do not change this as Kudasai does not support this feature.

    openai_max_tokens :  The maximum number of tokens to generate in the chat completion. The total length of input tokens and generated tokens is limited by the model's context length. I wouldn't recommend changing this. Is none by default. If you change to an integer, make sure it doesn't exceed that model's context length or your request will fail and repeat till timeout.

    openai_presence_penalty : Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics. While negative values encourage repetition. Should leave this at 0.0.

    openai_frequency_penalty : Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim. Negative values encourage repetition. Should leave this at 0.0.
    ----------------------------------------------------------------------------------
    openai_stream, openai_logit_bias, openai_stop and openai_n are included for completion's sake, current versions of Kudasai will hardcode their values when validating the translation_settings.json to their default values. As different values for these settings do not have a use case in Kudasai's current implementation.
    ----------------------------------------------------------------------------------
    Gemini Settings:
    See https://ai.google.dev/docs/concepts#model-parameters for further details
    ----------------------------------------------------------------------------------
    gemini_model : The model to use. Currently only supports gemini-pro and gemini-pro-vision, the 1.0 model and 1.5 models and their aliases.

    gemini_prompt : Instructions to the model. Basically tells the model how to translate.

    gemini_temperature : What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. Lower values are typically better for translation.

    gemini_top_p : An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. I generally recommend altering this or temperature but not both.

    gemini_top_k : Determines the number of most probable tokens to consider for each selection step. A higher value increases diversity, a lower value makes the output more deterministic.

    gemini_candidate_count : The number of candidates to generate for each input message. Do not change this as Kudasai will always use 1.

    gemini_stream : If set, partial message deltas will be sent, like in Gemini Chat. Tokens will be sent as data-only server-sent events as they become available, with the stream terminated by a data: [DONE] message. Do not change this as Kudasai does not support this feature.

    gemini_stop_sequences : Up to 4 sequences where the API will stop generating further tokens. Do not change this as Kudasai does not support this feature.

    gemini_max_output_tokens : The maximum number of tokens to generate in the chat completion. The total length of input tokens and generated tokens is limited by the model's context length. I wouldn't recommend changing this. Is none by default. If you change to an integer, make sure it doesn't exceed that model's context length or your request will fail and repeat till timeout.
    ----------------------------------------------------------------------------------
    gemini_stream, gemini_stop_sequences and gemini_candidate_count are included for completion's sake, current versions of Kudasai will hardcode their values when validating the translation_settings.json to their default values. As different values for these settings do not have a use case in Kudasai's current implementation.
    ----------------------------------------------------------------------------------
    Deepl Settings:
    See https://developers.deepl.com/docs/api-reference/translate for further details
    ----------------------------------------------------------------------------------
    deepl_context : The context in which the text should be translated. This is used to improve the translation. If you don't have any context, you can leave this empty. This is a DeepL Alpha feature and could be subject to change.

    deepl_split_sentences : How the text should be split into sentences. Possible values are 'OFF', 'ALL', 'NO_NEWLINES'.

    deepl_preserve_formatting : Whether the formatting of the text should be preserved. If you don't want to preserve the formatting, you can set this to False. Otherwise, set it to True.

    deepl_formality : The formality of the text. Possible values are 'default', 'more', 'less', 'prefer_more', 'prefer_less'.

---------------------------------------------------------------------------------------------------------------------------------------------------

## **Web GUI**<a name="webgui"></a>

Kudasai also offers a Web GUI. It has all the main functionality of the program but in an easier and non-linear way.

To run the Web GUI, simply run webgui.py which is in the same directory as kudasai.py

Below are some images of the Web GUI.

Detailed Documentation for this can be found on the Hugging Face hosted version of Kudasai [here](https://huggingface.co/spaces/Bikatr7/Kudasai/blob/main/README.md).

Name Indexing | Kairyou:
![Name Indexing Screen | Kairyou](https://i.imgur.com/QCPqjrw.jpeg)

Text Preprocessing | Kairyou:
![Text Preprocessing Screen | Kairyou](https://i.imgur.com/r8nHEvw.jpeg)

Text Translation | Translator:
![Text Translation Screen | Translator](https://i.imgur.com/0E9q2eh.jpeg)

Translation Settings Page 1:
![Translation Settings Page 1](https://i.imgur.com/0E9q2eh.jpeg)

Translation Settings Page 2:
![Translation Settings Page 2](https://i.imgur.com/8MQk6pL.jpeg)

Logging Page:
![Logging Page](https://i.imgur.com/vDPCUQC.jpeg)

---------------------------------------------------------------------------------------------------------------------------------------------------

## **Hugging Face**<a name="huggingface"></a>

For those who are interested, or simply cannot run Kudasai locally, a instance of Kudasai's WebGUI is hosted on Hugging Face's servers. You can find it [here](https://huggingface.co/spaces/Bikatr7/Kudasai).

It's a bit slower than running it locally, but it's a good alternative for those who cannot run it locally. The webgui on huggingface does not save anything through runs, so you will need to download the output files or copy the text out of the webgui. API keys are not saved, and the output folder is overwritten every time it loads. Archives deleted every run as well.

To see the README for the Hugging Face hosted version of Kudasai, please see [here](https://huggingface.co/spaces/Bikatr7/Kudasai/blob/main/README.md).

---------------------------------------------------------------------------------------------------------------------------------------------------
## **License**<a name="license"></a>

This project (Kudasai) is licensed under the GNU General Public License (GPL). You can find the full text of the license in the [LICENSE](License.md) file.

The GPL is a copyleft license that promotes the principles of open-source software. It ensures that any derivative works based on this project must also be distributed under the same GPL license. This license grants you the freedom to use, modify, and distribute the software.

Please note that this information is a brief summary of the GPL. For a detailed understanding of your rights and obligations under this license, please refer to the full license text.

---------------------------------------------------------------------------------------------------------------------------------------------------
## **Contact**<a name="contact"></a>

If you have any questions, comments, or concerns, please feel free to contact me at [Bikatr7@proton.me](mailto:Bikatr7@proton.me)

For any bugs or suggestions please use the issues tab [here](https://github.com/Bikatr7/Kudasai/issues).

I actively encourage and welcome any feedback on this project.

---------------------------------------------------------------------------------------------------------------------------------------------------

## **Acknowledgements**<a name="acknowledgements"></a>

Kudasai gets it's original name idea from it's inspiration, Atreyagaurav's Onegai. Which also means please. You can find that [here](https://github.com/Atreyagaurav/onegai)

---------------------------------------------------------------------------------------------------------------------------------------------------