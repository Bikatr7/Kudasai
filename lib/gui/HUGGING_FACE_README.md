---
license: gpl-3.0
title: Kudasai
sdk: gradio
emoji: 🈷️
python_version: 3.10.0
app_file: webgui.py
colorFrom: gray
colorTo: gray
short_description: Japanese-English preprocessor with automated translation.
pinned: true
---

---------------------------------------------------------------------------------------------------------------------------------------------------
**Table of Contents**

- [**Notes**](#notes)
- [**General Usage**](#general-usage)
- [**Indexing and Preprocessing**](#indexing-and-preprocessing)
- [**Translator**](#translator)
- [**Translator Settings**](#translator-settings)
- [**Web GUI**](#web-gui)
- [**License**](#license)
- [**Contact**](#contact)
- [**Acknowledgements**](#acknowledgements)

---------------------------------------------------------------------------------------------------------------------------------------------------
## **Notes**<a name="notes"></a>

This readme is for the Hugging Space instance of Kudasai's WebGUI and the WebGUI itself, to run Kudasai locally or see any info on the project, please see the [GitHub Page](https://github.com/Bikatr7/Kudasai).

Streamlining Japanese-English Translation with Advanced Preprocessing and Integrated Translation Technologies.

Preprocessor and Translation logic is sourced from external packages, which I also designed, see [Kairyou](https://github.com/Bikatr7/Kairyou) and [EasyTL](https://github.com/Bikatr7/easytl) for more information.

Kudasai has a public trello board, you can find it [here](https://trello.com/b/Wsuwr24S/kudasai) to see what I'm working on and what's coming up.

The WebGUI on huggingface does not save anything through runs, so you will need to download the output files or copy the text out of the webgui. API keys are not saved, and the output folder is overwritten every time you run it. Archives deleted every run as well.

Kudasai is proud to have been a Backdrop Build v3 Finalist:
https://backdropbuild.com/builds/v3/kudasai

---------------------------------------------------------------------------------------------------------------------------------------------------

## **General Usage**<a name="general-usage"></a>

Kudasai's WebGUI is pretty easy to understand for the general usage, most incorrect actions will be caught by the system and a message will be displayed to the user on how to correct it.

Normally, Kudasai would save files to the local system, but on Hugging Face's servers, this is not possible. Instead, you'll have to click the 'Save As' button to download the files to your local system.

Or you can click the copy button on the top right of textbox modals to copy the text to your clipboard.

For further details, see below chapters.

---------------------------------------------------------------------------------------------------------------------------------------------------

## **Indexing and Preprocessing**<a name="kairyou"></a>

This section can be skipped if you're only interested in translation or do not know what indexing or preprocessing is.

Indexing is not for everyone, only use it if you have a large amount of previous text and want to flag new names. It can be a very slow and long process, especially on Hugging Face's servers. It's recommended to use a local version of Kudasai for this process.

You'll need a txt file or some text to index. You'll also need a knowledge base, this can either be a single txt file or a directory of them, as well as a replacements json. Either Kudasai or Fukuin Type works. See [this](https://github.com/Bikatr7/Kairyou?tab=readme-ov-file#kairyou) for further details on replacement jsons.

Please do indexing before preprocessing, output is neater that way.

For Preprocessing, you'll need a txt file or some text to preprocess. You'll also need a replacements json. Either Kudasai or Fukuin Type works like with indexing.

For both, text is put in the textbox modals, with the output text being in the first field, and results being in the second field. 

They both have a debug field, but neither module really uses it.

---------------------------------------------------------------------------------------------------------------------------------------------------

## **Translator**<a name="translator"></a>

Kudasai supports 3 different translation methods at the moment, OpenAI's GPT, Google's Gemini, and DeepL. 

For OpenAI, you'll need an API key, you can get one [here](https://platform.openai.com/docs/api-reference/authentication). This is a paid service with no free tier.

For Gemini, you'll also need an API key, you can get one [here](https://ai.google.dev/tutorials/setup). Gemini is free to use under a certain limit, 2 RPM for 1.5 and 15 RPM for 1.0.

For DeepL, you'll need an API key too, you can get one [here](https://www.deepl.com/pro#developer). DeepL is also a paid service but is free under 500k characters a month.

I'd recommend using GPT for most things, as it's generally better at translation.

Mostly straightforward, choose your translation method, fill in your API key, and select your text. You'll also need to add your settings file if on HuggingFace if you want to tune the output, but the default is generally fine.

You can calculate costs here or just translate. Output will show in the appropriate fields.

For further details on the settings file, see [here](#translation-with-llms-settings).

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

Below are some images of the Web GUI.

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
