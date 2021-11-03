from discord import Member, TextChannel
from discord.ext.commands import Cog, Bot

from dixxbot import statics


class RoleChange(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.cog_id = 6

    # TODO: Make Generic
    # Lots of member changes keep loop tight.
    @Cog.listener()
    async def on_member_update(self, before: Member, after: Member):
        before_roles = {role.id for role in before.roles}
        after_roles = {role.id for role in after.roles}
        new_roles = after_roles - before_roles
        if statics.PATRONS_ROLE_ID in new_roles:
            channel: TextChannel = self.bot.get_channel(statics.PATREON_CHAT_CHANNEL_ID)
            await channel.send(
                f"⚡ A new member has joined the ranks!\n⚡ Let's welcome our newest Patron {after.mention}!\n\n<@&{statics.PATREON_BOSS_ROLE_ID}>"
            )
        if statics.BOOSTERS_ROLE_ID in new_roles:
            channel: TextChannel = self.bot.get_channel(statics.GENERAL_CHAT_CHANNEL_ID)
            await channel.send(
                f"⚡ A member has boosted the discord!\n⚡ Let's thank our newest booster {after.mention}."
            )
        if statics.REGS_ROLE_ID in new_roles:
            channel: TextChannel = self.bot.get_channel(
                statics.POWER_PLAYERS_TRYHARDS_CHANNEL_ID
            )
            await channel.send(
                f"⚡ A member has obtained the REGS role\n⚡ Let's greet our newest REG {after.mention} in <#{statics.GENERAL_CHAT_CHANNEL_ID}>"
            )
