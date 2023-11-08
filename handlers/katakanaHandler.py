## built-in libraries
from __future__ import annotations ## used for cheating the circular import issue that occurs when i need to type check some things

import string
import typing

## custom modules
if(typing.TYPE_CHECKING): ## used for cheating the circular import issue that occurs when i need to type check some things
    from models.Kairyou import Name

## https://en.wikipedia.org/wiki/Katakana_(Unicode_block)
KATAKANA_CHARSET = {
'゠','ァ','ア','ィ','イ','ゥ','ウ','ェ','エ','ォ','オ','カ','ガ','キ','ギ','ク',
'グ','ケ','ゲ','コ','ゴ','サ','ザ','シ','ジ','ス','ズ','セ','ゼ','ソ','ゾ','タ',
'ダ','チ','ヂ','ッ','ツ','ヅ','テ','デ','ト','ド','ナ','ニ','ヌ','ネ','ノ','ハ',
'バ','パ','ヒ','ビ','ピ','フ','ブ','プ','ヘ','ベ','ペ','ホ','ボ','ポ','マ','ミ',
'ム','メ','モ','ャ','ヤ','ュ','ユ','ョ','ヨ','ラ','リ','ル','レ','ロ','ヮ','ワ',
'ヰ','ヱ','ヲ','ン','ヴ','ヵ','ヶ','ヷ','ヸ','ヹ','ヺ','・','ー','ヽ','ヾ'
}

## Punctuation unicode ranges:
## https://kairozu.github.io/updates/cleaning-jp-text
PUNCTUATION_CHARSET = {
'　','、','。','〃','〄','々','〆','〇','〈','〉','《','》','「','」','『','』',
'【','】','〒','〓','〔','〕','〖','〗','〘','〙','〚','〛','〜','〝','〞','〟',
'〠','〡','〢','〣','〤','〥','〦','〧','〨','〩','〪','〫','〬','〭','〮','〯',
'〰','〱','〲','〳','〴','〵','〶','〷','〸','〹','〺','〻','〼','〽','〾','〿',
'！','＂','＃','＄','％','＆','＇','（','）','＊','＋','，','－','．','／','：',
'；','＜','＝','＞','？','［','＼','］','＾','＿','｀','｛','｜','｝','～','｟',
'｠','｡','｢','｣','､','･','ー','※',' ',' ',' ',' ',
' ',' ',' ',' ',' ',' ',' ',
'​','‌','‍','‎','‏','‐','‑','‒','–','—',
'―','‖','‗','‘','’','‚','‛','“','”','„','‟','†','‡','•','‣','․','‥','…','‧',
' ',' ','‪','‫','‬','‭','‮',
' ','‰','‱','′','″','‴','‵','‶','‷','‸','‹','›','※','‼','‽','‾','‿',
'⁀','⁁','⁂','⁃','⁄','⁅','⁆','⁇','⁈','⁉','⁊','⁋','⁌','⁍','⁎','⁏','⁐','⁑','⁒',
'⁓','⁔','⁕','⁖','⁗','⁘','⁙','⁚','⁛','⁜','⁝','⁞',' ','⁠',
'⁦','⁧','⁨','⁩','«','»','×',"△","▼"
} | set(string.punctuation) ## EN punctuation set

##--------------------start-of-katakanaHandler------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class KatakanaHandler:

    """
    
    Has some helper functions for dealing with katakana characters while preprocessing.

    """
##--------------------start-of-__init__()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, katakana_lib_file:str) -> None:

        """
        
        Parameters:\n
        katakana_lib_file (str) : path to the katakana library file.\n

        Returns:\n
        None.\n

        """

        self.load_katakana_words(katakana_lib_file)

##--------------------start-of-load_katakana_words()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def load_katakana_words(self, katakana_lib_file:str) -> None:

        """

        Loads the katakana library file into memory.\n
        
        Parameters:\n
        self (object - katakanaHandler) : the katakanaHandler object.\n
        katakana_lib_file (str) : path to the katakana library file.\n

        Returns:\n
        None.\n

        """

        self.katakana_words = []

        with open(katakana_lib_file, "r", encoding="utf-8") as file:
            for line in file:
                self.katakana_words.append(line.strip())

##--------------------start-of-is_katakana_only()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def is_katakana_only(self, string:str) -> bool:

        """

        Checks if the string is only katakana.\n
        
        Parameters:\n
        self (object - katakanaHandler) : the katakanaHandler object.\n
        string (str) : the string to check.\n

        Returns:\n
        bool : True if the word is only katakana, False otherwise.\n

        """

        return all([char in KATAKANA_CHARSET for char in string])

##--------------------start-of-get_katakana_entities()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def get_katakana_entities(self, names:dict) -> typing.List[Name]:

        """

        Gets the katakana entities from the names dictionary.\n

        Parameters:\n
        self (object - katakanaHandler) : the katakanaHandler object.\n

        Returns:\n
        list : a list of Name objects.\n

        """

        return [Name(jap=j, eng=e) for e, j in names.items() if self.is_katakana_only(j)]
    
##--------------------start-of-is_actual_word()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def is_actual_word(self, jap:str) -> bool:

        """
        
        Checks if the given jap is an actual katakana word.

        Parameters:\n
        self (object - katakanaHandler) : the katakanaHandler object.
        jap (str) : the katakana word to check.
 
        Returns:
        bool : True if the word is an actual katakana word, False otherwise.

        """

        if(jap in self.katakana_words):
            return True
        
        else:
            return False
        
##--------------------start-of-is_punctuation()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def is_punctuation(self, string):

        """
        
        Checks if the given string is all punctuation.

        Parameters:
        self (object - katakanaHandler) : the katakanaHandler object.
        string (str) : the string to check.

        Returns:
        bool : True if the word is all punc otherwise false

        """

        return all([char in PUNCTUATION_CHARSET for char in string])