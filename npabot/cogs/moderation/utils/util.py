from discord.ext.commands import (
    MissingRequiredArgument,
    MissingPermissions,
    CommandInvokeError,
    MemberNotFound,
    UserNotFound,
)

from .embed import mod_action_embed
from dixxbot.statics import NPA_MOD_LOG_CHANNEL_ID, EMOTE_CHECK_MARK_BUTTON, EMOTE_X


async def mod_log_and_report(self, author, ctx, member, reason):
    channel = self.bot.get_channel(NPA_MOD_LOG_CHANNEL_ID)
    message = ctx.message
    action = ctx.command.name
    await channel.send(embed=mod_action_embed(member, author, reason, message, action))
    await ctx.message.add_reaction(EMOTE_CHECK_MARK_BUTTON)


async def error_handle(ctx, error):
    """The event triggered when an error is raised while invoking a command.
    Parameters
    ------------
    ctx: commands.Context
        The context used for command invocation.
    error: commands.CommandError
        The Exception raised.
    """
    if isinstance(error, MissingRequiredArgument):
        await ctx.send(
            "You forgot a important part of the command, might want to use ?help.",
            delete_after=10.0,
        )
        await ctx.message.add_reaction(EMOTE_X)
    elif isinstance(error, MissingPermissions):
        await ctx.send(
            "You are missing permission(s) to run this command.", delete_after=10.0,
        )
        await ctx.message.add_reaction(EMOTE_X)
    elif isinstance(error, CommandInvokeError):
        await ctx.send(
            "Unable to DM user, attempt to direct message a user that has DMs disabled for non-friends.",
        )
        await ctx.message.add_reaction(EMOTE_X)
    elif isinstance(error, MemberNotFound):
        await ctx.send(
            "The member is not found, ensure proper spelling.", delete_after=10.0,
        )
        await ctx.message.add_reaction(EMOTE_X)
    elif isinstance(error, UserNotFound):
        await ctx.send(
            "The user is not found, ensure proper spelling.", delete_after=10.0,
        )
        await ctx.message.add_reaction(EMOTE_X)
    else:
        await ctx.message.add_reaction(EMOTE_X)
        raise error
