from traceback import TracebackException

from discord import Member, TextChannel, Guild, Role
from discord.ext.commands import Cog, Bot

from dixxbot import statics


class MemberScreening(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.cog_id = 11

    @Cog.listener()
    async def on_member_update(self, before: Member, after: Member):
        try:
            if before.pending is True and after.pending is False:
                guild: Guild = self.bot.get_guild(statics.DIXXCORD_GUILD_ID)
                member: Member = guild.get_member(after.id)
                role: Role = guild.get_role(statics.JUMPER_ROLE_ID)
                await member.add_roles(role, reason="Accepted member screening.")
        except Exception as e:
            guild: Guild = self.bot.get_guild(statics.DIXXCORD_GUILD_ID)
            error_channel: TextChannel = guild.get_channel(
                statics.REDS_MOD_SOFTWARE_BOT_ERRORS_CHANNEL_ID
            )
            error = TracebackException.from_exception(e)
            await error_channel.send(
                f"Member Screening Exception\n```python\n{error}\n```"
            )
