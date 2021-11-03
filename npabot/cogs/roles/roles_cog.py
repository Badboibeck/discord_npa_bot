import discord
from discord.ext.commands import (
    Bot,
    group,
)

from ..base import BaseCog
from dixxbot.cogs.common.invalid_command_text import invalid_command_text
from ..common.has_x import async_has_role_by_id
from .utils.util import error_handle
from .utils.roles_mapping import roles_add_remove
from dixxbot.statics import (
    EMOTE_CHECK_MARK_BUTTON,
    EMOTE_X,
)


class Roles(BaseCog):
    """Deals with:
    Add and Remove Roles
    """

    cog_id: int = 14

    def __init__(self, bot: Bot):
        super().__init__(bot, self.cog_id)

    # +------------------------------------------------------------+
    # |                           Roles                            |
    # +------------------------------------------------------------+

    @group(name="role", pass_context=True, invoke_without_command=True)
    async def role(self, ctx):
        """
        Gives or Takes members role.
        """
        await ctx.send(invalid_command_text("role"), delete_after=10.0)

    @role.command(name="add")
    async def give_role(self, ctx, role: discord.Role, member: discord.Member):
        """
        Gives the member role.
        """

        author = ctx.author
        role_id = role.id
        if role_id not in roles_add_remove:
            await ctx.send(f"This {role} is not supported.", delete_after=10.0)
            await ctx.message.add_reaction(EMOTE_X)
            return

        if await async_has_role_by_id(
            member=author, role_id=roles_add_remove[role_id],
        ):
            await member.add_roles(
                ctx.guild.get_role(role_id),
                reason=f"{ctx.author} has added the {role} role to {member}.",
            )
            await ctx.message.add_reaction(EMOTE_CHECK_MARK_BUTTON)
            return
        await ctx.send(f"Sorry you are not allowed to add {role}.", delete_after=10.0)
        await ctx.message.add_reaction(EMOTE_X)

    @role.command(name="remove")
    async def take_role(self, ctx, role: discord.Role, member: discord.Member):
        """
        Takes a members role.
        """

        author = ctx.author
        role_id = role.id
        if role_id not in roles_add_remove:
            await ctx.send(f"This {role} is not supported.", delete_after=10.0)
            await ctx.message.add_reaction(EMOTE_X)
            return

        if await async_has_role_by_id(
            member=author, role_id=roles_add_remove[role_id],
        ):
            await member.remove_roles(
                ctx.guild.get_role(role_id),
                reason=f"{ctx.author} has removed the {role} role from {member}.",
            )
            await ctx.message.add_reaction(EMOTE_CHECK_MARK_BUTTON)
            return
        await ctx.send(f"Sorry you are not allowed to add {role}.", delete_after=10.0)
        await ctx.message.add_reaction(EMOTE_X)

    # +------------------------------------------------------------+
    # |                     ERROR HANDLERS                         |
    # +------------------------------------------------------------+

    @give_role.error
    async def give_role_handler(self, ctx, error):
        await error_handle(ctx, error)

    @take_role.error
    async def take_role_handler(self, ctx, error):
        await error_handle(ctx, error)
