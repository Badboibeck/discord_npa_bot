from enum import Enum
from typing import Type

from dixxbot.errors import DIXXBotException


class BaseConfigException(DIXXBotException):
    def __init__(self, msg: str = None, **kwargs):
        if kwargs:
            super().__init__(msg.format(**kwargs))
        elif msg is None:
            super().__init__()
        else:
            super().__init__(msg)


class MissingConfigException(BaseConfigException):
    def __init__(self, key: str):
        msg = "Missing configuration for {key}"
        super().__init__(msg=msg, key=key)


class IntConfigException(BaseConfigException):
    def __init__(self, key: str):
        msg = "{key} must be an integer"
        super().__init__(msg=msg, key=key)


class EnumConfigException(BaseConfigException):
    def __init__(self, key: str, enum: Type[Enum]):
        msg = "{key} must be one of ({options})"
        enum_names = [e.name for e in enum]
        options = ", ".join(enum_names)
        super().__init__(msg=msg, key=key, options=options)


class BooleanParseConfigException(BaseConfigException):
    def __init__(self, key: str):
        msg = "Unable to parse boolean configuration for {key}"
        super().__init__(msg=msg, key=key)
