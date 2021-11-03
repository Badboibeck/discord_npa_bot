from discord.ext.commands import (
    MissingRequiredArgument,
    MemberNotFound,
    RoleNotFound,
)

from dixxbot.statics import EMOTE_X


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

    elif isinstance(error, RoleNotFound):
        await ctx.send(
            "The bot can not find the role.", delete_after=10.0,
        )
        await ctx.message.add_reaction(EMOTE_X)

    elif isinstance(error, MemberNotFound):
        await ctx.send(
            "The member is not found, ensure proper spelling.", delete_after=10.0,
        )
        await ctx.message.add_reaction(EMOTE_X)

    else:
        await ctx.message.add_reaction(EMOTE_X)
        raise error
