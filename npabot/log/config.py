from os import getenv
from typing import Literal, Union, Optional


LOGGING_LEVELS = Literal[0, 10, 20, 30, 40, 50]


def get_logging_level(
    value: Union[str, int], default: LOGGING_LEVELS = 30
) -> LOGGING_LEVELS:
    in_value = value
    if isinstance(value, str):
        in_value = value[0].lower()
    mapping = {
        "n": 0,
        "d": 10,
        "i": 20,
        "w": 30,
        "e": 40,
        "c": 50,
        0: 0,
        10: 10,
        20: 20,
        30: 30,
        40: 40,
        50: 50,
    }
    if in_value in mapping:
        return mapping[in_value]
    return default


class LogConfig(object):
    def __init__(self):
        self._cache = dict()

    @property
    def level(self) -> LOGGING_LEVELS:
        prop_name = "logging_level"
        if prop_name not in self._cache:
            self._cache[prop_name] = get_logging_level(
                getenv("LOGGING_LEVEL"), default=30
            )
        return self._cache[prop_name]

    @property
    def file(self) -> Optional[str]:
        prop_name = "logging_file"
        if prop_name not in self._cache:
            self._cache[prop_name] = getenv("LOGGING_FILE")
        return self._cache[prop_name]

    @property
    def file_log_format(self) -> str:
        prop_name = "file_log_format"
        if prop_name not in self._cache:
            self._cache[prop_name] = getenv(
                "LOGGING_FORMAT", "%(asctime)s:%(levelname)s:%(name)s: %(message)s"
            )
        return self._cache[prop_name]
