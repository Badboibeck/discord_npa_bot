from os import getenv
from pathlib import Path
from typing import Optional, Type, TypeVar

from dixxbot.config.errors import (
    BaseConfigException,
    MissingConfigException,
    IntConfigException,
    EnumConfigException,
    BooleanParseConfigException,
)


T = TypeVar("T")


def required_get_env_str(key: str) -> str:
    value = getenv(key)
    if value is None:
        raise MissingConfigException(key=key)
    return value


def get_env_int(key: str, default: Optional[int] = None) -> Optional[int]:
    try:
        return int(getenv(key, default))
    except ValueError:
        raise IntConfigException(key=key)


def required_get_env_int(key: str) -> int:
    value = get_env_int(key=key)
    if value is None:
        raise MissingConfigException(key=key)
    return value


def get_env_enum(key: str, enum: Type[T], default: str = None) -> Optional[T]:
    value = getenv(key, default)
    if value is None:
        return None
    try:
        return enum[value]
    except KeyError:
        raise EnumConfigException(key=key, enum=enum)


def required_get_env_enum(key: str, enum: Type[T]) -> T:
    value = get_env_enum(key=key, enum=enum)
    if value is None:
        raise MissingConfigException(key=key)
    return value


def get_env_directory(key: str, default: str = None) -> Optional[Path]:
    value = getenv(key, default)
    try:
        path = Path(value)
        if not path.is_dir():
            raise BaseConfigException(
                f"Given path `{value}` is not a directory or does not exist."
            )
        return path.absolute()
    except TypeError:
        return None


def get_env_bool(key: str, default: bool = None) -> Optional[bool]:
    value = getenv(key, default)
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, str):
        if not len(value) > 0:
            return default
        normalized_value = value.lower()[0]
        if normalized_value in ["t", "1"]:
            return True
        if normalized_value in ["f", "0"]:
            return False
    raise BooleanParseConfigException(key=key)


def required_get_env_bool(key: str) -> bool:
    try:
        value = get_env_bool(key=key)
        if value is None:
            raise MissingConfigException(key=key)
        return value
    except BooleanParseConfigException:
        raise
