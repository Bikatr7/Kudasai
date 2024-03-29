---------------------------------------------------------------------------------------------------------------------------------------------------
**Table of Contents**

- [Notes](#notes)
- [Dependencies](#dependencies)
- [Naming Conventions](#naming-conventions)
- [Quick Start](#quick-start)
- [Kairyou](#kairyou)
- [Kaiseki](#kaiseki)
- [Kijiku](#kijiku)
- [Kijiku Settings](#kijiku-settings)
- [Web GUI](#webgui)
- [Hugging Face](#huggingface)
- [License](#license)
- [Contact](#contact)

---------------------------------------------------------------------------------------------------------------------------------------------------
**Notes**<a name="notes"></a>

Windows 10 and Linux Mint are the only tested operating systems, feel free to test on other operating systems and report back to me. I will do my best to fix any issues that arise.

To see the README for the Hugging Face hosted version of Kudasai, please see [here](https://huggingface.co/spaces/Bikatr7/Kudasai/blob/main/README.md). Further WebGUI documentation can be found there as well.

Python version: 3.10+

Streamlining Japanese-English Translation with Advanced Preprocessing and Integrated Translation Technologies.

Preprocessor is sourced from an external package, which I also designed, called [Kairyou](https://github.com/Bikatr7/Kairyou).

Kudasai has a public trello board, you can find it [here](https://trello.com/b/Wsuwr24S/kudasai) to see what I'm working on.

---------------------------------------------------------------------------------------------------------------------------------------------------
**Dependencies**<a name="dependencies"></a>

deepl==1.16.1

openai==1.13.3

backoff==2.2.1

tiktoken==0.6.0

gradio==4.19.2

kairyou==1.4.1

google-generativeai==0.4.0

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
**Naming Conventions**<a name="naming-conventions"></a> 

kudasai.py - Main script - ください　- Please

Kairyou - Preprocessing Package - 改良 - Reform

kaiseki.py - DeepL translation module - 解析 - Parsing

kijiku.py - OpenAI translation module - 基軸 - Foundation

Kudasai gets it's original name idea from it's inspiration, Atreyagaurav's Onegai. Which also means please. You can find that [here](https://github.com/Atreyagaurav/onegai)

---------------------------------------------------------------------------------------------------------------------------------------------------
**Quick Start**<a name="quick-start"></a>

Windows is assumed for the rest of this README, but the process should be similar for Linux. This is for the console version, for something less linear, see the [Web GUI](#webgui) section.

Due to PyPi limitations, you need to install Spacy's JP Model, which can not be included automatically due to it being a direct dependency link which PyPi does not support. Make sure you do this after installing the requirements.txt file as it requires spacy to be installed first.

```bash
python -m spacy download ja_core_news_lg
```

Simply run Kudasai.py, enter a txt file path to the text you wish to translate, and then insert a replacement json file path if you wish to use one. If you do not wish to use a replacement json file, you can simply input a blank space and Kudasai will skip preprocessing and go straight to translation.

Kudasai will offer to index the text, which is useful for finding new names to add to the replacement json file. This is optional and can be skipped.

After preprocessing is completed (if triggered), you will be prompted to run the translation modules.

I recommend using Kijiku as it is vastly superior.

See the [Kijiku Settings](#kijiku-settings) section for more information on Kijiku's settings, but default should run fine. Inside the demo folder is a copy of the settings I use to translate COTE should you wish to use them. There is also a demo txt file in the demo folder that you can use to test Kudasai.

Follow the prompts from there and you should be good to go, results will be stored in the output folder in the same directory as kudasai.py.

If you have any questions, comments, or concerns, please feel free to open an issue.

---------------------------------------------------------------------------------------------------------------------------------------------------

**Kairyou**<a name="kairyou"></a>

Kairyou is the preprocessing package, it is used to preprocess Japanese text to make it easier to translate. It is the first step taken when running Kudasai.

To run Kairyou and by extension Kudasai, you may use the CLI or the Console.

You can run the console by simply clicking on kudasai.py, this will open the console and you can follow the prompts from there.

If you wish to use the CLI, you can do so by opening a command prompt and entering the following:

```python Path to Kudasai.py Path to the text you are preprocessing Path to the replacement json file```

i.e.

    Path to Kudasai.py

    Path to the text you are preprocessing

    Path to the replacement json file

You can omit the replacement json file if you do not wish to use one. This will skip preprocessing and go straight to translation.

See an example of a command line entry below

![Example CMD](https://i.imgur.com/eQmVaYY.png)

Many replacement json files are included in the jsons folder, you can also make your own if you wish provided it follows the same format. See an example below
Kudasai/Kairyou works with both Kudasai and Fukuin Json's, the below is a Kudasai type json.

![Example JSON](https://i.imgur.com/u3FnUia.jpg)

Upon Kudasai being run, it will create a folder called "output" which will contain 5 files. It is located in the same directory as kudasai.py.

Old runs are stored in the archive folder in output as well.

These files are:

    "debug_log.txt" : A log of crucial information that occurred during Kudasai's run, useful for debugging or reporting issues as well as seeing what was done.

    "error_log.txt" : A log of errors that occurred during Kudasai's run if any, useful for debugging or reporting issues.

    "je_check_text.txt" : A log of the Japanese and English sentences that were paired together, useful for checking the accuracy of the translation and further editing of a machine translation.

    "preprocessed_text.txt" : The preprocessed text, the text output by Kairyou (preprocessor).

    "preprocessing_results.txt" : A log of the results of the preprocessing, shows what was replaced and how many times.

    "translated_text.txt" : The translated text, the text output by Kaiseki or Kijiku.

Kairyou will ask if you'd like to index the text, this is useful for finding new names to add to the replacement json file. If you select 1 for yes, you need to provide a knowledge base, this can either be txt, a path to a txt file, or a path to a folder containing txt files. Kairyou will then index the all three sources and Kudasai will flag all new names with >>><<< in the preprocessed text. 

After preprocessing is completed, you will be prompted to run a translation module. If you choose to do so, you will be prompted to choose between Kaiseki and Kijiku. See the sections below for more information on each translation module.

---------------------------------------------------------------------------------------------------------------------------------------------------

**Kaiseki**<a name="kaiseki"></a>

Kaiseki is the DeepL translation module, it is used to translate Japanese to English. It is *flawed* and not very accurate compared to Kijiku although it is still useful for some things.

Kaiseki is effectively deprecated and is only maintained. Do not expect any updates to it anytime soon other than bug fixes or compatibility updates.

Please note an API key is required for Kaiseki to work, you can get one [here](https://www.deepl.com/pro#developer).

It is free under 500k characters per month.

If you accept the prompt and choose '1' to run Kaiseki, you will be prompted to enter your api key. Provided all goes well, Kaiseki will run and translate the preprocessed text and no other input is required.

Your translated text will be stored in the output folder in the same directory as kudasai.py.

Kaiseki will store your obfuscated api key locally under KudasaiSecrets under %APPDATA% or ~/.config/ depending on your OS. 

---------------------------------------------------------------------------------------------------------------------------------------------------

**Kijiku**<a name="kijiku"></a>

Kijiku is the LLM translation module, it is used to translate Japanese to English. It is very accurate and is the recommended translation module. 

You also need an api key for Kijiku to work.

You can get one here for OpenAI [here](https://platform.openai.com/)

and for Gemini is a bit more complicated, you'll need to make a google cloud project, enable the vertex AI API, and then create an api key. Although Gemini is free under 60 requests at once as of Kudasai v3.4.0. [This](https://ai.google.dev/tutorials/setup) should help you get started.

Kijiku is vastly more complicated and has a lot of steps, so let's go over them.

Provided you accept the prompt and choose '2' to run Kijiku, you will be prompted to choose a LLM. Then to enter your api key. Provided all goes well, Kijiku will attempt to load it's settings from KudasaiConfig, if it cannot find them, it will create them from the default. Kijiku will store your obfuscated api key locally under KudasaiSecrets under %APPDATA% or ~/.config/ depending on your OS.

You will be prompted if you'd like to change these settings, if you choose to do so, you'll be asked for which setting you'd like to change, and what to change it too, until you choose to exit. Multiple things can be done in this menu, so follow the prompts. If you want to change anything about the settings, you do it here.

You can also choose to upload your own settings file in the settings change menu, this is useful if you want to use someone else's settings file. You would do so by placing the json file in the same directory as kudasai.py and then selecting 'c' in the settings change menu. This will load the file in and use it as your settings instead.

You can change your api key right after this step if you wish.

After that you will be shown an estimated cost of translation, this is based on the number of tokens in the preprocessed text as determined by tiktoken for OpenAI, and by Google for Gemini. Kijiku will then prompt for confirmation, run, and translate the preprocessed text and no other input is required.

Your translated text will be stored in the output folder in the same directory as kudasai.py.

Also note that Kijiku's settings are somewhat complex, please see the section below for more information on them if you wish to change them.

---------------------------------------------------------------------------------------------------------------------------------------------------

**Kijiku Settings**<a name="kijiku-settings"></a>

(Fairly technical, can be abstracted away by using default settings or someone else's settings file.)

    ----------------------------------------------------------------------------------
    Kijiku Settings:

    prompt_assembly_mode : 1 or 2. 1 means the system message will actually be treated as a system message. 2 means it'll be treated as a user message. 1 is recommend for gpt-4 otherwise either works. For Gemini, this setting is ignored.

    number_of_lines_per_batch : The number of lines to be built into a prompt at once. Theoretically, more lines would be more cost effective, but other complications may occur with higher lines. So far been tested up to 48.

    sentence_fragmenter_mode : 1 or 2  (1 - via regex and other nonsense) 2 - None (Takes formatting and text directly from API return)) the API can sometimes return a result on a single line, so this determines the way Kijiku fragments the sentences if at all. Use 2 for newer models.

    je_check_mode : 1 or 2, 1 will print out the jap then the english below separated by ---, 2 will attempt to pair the english and jap sentences, placing the jap above the eng. If it cannot, it will default to 1. Use 2 for newer models.

    number_of_malformed_batch_retries : (Malformed batch is when je-fixing fails) How many times Kijiku will attempt to mend a malformed batch (mending is resending the request), only for gpt4. Be careful with increasing as cost increases at (cost * length * n) at worst case. This setting is ignored if je_check_mode is set to 1.

    batch_retry_timeout : How long Kijiku will try to translate a batch in seconds, if a requests exceeds this duration, Kijiku will leave it untranslated.

    number_of_concurrent_batches : How many translations batches Kijiku will send to the translation API at a time. For OpenAI, be conservative as rate-limiting is aggressive, I'd suggest 3-5. For Gemini, do not exceed 60.
    ----------------------------------------------------------------------------------
    Open AI Settings:
    See https://platform.openai.com/docs/api-reference/chat/create for further details
    ----------------------------------------------------------------------------------
    openai_model : ID of the model to use. Kijiku only works with 'chat' models.

    openai_system_message : Instructions to the model. Basically tells the model how to translate.

    openai_temperature : What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. Lower values are typically better for translation.

    openai_top_p : An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. I generally recommend altering this or temperature but not both.

    openai_n : How many chat completion choices to generate for each input message. Do not change this.

    openai_stream : If set, partial message deltas will be sent, like in ChatGPT. Tokens will be sent as data-only server-sent events as they become available, with the stream terminated by a data: [DONE] message. See the OpenAI python library on GitHub for example code. Do not change this.

    openai_stop : Up to 4 sequences where the API will stop generating further tokens. Do not change this.

    openai_logit_bias : Modifies the likelihood of specified tokens appearing in the completion. Do not change this.

    openai_max_tokens :  The maximum number of tokens to generate in the chat completion. The total length of input tokens and generated tokens is limited by the model's context length. I wouldn't recommend changing this. Is none by default. If you change to an integer, make sure it doesn't exceed that model's context length or your request will fail and repeat till timeout.

    openai_presence_penalty : Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics. While negative values encourage repetition. Should leave this at 0.0.

    openai_frequency_penalty : Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim. Negative values encourage repetition. Should leave this at 0.0.
    ----------------------------------------------------------------------------------
    openai_stream, openai_logit_bias, openai_stop and openai_n are included for completion's sake, current versions of Kudasai will hardcode their values when validating the Kijiku_rule.json to their default values. As different values for these settings do not have a use case in Kudasai's current implementation.
    ----------------------------------------------------------------------------------
    Gemini Settings:
    https://ai.google.dev/docs/concepts#model-parameters for further details
    ----------------------------------------------------------------------------------
    gemini_model : The model to use. Currently only supports gemini-pro and gemini-pro-vision, the 1.0 model and it's aliases.

    gemini_prompt : Instructions to the model. Basically tells the model how to translate.

    gemini_temperature : What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. Lower values are typically better for translation.

    gemini_top_p : An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. I generally recommend altering this or temperature but not both.

    gemini_top_k : Determines the number of most probable tokens to consider for each selection step. A higher value increases diversity, a lower value makes the output more deterministic.

    gemini_candidate_count : The number of candidates to generate for each input message. Do not change this.

    gemini_stream : If set, partial message deltas will be sent, like in Gemini Chat. Tokens will be sent as data-only server-sent events as they become available, with the stream terminated by a data: [DONE] message. Do not change this.

    gemini_stop_sequences : Up to 4 sequences where the API will stop generating further tokens. Do not change this.

    gemini_max_output_tokens : The maximum number of tokens to generate in the chat completion. The total length of input tokens and generated tokens is limited by the model's context length. I wouldn't recommend changing this. Is none by default. If you change to an integer, make sure it doesn't exceed that model's context length or your request will fail and repeat till timeout.
    ----------------------------------------------------------------------------------
    gemini_stream, gemini_stop_sequences and gemini_candidate_count are included for completion's sake, current versions of Kudasai will hardcode their values when validating the Kijiku_rule.json to their default values. As different values for these settings do not have a use case in Kudasai's current implementation.
    ----------------------------------------------------------------------------------

---------------------------------------------------------------------------------------------------------------------------------------------------

**Web GUI**<a name="webgui"></a>

Kudasai also offers a Web GUI. It has all the main functionality of the program but in an easier and non-linear way.

To run the Web GUI, simply run webgui.py which is in the same directory as kudasai.py

Below are some images of the Web GUI.

Detailed Documentation for this can be found on the Hugging Face hosted version of Kudasai [here](https://huggingface.co/spaces/Bikatr7/Kudasai/blob/main/README.md).

Indexing | Kairyou:
![Indexing Screen | Kairyou](https://i.imgur.com/0a2mzOI.png)

Preprocessing | Kairyou:
![Preprocessing Screen | Kairyou](https://i.imgur.com/2pt06gC.png)

Translation | Kaiseki:
![Translation Screen | Kaiseki](https://i.imgur.com/X98JYsp.png)

Translation | Kijiku:
![Translation Screen | Kijiku](https://i.imgur.com/X6IxyL8.png)

Kijiku Settings:
![Kijiku Settings](https://i.imgur.com/VX0fGd5.png)

Logging:
![Logging](https://i.imgur.com/IkUjpXR.png)

---------------------------------------------------------------------------------------------------------------------------------------------------

**Hugging Face**<a name="huggingface"></a>

For those who are interested, or simply cannot run Kudasai locally, a instance of Kudasai's WebGUI is hosted on Hugging Face's servers. You can find it [here](https://huggingface.co/spaces/Bikatr7/Kudasai).

It's a bit slower than running it locally, but it's a good alternative for those who cannot run it locally. The webgui on huggingface does not save anything through runs, so you will need to download the output files or copy the text out of the webgui. API keys are not saved, and the output folder is overwritten every time you run it. Archives deleted every run as well.

To see the README for the Hugging Face hosted version of Kudasai, please see [here](https://huggingface.co/spaces/Bikatr7/Kudasai/blob/main/README.md).

---------------------------------------------------------------------------------------------------------------------------------------------------
**License**<a name="license"></a>

This project (Kudasai) is licensed under the GNU General Public License (GPL). You can find the full text of the license in the [LICENSE](License.md) file.

The GPL is a copyleft license that promotes the principles of open-source software. It ensures that any derivative works based on this project must also be distributed under the same GPL license. This license grants you the freedom to use, modify, and distribute the software.

Please note that this information is a brief summary of the GPL. For a detailed understanding of your rights and obligations under this license, please refer to the full license text.

---------------------------------------------------------------------------------------------------------------------------------------------------
**Contact**<a name="contact"></a>

If you have any questions, comments, or concerns, please feel free to contact me at [Tetralon07@gmail.com](mailto:Tetralon07@gmail.com).

For any bugs or suggestions please use the issues tab [here](https://github.com/Bikatr7/Kudasai/issues).

Once again, I actively encourage and welcome any feedback on this project.

---------------------------------------------------------------------------------------------------------------------------------------------------
