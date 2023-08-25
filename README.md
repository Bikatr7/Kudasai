---------------------------------------------------------------------------------------------------------------------------------------------------
**Table of Contents**

- [Notes](#notes)
- [Naming Conventions](#naming-conventions)
- [Dependencies](#dependencies)
- [Known Issues During Installation](#known-issues-during-installation)
- [Kairyou](#kairyou)
- [Kaiseki](#kaiseki)
- [Kijiku](#kijiku)
- [Kijiku Settings](#kijiku-settings)
- [GUI](#gui)
- [License](#license)
- [Contact](#contact)

---------------------------------------------------------------------------------------------------------------------------------------------------
**Notes**<a name="notes"></a>

Built for Windows, should work on Linux/MacOS but is untested.

Python version: 3.8+

It should work with 3.8, although it is untested. I recommend using 3.9+

Used to make (Japanese - English) translation easier by preprocessing the Japanese text (optional auto translation using deepL/openai API).

Preprocessor originally derived from https://github.com/Atreyagaurav/mtl-related-scripts

---------------------------------------------------------------------------------------------------------------------------------------------------
**Naming Conventions**<a name="naming-conventions"></a> 

Kudasai.py - Main Script - ください　- Please

Kairyou.py - preprocessing module - 改良 - Reform

Kaiseki.py - deepL translation module - 解析 - Parsing

Kijiku.py - openai translation module - 基軸 - Foundation

---------------------------------------------------------------------------------------------------------------------------------------------------
**Dependencies**<a name="dependencies"></a>

spacy[jp]

spacy[en]

ja_core_news_lg

en_core_web_lg

deepl

openai

backoff

requests

tiktoken

or see requirements.txt

---------------------------------------------------------------------------------------------------------------------------------------------------
**Known Issues During Installation**<a name="known-issues-during-installation"></a>

Please note that issues can occur when trying to install these dependencies:

python -m spacy download ja_core_news_lg

python -m spacy download en_core_web_lg

if these do not work, either reinstall spacy or try:

pip install en_core_web_lg

pip install ja_core_news_lg

---------------------------------------------------------------------------------------------------------------------------------------------------

**Kairyou**<a name="kairyou"></a>

Kairyou is the preprocessing module, it is used to preprocess Japanese text to make it easier to translate. It is the first step in the process.

To run Kairyou and by extension Kudasai, you must use the command line. You can do so by opening a command prompt and entering the following command:

```python Path to Kudasai.py Path to the text you are preprocessing Path to the replacement json file```

Where the following is replaced with the appropriate information:

i.e.

    Path to Kudasai.py

    Path to the text you are preprocessing

    Path to the replacement json file

See an example of a command line entry below

![Example CMD](https://i.imgur.com/eQmVaYY.png)

Many replacement json files are included in the replacements jsons folder, you can also make your own if you wish provided it follows the same format. See an example below

![Example JSON](https://i.imgur.com/qgCI9w9.png)

If you do not wish to use a replacement json file, you can use the blank replacement json file provided in the replacements folder. This also serves as a template for making your own replacement json files.

Upon Kudasai being run, it will create a folder called "KudasaiOutput" which will contain 5 files. It is located in the same directory as Kudasai.py.

These files are:

    "debug log.txt" : A log of most actions taken by Kudasai, useful for debugging.

    "error log.txt" : A log of errors that occurred during Kudasai's run, useful for debugging or reporting issues.

    "jeCheck.txt" : A log of the Japanese and English sentences that were paired together, useful for checking the accuracy of the translation and further editing of a machine translation.

    "Kairyou Results.txt" : A log of the results of Kairyou's run, shows what was replaced and how many times it was replaced.

    "preprocessedText.txt" : The preprocessed text, the preprocessed text output by Kairyou.

    "translatedText.txt" : The translated text, the translated text output by Kaiseki or Kijiku.

After preprocessing is completed, you will be prompted to run the translation modules.

---------------------------------------------------------------------------------------------------------------------------------------------------

**Kaiseki**<a name="kaiseki"></a>

Kaiseki is a deepl translation module, it is used to translate Japanese to English. It is flawed and not very accurate compared to Kijiku although plans are in place to develop a better version.

Please note an api key is required for Kaiseki to work, you can get one here: https://www.deepl.com/pro#developer.

It is free under 500k characters per month.

If you accept the prompt and choose '1' to run Kaiseki, you will be prompted to enter your api key. Provided all goes well, Kaiseki will run and translate the preprocessed text and no other input is required.

Kaiseki will store your obfuscated api key locally under KudasaiConfig under your user directory. 

---------------------------------------------------------------------------------------------------------------------------------------------------

**Kijiku**<a name="kijiku"></a>

Kijiku is an openai translation module, it is used to translate Japanese to English. It is very accurate and is the recommended translation module. 

You also need an api key for Kijiku to work, you can get one here: https://beta.openai.com/

Currently, you can get a free api trial credit that lasts for a month and is worth around 15 dollars.

Kijiku is vastly more complicated and has a lot of steps, so let's go over them.

Provided you accept the prompt and choose '2' to run Kijiku, you will be prompted to enter your api key. Provided all goes well, Kijiku will attempt to load it's settings from KudasaiConfig, if it cannot find them, it will create them.

Kijiku will store your obfuscated api key locally under KudasaiConfig under your user directory. 

You will also be prompted if you'd like to change these settings, if you choose to do so, you'll be asked for which setting you'd like to change, and what to change it too, until you choose to exit. Multiple things can be done in this menu. If you want to change anything about the settings, you do it here.

You can also choose upload your own settings file in the setting change menu, this is useful if you want to use someone else's settings file. You would do so by placing the json file in the same directory as Kudasai.py and then selecting 'c' in the settings change menu. This will load the file in and use it as your settings.

After that you will be shown an estimated cost of translation, this is based on the number of tokens in the preprocessed text. Kijiku will then run and translate the preprocessed text and no other input is required.

Please note that translation with Kijiku can take a very long time depending on the length of the text and the number of tokens. It is not uncommon for it to take hours or more for long texts. Plans are in place to make Kijiku asynchronous to speed up translation.

Also note that Kijiku's settings are very complex, please see the section below for more information on them.

---------------------------------------------------------------------------------------------------------------------------------------------------

**Kijiku Settings**<a name="kijiku-settings"></a>

See https://platform.openai.com/docs/api-reference/chat/create for further details

    model : ID of the model to use. As of right now, Kijiku only works with 'chat' models.

    temperature : What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. Lower Values are typically better for translation

    top_p : An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. I generally recommend altering this or temperature but not both.

    n : How many chat completion choices to generate for each input message. Do not change this.

    stream : If set, partial message deltas will be sent, like in ChatGPT. Tokens will be sent as data-only server-sent events as they become available, with the stream terminated by a data: [DONE] message. See the OpenAI Cookbook for example code. Do not change this.

    stop : Up to 4 sequences where the API will stop generating further tokens. Do not change this.

    max_tokens :  The maximum number of tokens to generate in the chat completion. The total length of input tokens and generated tokens is limited by the model's context length. I wouldn't recommend changing this

    presence_penalty : Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.

    frequency_penalty : Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.

    logit_bias : Modify the likelihood of specified tokens appearing in the completion. Do not change this.

    system_message : Instructions to the model. Do not change this unless you know what you're doing.

    message_mode : 1 or 2. 1 means the system message will actually be treated as a system message. 2 means it'll be treating as a user message. 1 is recommend for gpt-4 otherwise either works.

    num_lines : the number of lines to be built into a prompt at once. Theoretically, more lines would be more cost effective, but other complications may occur with higher lines.

    sentence_fragmenter_mode : 1 or 2 or 3 (1 - via regex and other nonsense, 2 - NLP via spacy, 3 - None (Takes formatting and text directly from ai return)) the api can sometimes return a result on a single line, so this determines the way Kijiku fragments the sentences if at all.

    je_check_mode : 1 or 2, 1 will print out the 'num_lines' amount of jap then the english below separated by ---, 2 will attempt to pair the english and jap sentences, placing the jap above the eng. If  it cannot, it will do 1.

    Please note that while logit_bias and max_tokens can be changed, Kijiku does not currently do anything with them.

---------------------------------------------------------------------------------------------------------------------------------------------------
**GUI**<a name="gui"></a>

GUI.py is a GUI Interface for Kudasai, it also provides visuals for Kaiseki and Kijiku.

Please note that the GUI can appear unresponsive while translating or preprocessing, this is normal.

A console also launches with the gui, it is mostly for visuals but you will be required to confirm your settings if you choose to run Kijiku.

![Example GUI](https://i.imgur.com/JqIj5bE.png)

---------------------------------------------------------------------------------------------------------------------------------------------------
**License**<a name="license"></a>

This project (Kudasai) is licensed under the GNU General Public License (GPL). You can find the full text of the license in the [LICENSE](License.md) file.

The GPL is a copyleft license that promotes the principles of open-source software. It ensures that any derivative works based on this project must also be distributed under the same GPL license. This license grants you the freedom to use, modify, and distribute the software.

Please note that this information is a brief summary of the GPL. For a detailed understanding of your rights and obligations under this license, please refer to the full license text.

---------------------------------------------------------------------------------------------------------------------------------------------------
**Contact**<a name="contact"></a>

If you have any questions, comments, or concerns, please feel free to contact me at [Seinuve@gmail.com](mailto:Seinuve@gmail.com).

For any bugs or suggestions please use the issues tab [here](https://github.com/Seinuve/Kudasai/issues).

---------------------------------------------------------------------------------------------------------------------------------------------------
