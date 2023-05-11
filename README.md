Kudasai

Original Author: thevoidzero#4686

Refactored, Maintained, and Added to by: Seinu#7854

Contributions by: SnOrT NeSqUiK™#9775

Built for Windows, Doesn't use an os specific library, so it should work on other OS's, but it is untested.

Python Version: 3.8-3.11.2

It should work with 3.8, although it is untested. I recommend using 3.9+

Used to make (Japanese - English) translation easier by preprocessing the Japanese text (optional auto translation using deepL/openai API).

Derived from https://github.com/Atreyagaurav/mtl-related-scripts

---------------------------------------------------------------------------------------------------------------------------------------------------

Dependencies:

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

Please note that issues can occur when trying to install these dependencies:

python -m spacy download ja_core_news_lg
python -m spacy download en_core_web_lg

if these do not work, either reinstall spacy or try:

pip install en_core_web_lg
pip install ja_core_news_lg

---------------------------------------------------------------------------------------------------------------------------------------------------

CmdLineArgs

Argument 1: Path to a .txt file that needs to be preprocessed

Argument 2: Path to JSON Criteria

An example of how to run Kudasai.py from cmd:

C:\Users\Tetra\Documents\Repositories\Kudasai\Kudasai.py "C:\Users\Tetra\Desktop\arc 8 chapter 9.txt" "C:\Users\Tetra\Documents\Repositories\Kudasai\Replacements\Rezero Replacements.json"

Where:

C:\Users\Tetra\Documents\Repositories\Kudasai\Kudasai.py is the path to Kudasai.py

C:\users\Tetra\Desktop\arc 8 chapter 9.txt is the path to the .txt file that needs to be preprocessed

C:\Users\Tetra\Documents\Repositories\Kudasai\Replacements\Rezero Replacements.json is the path to the JSON Criteria

---------------------------------------------------------------------------------------------------------------------------------------------------

JSON Criteria

For the json it has to be a specific format, you can see several examples in the 'Replacements' Folder or an outline below

{
  "honorifics": {
    "さん": "san",
    "くん": "kun"
  },

  "single_words": {
    "β": "Beta"
  },

  "unicode": {
    "\u3000": " "
  },

  "phrases": {
    "ケヤキモール" : "Keyaki Mall",
    "高育" : "ANHS"
  },

  "kutouten": {
    "「": "\"",
    "」": "\"",
    "『": "'",
    "』": "'",
    "、": ","

  },

  "name_like": {
    "お兄": ["Onii"],
  },

  "single_names": {
    "Kijima": ["鬼島"],
    "king": ["Wan-sama"]

  },

  "full_names": {
    "Amasawa Ichika": ["天沢","一夏"]
  }

}

---------------------------------------------------------------------------------------------------------------------------------------------------

Output: 

KudasaiOutput (folder created where this script (Kudasai.py) is located)

KudasaiOutput contains:

jeCheck.txt (a txt file for j-e checkers to cross-check sentences that were translated by deepL)

output.txt (a txt file containing Kudasai's output, basically what Kudasai replaced)

preprocessedText.txt (a txt file containing the results of Kudasai's preprocessing)

tlDebug.txt (a txt file containing debug material for the developer)

translatedText.txt (a txt file containing the results of your chosen auto translation module)

errorText.txt (a txt file containing the errors that occurred during auto translation (if any))

---------------------------------------------------------------------------------------------------------------------------------------------------

To use

Step 1: Open CMD

Step 2: Copy the path of Kudasai.py to cmd and type a space.

Step 3: Copy the path of .txt file you want to preprocess to cmd and type a space

Step 4: Copy the path of replacements.json to CMD

Step 5: Press enter

Step 6: Follow internal instructions to use auto-translation

Any questions or bugs, please email Seinuve@gmail.com

---------------------------------------------------------------------------------------------------------------------------------------------------

Security:

api keys are stored locally in the user folder and are obfuscated.

---------------------------------------------------------------------------------------------------------------------------------------------------

Util:

Util folder has a script called Token Counter.py that lets you estimated the number of tokens/cost in a file/string

---------------------------------------------------------------------------------------------------------------------------------------------------

GUI:

GUI.py is a GUI Interface for Kudasai.py, it does not include Kijiku or Kaiseki currently, and is solely for providing a visual interface for preprocessing.

---------------------------------------------------------------------------------------------------------------------------------------------------

Naming Conventions:

Kudasai.py - Main Script (Preprocessing) - ください　- Please
Kijiku.py - openai translation module - 基軸 - Foundation
Kaiseki.py - deepl translation module - 解析 - Parsing

---------------------------------------------------------------------------------------------------------------------------------------------------