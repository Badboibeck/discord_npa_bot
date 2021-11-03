from discord import TextChannel, AllowedMentions, Embed
from discord.ext.commands import Cog, CheckFailure
from loguru import logger

from dixxbot.bot import Bot
from dixxbot.cache.include_channels import is_in_include_channels_cog
from dixxbot.statics import REDS_MOD_SOFTWARE_BOT_ERRORS_CHANNEL_ID


class OnlyIncludeGuildChannelCog(CheckFailure):
    ...


class BaseCog(Cog):
    def __init__(self, bot: Bot, cog_id: int, disable_channel_check: bool = False):
        self.bot = bot
        self.cog_id = cog_id
        self.disable_channel_check = disable_channel_check

    async def cog_check(self, ctx) -> bool:
        if self.disable_channel_check:
            return True
        if await is_in_include_channels_cog(
            cache=self.bot.aio_cache,
            guild_id=ctx.guild.id,
            channel_id=ctx.channel.id,
            cog_id=self.cog_id,
        ):
            return True
        raise OnlyIncludeGuildChannelCog()

    async def cog_command_error(self, ctx, error):
        if isinstance(error, OnlyIncludeGuildChannelCog):
            return
        embed = Embed()
        embed.title = "Uncaught Error"
        embed.add_field(name="channel", value=ctx.channel.mention, inline=True)
        embed.add_field(name="Author", value=ctx.author.mention, inline=True)
        embed.add_field(name="command", value=ctx.command, inline=False)
        embed.add_field(name="error", value=error, inline=False)
        context = (
            f"channel: {ctx.message.channel.mention}, author: {ctx.author.mention}, command: `{ctx.command}`"
            if hasattr(ctx, "command")
            else ""
        )
        msg = f"Uncaught error: `{error}`{context}"
        logger.warning(msg)
        try:
            channel: TextChannel = self.bot.get_channel(
                REDS_MOD_SOFTWARE_BOT_ERRORS_CHANNEL_ID
            )
            await channel.send(embed=embed, allowed_mentions=AllowedMentions.none())
        except Exception:
            pass
        pass

    @staticmethod
    def invalid_command_text(command: str) -> str:
        return f"Invalid **{command}** command passed. See `?help {command}`"
