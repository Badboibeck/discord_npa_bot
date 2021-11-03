import logging

from aiomysql.sa import create_engine
from aioredis import create_redis_pool
import loguru

from dixxbot.bot import Bot
from dixxbot.config import BotConfig
from dixxbot.cogs import (
    Utils,
    Reactions,
    Embeds,
    RoleChange,
    Stats,
    HellLetLose,
    Squad,
    NickNameTag,
    CleanReports,
    MemberScreening,
    Amazon,
    Moderation,
    Roles,
)
from dixxbot.log.setup import setup_logger


async def run():
    description = "A DIXX to all Bots"
    config = BotConfig()
    engine = await create_engine(
        user=config.db.user,
        db=config.db.db,
        host=config.db.host,
        port=config.db.port,
        password=config.db.password,
    )

    cache = await create_redis_pool(
        config.cache.url,
        password=config.cache.password,
        minsize=config.cache.minsize,
        maxsize=config.cache.maxsize,
    )

    bot = Bot(
        description=description,
        db=engine,
        command_prefix=config.command_prefix,
        cache=cache,
        config=config,
    )
    if config.cogs.utils_enabled:
        bot.add_cog(Utils(bot=bot))
    if config.cogs.reactions_enabled:
        bot.add_cog(Reactions(bot=bot))
    if config.cogs.embed_enabled:
        bot.add_cog(Embeds(bot=bot))
    if config.cogs.role_change_enabled:
        bot.add_cog(RoleChange(bot=bot))
    if config.cogs.stats_enabled:
        bot.add_cog(Stats(bot=bot, loops_enabled=config.cogs.stats_loops_enabled))
    if config.cogs.hll_enabled:
        bot.add_cog(HellLetLose(bot=bot, api_key=config.cogs.hll_api_key))
    if config.cogs.sqd_enabled:
        bot.add_cog(Squad(bot=bot, api_key=config.cogs.sqd_api_key))
    if config.cogs.nick_name_tag_enabled:
        bot.add_cog(NickNameTag(bot=bot))
    if config.cogs.clean_report_enabled:
        bot.add_cog(CleanReports(bot=bot))
    if config.cogs.member_screening_enabled:
        bot.add_cog(MemberScreening(bot=bot))
    if config.cogs.amazon_enabled:
        bot.add_cog(Amazon(bot=bot))
    if config.cogs.moderation_enabled:
        bot.add_cog(Moderation(bot=bot))
    if config.cogs.roles_enabled:
        bot.add_cog(Roles(bot=bot))

    logger = setup_logger(config=config)

    try:
        loguru.logger.info(f"Logging Level: {logging.getLevelName(logger.level)}")
        await bot.start(config.token)
    except KeyboardInterrupt:
        pass
    finally:
        engine.close()
        await engine.wait_closed()
        cache.close()
        await cache.wait_closed()
        await bot.logout()
