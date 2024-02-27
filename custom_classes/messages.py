## built-in libraries
import typing

##-------------------start-of-Message--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Message(typing.TypedDict):

    """

    Message is a typedDict that is used to send the message to the OpenAI API.

    """

    role: typing.Literal['system', 'user']
    content: str

##-------------------start-of-SystemTranslationMessage--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class SystemTranslationMessage(Message):

    """

    SystemTranslationMessage is a typedDict that is used to send the system message to the OpenAI API.

    """

    role: typing.Literal['system']
    content: str

##-------------------start-of-ModelTranslationMessage--------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class ModelTranslationMessage(Message):

    """

    ModelTranslationMessage is a typedDict that is used to send the model/user message to the OpenAI API.

    """

    role: typing.Literal['user']
    content: str