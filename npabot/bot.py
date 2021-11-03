from aiomysql.sa import Engine
from aioredis import ConnectionsPool
from discord import Intents
from discord.ext import commands
from loguru import logger

from dixxbot.cache.cache import populate_cache_from_db
from dixxbot.config import BotConfig


class OnlyIncludeGuildChannels(commands.CheckFailure):
    ...


class Bot(commands.Bot):
    def __init__(
        self,
        description: str,
        command_prefix: str,
        db: Engine,
        cache: ConnectionsPool,
        config: BotConfig,
    ):
        intents = Intents.default()
        intents.members = True
        intents.messages = True
        intents.bans = True
        super().__init__(
            description=description,
            command_prefix=command_prefix,
            intents=intents,
            case_insensitive=True,
        )
        self.bot_config_object = config
        self.db = db
        self.cog_id = "0"
        self.aio_cache = cache

    async def on_ready(self):
        logger.info(f"Username: {self.user}\nID: {self.user.id}")
        await populate_cache_from_db(cache=self.aio_cache, db=self.db)
