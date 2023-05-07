Kudasai.py

Original Author: thevoidzero#4686

Refactored and Maintained by: Seinu#7854

Contributions by: SnOrT NeSqUiK™#9775

Windows only.

Python Version: 3.7.6-3.11.2

Used to make (Japanese - English) translation easier by preprocessing the Japanese text (optional auto translation using deepL/openai API).

Derived from https://github.com/Atreyagaurav/mtl-related-scripts

---------------------------------------------------------------------------------------------------------------------------------------------------

Run the pip commands listed in requirements.txt before running Kudasai.

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

Note:
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
