## built-in libraries
import typing

##-------------------start-of-SystemTranslationMessage--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class SystemTranslationMessage(typing.TypedDict):

    """

    SystemTranslationMessage is a typedDict that is used to send the system message to the API.

    """

    role: typing.Literal['system']
    content: str

##-------------------start-of-ModelTranslationMessage--------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class ModelTranslationMessage(typing.TypedDict):

    """

    ModelTranslationMessage is a typedDict that is used to send the model/user message to the API.

    """

    role: typing.Literal['user']
    content: str