import re
from typing import Union, List, Tuple

from discord import Member, User, Guild, Forbidden, HTTPException
from discord.ext.commands import Bot, Context, group
from loguru import logger

from .exception import (
    InvalidTagNameException,
    TagNameInUseException,
    NickNameTooLongException,
)
from ..base import BaseCog
from ..common.aiters import aiter_members
from ..common.has_x import async_has_role_by_id
from dixxbot.statics import (
    NICK_NAME_VARIANTS,
    NICK_NAME_VARIANTS_RE,
    OLD_NICK_NAME_VARIANTS_RE,
    REDS_ROLE_ID,
    EMOTE_CHECK_MARK_BUTTON,
)


UserOrMember = Union[Member, User]


def always_member(person: UserOrMember, guild: Guild) -> Member:
    if isinstance(person, Member):
        return person
    return guild.get_member(person.id)


def nick_name_variants_help() -> str:
    return "\n".join(NICK_NAME_VARIANTS)


def variants_in_name(name: str, regexes: List[re.Pattern]) -> bool:
    for reg in regexes:
        match = reg.search(name)
        if match:
            return True
    return False


def remove_variants_in_name(name: str, regexes: List[re.Pattern]) -> str:
    tmp_name = name
    for reg in regexes:
        tmp_name = reg.sub("", tmp_name)
    return tmp_name.strip()


def nick_add_general(tag_variant: str, display_name: str) -> str:

    if variants_in_name(name=display_name, regexes=NICK_NAME_VARIANTS_RE):
        raise TagNameInUseException()

    adjusted_nick = remove_variants_in_name(
        name=display_name, regexes=OLD_NICK_NAME_VARIANTS_RE
    )
    new_nick = f"{adjusted_nick} [{tag_variant}]"
    if len(new_nick) > 32:
        raise NickNameTooLongException()
    return new_nick


class NickNameTag(BaseCog):
    """
    Enforces unified nickname tags
    """

    cog_id: int = 8

    def __init__(self, bot: Bot):
        super().__init__(bot=bot, cog_id=self.cog_id)

    @group(pass_context=True, invoke_without_command=True, case_insensitive=True)
    async def nick(self, ctx: Context):
        """
        Gives or Removes the tag variant to user in discord.
        """
        await ctx.send(self.invalid_command_text("nick"), delete_after=10.0)

    @nick.command(name="add")
    async def nick_add(self, ctx: Context, tag_variant: str):
        """
        Adds the tag variant to user in discord.
        """
        tag = tag_variant.strip().upper()
        if tag not in NICK_NAME_VARIANTS:
            await ctx.send(
                f"Invalid tag variant.  Please use one of the following:\n{nick_name_variants_help()}"
            )
            return

        member = always_member(person=ctx.author, guild=ctx.guild)
        if member is None:
            return

        if variants_in_name(name=member.display_name, regexes=NICK_NAME_VARIANTS_RE):
            await ctx.send(f"User already has a variant in their name.")
            return

        adjusted_nick = remove_variants_in_name(
            name=member.display_name, regexes=OLD_NICK_NAME_VARIANTS_RE
        )

        new_nick = f"{adjusted_nick} [{tag}]"
        if len(new_nick) > 32:
            await ctx.send(
                f"Unable to add variant as the nickname has a length limit of 32 characters."
            )
            return
        try:
            await member.edit(nick=new_nick, reason="User requested nick tag")
            await ctx.message.add_reaction(EMOTE_CHECK_MARK_BUTTON)
        except Forbidden:
            await ctx.send("Unable to adjust nickname due to permissions.")
        except HTTPException:
            await ctx.send("Unable to adjust nickname due to http error.")
        except Exception as e:
            logger.exception("Unknown exception on nick name cog", e)

    @nick.command(name="remove")
    async def nick_remove(self, ctx: Context):
        """
        Removes any nick name for user
        """
        member = always_member(person=ctx.author, guild=ctx.guild)
        if member is None:
            return
        try:
            await member.edit(nick=None, reason="User requested nick removal")
            await ctx.message.add_reaction(EMOTE_CHECK_MARK_BUTTON)
        except Forbidden:
            await ctx.send("Unable to adjust nickname due to permissions.")
        except HTTPException:
            await ctx.send("Unable to adjust nickname due to http error.")
        except Exception as e:
            logger.exception("Unknown exception on nick name cog", e)

    @nick.group(pass_context=True, invoke_without_command=True, case_insensitive=True)
    async def admin(self, ctx: Context):
        """
        Gives or Removes the tag variant to users in discord. Must have the RED Role.
        """
        await ctx.send(self.invalid_command_text("nick admin"), delete_after=10.0)

    @admin.command(name="add")
    async def nick_admin_add(self, ctx: Context, tag_variant: str, *members: Member):
        """
        Adds the tag variant to users in discord. Must have the RED Role.
        """
        author = always_member(person=ctx.author, guild=ctx.guild)
        if author is None:
            return
        if not await async_has_role_by_id(member=author, role_id=REDS_ROLE_ID):
            await ctx.send("Not authorized.", delete_after=10.0)
            return
        tag = tag_variant.strip().upper()
        if tag not in NICK_NAME_VARIANTS:
            await ctx.send(
                f"Invalid tag variant.  Please use one of the following:\n{nick_name_variants_help()}"
            )
            return
        total = len(members)
        current = 0
        async for member in aiter_members(members):
            try:
                current += 1
                new_nick = nick_add_general(
                    tag_variant=tag, display_name=member.display_name
                )
                await ctx.send(
                    f"Attempting name change {current} of {total}", delete_after=5.0
                )
                await member.edit(
                    nick=new_nick,
                    reason=f"Admin: {author.display_name} - requested nick tag",
                )
                await ctx.send(f"Completed: {member.display_name}", delete_after=5.0)
            except TagNameInUseException:
                await ctx.send(
                    f"User already has a variant in their name on member: {member.display_name}"
                )
                return
            except NickNameTooLongException:
                await ctx.send(
                    f"Unable to add variant as the nickname has a length limit of 32 characters on member: {member.display_name}"
                )
                return
            except Forbidden:
                await ctx.send(
                    f"Unable to adjust nickname due to permissions on member: {member.display_name}"
                )
            except HTTPException:
                await ctx.send(
                    f"Unable to adjust nickname due to http error on member: {member.display_name}"
                )
            except Exception as e:
                logger.exception(
                    f"Unknown exception on nick name cog on member: {member.display_name}",
                    e,
                )

    @admin.command(name="remove")
    async def nick_admin_remove(self, ctx: Context, *members: Member):
        """
        Removes any nick name for users. Must have the RED Role.
        """
        author = always_member(person=ctx.author, guild=ctx.guild)
        if author is None:
            return
        if not await async_has_role_by_id(member=author, role_id=REDS_ROLE_ID):
            await ctx.send("Not authorized.", delete_after=10.0)
            return
        total = len(members)
        current = 0
        async for member in aiter_members(members):
            try:
                current += 1
                await ctx.send(
                    f"Attempting name change {current} of {total}", delete_after=5.0
                )
                await member.edit(
                    nick=None,
                    reason=f"Admin: {author.display_name} - requested nick removal",
                )
                await ctx.send(f"Completed: {member.display_name}", delete_after=5.0)
            except Forbidden:
                await ctx.send(
                    f"Unable to adjust nickname due to permissions on member: {member.display_name}"
                )
            except HTTPException:
                await ctx.send(
                    f"Unable to adjust nickname due to http error on member: {member.display_name}"
                )
            except Exception as e:
                logger.exception(
                    f"Unknown exception on nick name cog on member: {member.display_name}",
                    e,
                )
