from dixxbot.errors import DIXXBotException


class InvalidTagNameException(DIXXBotException):
    ...


class TagNameInUseException(DIXXBotException):
    ...


class NickNameTooLongException(DIXXBotException):
    ...
