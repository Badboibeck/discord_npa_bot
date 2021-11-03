from typing import NamedTuple

from discord import (
    utils,
    Forbidden,
    TextChannel,
    Member,
    Guild,
    Role,
    RawReactionActionEvent,
)
from discord.ext.commands import Bot
from loguru import logger


class AddRemoveRoleGets(NamedTuple):
    guild: Guild
    member: Member
    role: Role
    channel: TextChannel


def add_remove_roles_gets(
    bot: Bot, payload: RawReactionActionEvent, role_id: str
) -> AddRemoveRoleGets:
    rid = int(role_id.strip())
    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    role = utils.get(guild.roles, id=rid)
    channel = bot.get_channel(payload.channel_id)
    return AddRemoveRoleGets(guild, member, role, channel)


async def add_role(bot: Bot, payload: RawReactionActionEvent, role_id: str):
    if payload.user_id != bot.user.id:
        gets = add_remove_roles_gets(bot=bot, payload=payload, role_id=role_id)
        try:
            await gets.member.add_roles(gets.role)
        except Forbidden:
            logger.warning(
                f"Attempted to add role <{gets.role.name}:{role_id}> to <{gets.member.mention}> but do not"
                f" have permissions.  Ensure my role is hierarchically higher than the role that was"
                f" attempted to be assigned.  Also ensure Manage Roles permission has been given to the bot."
            )


async def remove_role(bot: Bot, payload: RawReactionActionEvent, role_id: str):
    if payload.user_id != bot.user.id:
        gets = add_remove_roles_gets(bot=bot, payload=payload, role_id=role_id)
        try:
            await gets.member.remove_roles(gets.role)
        except Forbidden:
            logger.warning(
                f"Attempted to remove role <{gets.role.name}:{role_id}> to <{gets.member.mention}> but do not"
                f" have permissions.  Ensure my role is hierarchically higher than the role that was"
                f" attempted to be removed.  Also ensure Manage Roles permission has been given to the bot."
            )
