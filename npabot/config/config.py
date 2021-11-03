from os import getenv

from dixxbot.common.config import required_get_env_str
from dixxbot.db.config import DBConfig
from dixxbot.log.config import LogConfig
from dixxbot.cache.config import CacheConfig

from .cogs_config import CogsConfig


class BotConfig(object):
    def __init__(self):
        self._cache = dict()
        self.db = DBConfig()
        self.log = LogConfig()
        self.cache = CacheConfig()
        self.cogs = CogsConfig()

    @property
    def token(self) -> str:
        prop_name = "token"
        if prop_name not in self._cache:
            self._cache[prop_name] = required_get_env_str(key="TOKEN")
        return self._cache[prop_name]

    @property
    def command_prefix(self) -> str:
        prop_name = "commend_prefix"
        if prop_name not in self._cache:
            self._cache[prop_name] = getenv("COMMAND_PREFIX", "?")
        return self._cache[prop_name]
