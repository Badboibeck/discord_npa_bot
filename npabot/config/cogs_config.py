from os import getenv
from typing import Optional

from loguru import logger

from dixxbot.common.config import get_env_bool

"""
cog enable template:
@property
    def (self):
        prop_name = ""
        if prop_name not in self._cache:
            self._cache[prop_name] = get_env_bool(key="COG_", default=True)
        return self._cache[prop_name]
"""


class CogsConfig(object):
    def __init__(self):
        self._cache = dict()

    @property
    def utils_enabled(self) -> bool:
        prop_name = "utils_enabled"
        if prop_name not in self._cache:
            self._cache[prop_name] = get_env_bool(key="COG_UTILS_ENABLED", default=True)
        return self._cache[prop_name]

    @property
    def reactions_enabled(self) -> bool:
        prop_name = "reactions_enabled"
        if prop_name not in self._cache:
            self._cache[prop_name] = get_env_bool(
                key="COG_REACTIONS_ENABLED", default=True
            )
        return self._cache[prop_name]

    @property
    def embed_enabled(self) -> bool:
        prop_name = "embed_enabled"
        if prop_name not in self._cache:
            self._cache[prop_name] = get_env_bool(key="COG_EMBED_ENABLED", default=True)
        return self._cache[prop_name]

    @property
    def role_change_enabled(self) -> bool:
        prop_name = "role_change_enabled"
        if prop_name not in self._cache:
            self._cache[prop_name] = get_env_bool(
                key="COG_ROLE_CHANGE_ENABLED", default=True
            )
        return self._cache[prop_name]

    @property
    def stats_enabled(self) -> bool:
        prop_name = "stats_enabled"
        if prop_name not in self._cache:
            self._cache[prop_name] = get_env_bool(key="COG_STATS_ENABLED", default=True)
        return self._cache[prop_name]

    @property
    def stats_loops_enabled(self) -> bool:
        prop_name = "stats_loops_enabled"
        if prop_name not in self._cache:
            self._cache[prop_name] = get_env_bool(
                key="COG_STATS_LOOPS_ENABLED", default=True
            )
        return self._cache[prop_name]

    @property
    def hll_enabled(self) -> bool:
        prop_name = "hll_enabled"
        if prop_name not in self._cache:
            self._cache[prop_name] = get_env_bool(key="COG_HLL_ENABLED", default=True)
        if self.hll_api_key is None:
            logger.warning("HLL is not enabled as it is missing the API KEY.")
            return False
        return self._cache[prop_name]

    @property
    def hll_api_key(self) -> Optional[str]:
        prop_name = "hll_api_key"
        if prop_name not in self._cache:
            self._cache[prop_name] = getenv("HLL_API_KEY")
        return self._cache[prop_name]

    @property
    def sqd_enabled(self) -> bool:
        prop_name = "sqd_enabled"
        if prop_name not in self._cache:
            self._cache[prop_name] = get_env_bool(key="COG_SQD_ENABLED", default=True)
        if self.sqd_api_key is None:
            logger.warning("SQD is not enabled as it is missing the API KEY.")
            return False
        return self._cache[prop_name]

    @property
    def sqd_api_key(self) -> Optional[str]:
        prop_name = "sqd_api_key"
        if prop_name not in self._cache:
            self._cache[prop_name] = getenv("SQD_API_KEY")
        return self._cache[prop_name]

    @property
    def nick_name_tag_enabled(self) -> bool:
        prop_name = "nick_name_tag_enabled"
        if prop_name not in self._cache:
            self._cache[prop_name] = get_env_bool(
                key="COG_NICK_NAME_TAG_ENABLED", default=True
            )
        return self._cache[prop_name]

    @property
    def clean_report_enabled(self) -> bool:
        prop_name = "clean_report_enabled"
        if prop_name not in self._cache:
            self._cache[prop_name] = get_env_bool(
                key="COG_CLEAN_REPORT_ENABLED", default=True
            )
        return self._cache[prop_name]

    @property
    def member_screening_enabled(self) -> bool:
        prop_name = "member_screening_enabled"
        if prop_name not in self._cache:
            self._cache[prop_name] = get_env_bool(
                key="MEMBER_SCREENING_ENABLED", default=True
            )
        return self._cache[prop_name]

    @property
    def amazon_enabled(self) -> bool:
        prop_name = "amazon_enabled"
        if prop_name not in self._cache:
            self._cache[prop_name] = get_env_bool(
                key="COG_AMAZON_ENABLED", default=True
            )
        return self._cache[prop_name]

    @property
    def moderation_enabled(self) -> bool:
        prop_name = "moderation_enabled"
        if prop_name not in self._cache:
            self._cache[prop_name] = get_env_bool(
                key="COG_MODERATION_ENABLED", default=True
            )
        return self._cache[prop_name]

    @property
    def roles_enabled(self) -> bool:
        prop_name = "roles_enabled"
        if prop_name not in self._cache:
            self._cache[prop_name] = get_env_bool(key="COG_ROLES_ENABLED", default=True)
        return self._cache[prop_name]
