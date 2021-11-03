import io
from typing import Union, List, Optional, Dict

from discord import (
    Message,
    Member,
    VoiceChannel,
    TextChannel,
    CategoryChannel,
    Role,
    AllowedMentions,
    Guild,
    Emoji,
    PartialEmoji,
    File,
)

import discord

from discord.ext.commands import Bot, Context, group

from ..base import BaseCog
from dixxbot import statics
from dixxbot.cache.cache import populate_cache_from_db
from dixxbot.cogs.common.has_x import has_role_by_id
from dixxbot.cogs.common.emoji_utils import UnifiedEmoji, get_emoji_from_id
from dixxbot.cogs.common.aiters import aiter_members, aiter_roles
from dixxbot.cogs.common.in_memory_file import write_dict_as_csv
from .utils import to_string


class Utils(BaseCog):
    """Utilities for things."""

    cog_id: int = 2

    def __init__(self, bot: Bot):
        super().__init__(bot, self.cog_id)

    @group(pass_context=True, invoke_without_command=True, case_insensitive=True)
    async def utils(self, ctx: Context):
        await ctx.send(self.invalid_command_text("utils"), delete_after=10.0)

    @utils.command()
    async def ping(self, ctx: Context):
        """
        Get Bot Latency.
        """

        latency = self.bot.latency
        await ctx.send(latency)

    @utils.command(name="reload_config")
    async def reloadConfig(self, ctx: Context):
        """
        Reload the configuration.
        """
        # TODO (ibigpapa): Change to use a table instead of static mapping issue #9.
        if has_role_by_id(
            member=ctx.author, role_id=[statics.DIXX_DEVS_ROLE_ID, statics.GOAT_ROLE_ID]
        ):  # [DIXX DEVS, GOAT]
            await populate_cache_from_db(cache=self.bot.aio_cache, db=self.bot.db)
            await ctx.send("Configuration reloaded")
        else:
            await ctx.send("You are unauthorized to use this command")

    @utils.group(pass_context=True, invoke_without_command=True, case_insensitive=True)
    async def get(self, ctx: Context):
        await ctx.send(self.invalid_command_text("utils get"), delete_after=10.0)

    @get.group(
        name="id", pass_context=True, invoke_without_command=True, case_insensitive=True
    )
    async def get_id(self, ctx: Context):
        await ctx.send(self.invalid_command_text("utils get id"), delete_after=10.0)

    @get_id.command(name="text_channel")
    async def get_id_text_channel(self, ctx: Context, channel: TextChannel):
        """
        Get A text channel id.
        """
        await ctx.send(f"{channel.mention}: {channel.id}")

    @get_id.command(name="message")
    async def get_message_id(self, ctx: Context, msg: Message):
        """
        Get message id.
        """
        await ctx.send(msg.id)

    @get_id.command(name="member")
    async def get_member_id(self, ctx: Context, member: Member):
        """
        Get member id.

        EX:
        `utils get id member @person`
        `utils get id member person`
        `utils get id member "person with space(s)"`
        """
        await ctx.send(f"{member.display_name}: {member.id}")

    @get_id.command(name="voice_channel")
    async def get_id_voice_channel(self, ctx: Context, channel: VoiceChannel):
        """
        Get Voice Channel id.
        """
        await ctx.send(f"{channel.mention}: {channel.id}")

    @get_id.command(name="category")
    async def get_id_category(self, ctx: Context, category: CategoryChannel):
        """
        Get Category id.
        """
        await ctx.send(f"{category.mention}: {category.id}")

    @get_id.command(name="reactions")
    async def get_id_reactions(self, ctx: Context, msg: Message):
        """
        Get emoji Ids from reactions on a message.
        """
        # TODO: FIX BUGS #21
        emojis = list()
        for reaction in msg.reactions:
            emojis.append(f"{UnifiedEmoji(emoji=reaction.emoji)}")
        await ctx.send("\n".join(emojis))

    @get_id.command(name="role")
    async def get_id_role(self, ctx: Context, role: Role):
        """
        Get Role Id
        """
        await ctx.send(f"{role.name}: {role.id}")

    @get.group(
        name="members",
        pass_context=True,
        invoke_without_command=True,
        case_insensitive=True,
    )
    async def get_member(self, ctx: Context):
        await ctx.send(
            self.invalid_command_text("utils get members"), delete_after=10.0
        )

    @get_member.group(name="from", pass_context=True, invoke_without_command=True)
    async def get_member_from(self, ctx: Context):
        await ctx.send(
            self.invalid_command_text("utils get members from"), delete_after=10.0
        )

    @get_member_from.command(name="role")
    async def get_member_from_role(self, ctx: Context, role: Role):
        """
        Get Members in Role.
        """
        member_pages = [""]
        for member in [f"\n{member}" for member in role.members]:
            mem_size = len(member)
            if mem_size + len(member_pages[-1]) < 1800:
                member_pages[-1] += member
                continue
            member_pages.append(member)
        for idx, member_page in enumerate(member_pages):
            await ctx.send(
                f"\n**Members of {role} (page {idx + 1} of {len(member_pages)})**\n{member_page}\n "
            )

    @get_member_from.command(name="roles")
    async def get_member_from_role(self, ctx: Context, *roles: Role):
        """
        Get Members from a space separated list of roles.  Outputs a file due to likely size over 2000 characters.
        """
        role_mappings: List[Dict] = list()
        total_roles = len(roles)
        processed_roles = 0
        async for role in aiter_roles(roles):
            processed_roles += 1
            total_members_for_role: int = len(role.members)
            processed_members_for_role: int = 0
            await ctx.send(
                f"Processing role {role} ({processed_roles} of {total_roles} roles): {processed_members_for_role} of {total_members_for_role} members.",
                delete_after=10.0,
            )
            async for member in aiter_members(role.members):
                role_mappings.append(
                    {
                        "role_id": role.id,
                        "role": role.name,
                        "member_id": member.id,
                        "member": f"{member}",
                    }
                )
                processed_members_for_role += 1
                if processed_members_for_role % 1000 == 0:
                    await ctx.send(
                        f"Processing role {role} ({processed_roles} of {total_roles} roles): {processed_members_for_role} of {total_members_for_role} members.",
                        delete_after=10.0,
                    )
        file_object = write_dict_as_csv(
            rows=role_mappings, fieldnames=["role_id", "role", "member_id", "member"]
        )
        discord_file = File(file_object, filename="members_of_roles.csv")
        await ctx.send(
            "`get member from roles` done.", file=discord_file,
        )

    """@utils.group(pass_context=True, invoke_without_command=True)
    async def testing(self, ctx: Context):
        await ctx.send(self.invalid_command_text("utils testing"), delete_after=10.0)

    @testing.command(name="mentions")
    async def testing_mentions(
        self, ctx: Context, everyone: bool, users: bool, roles: bool
    ):
        await ctx.send(
            f"{ctx.guild.default_role} <@394361738386210828> <@&633199511317250056>",
            allowed_mentions=AllowedMentions(
                everyone=everyone, users=users, roles=roles
            ),
        )
    """

    @get.group(
        name="emoji",
        pass_context=True,
        invoke_without_command=True,
        case_insensitive=True,
    )
    async def get_emoji(self, ctx: Context):
        await ctx.send(self.invalid_command_text("utils get emoji"), delete_after=10.0)

    @get_emoji.command(name="from_id")
    async def get_emoji_from_id(self, ctx: Context, emoji_id: str):
        emoji = get_emoji_from_id(bot=self.bot, emoji_id=emoji_id)
        if emoji is None:
            await ctx.send(f'Unable to find emoji with id: "{emoji_id}"')
            return
        await ctx.send(f"{emoji}")

    @get.command(name="charinfo")
    async def charinfo(self, ctx, *, characters: str):
        """Shows you information about a number of characters.
        Only up to 25 characters at a time.
        """
        msg = "\n".join(map(to_string, characters))
        if len(msg) > 2000:
            return await ctx.send("Output too long to display.")
        await ctx.send(msg)

    @get.group(
        name="pending_status",
        pass_context=True,
        invoke_without_command=True,
        case_insensitive=True,
    )
    async def get_pending_status(self, ctx: Context):
        await ctx.send(
            self.invalid_command_text("utils get pending"), delete_after=10.0
        )

    @get_pending_status.command(name="user")
    async def get_pending_status_user(self, ctx: Context, member: Member):
        # member.pending is new in 1.6 not available yet.
        if hasattr(member, "pending"):
            await ctx.send(
                content=f"User: {member} Pending status is: {member.pending}",
                allowed_mentions=AllowedMentions.none(),
            )
        else:
            await ctx.send(
                "pending is not implemented on member yet in the discordpy library."
            )

    @utils.group(
        name="jumper",
        pass_context=True,
        invoke_without_command=True,
        case_insensitive=True,
    )
    async def jumper_group(self, ctx: Context):
        await ctx.send(self.invalid_command_text("utils jumper"), delete_after=10.0)

    @jumper_group.command(name="thumper")
    async def jumper_thumper(self, ctx: Context, dryrun: bool = False):
        """
        Jumper thumper will add jumpers to ever member without the role.  It excludes bots.

        Jumper thumper has an optional parameter to only see who would be `thumped`.
        """
        guild: Guild = self.bot.get_guild(statics.DIXXCORD_GUILD_ID)
        members: List[Member] = guild.members
        thumped: List[Member] = list()
        author: Member = ctx.author
        reason = f"Jumper Thumper issued by {author}"
        role_object = discord.Object(statics.JUMPER_ROLE_ID)
        for member in members:
            if member.bot:
                continue
            if (
                not has_role_by_id(member=member, role_id=statics.JUMPER_ROLE_ID)
                and member.pending is not True
            ):
                if not dryrun:
                    await member.add_roles(role_object, reason=reason)
                thumped.append(member)
        if len(thumped) > 0:
            thumped_names = [str(member) for member in thumped]
            thumped_file = File(
                io.StringIO("\n".join(thumped_names)), filename="thumped_users.txt"
            )
            if dryrun:
                await ctx.send(
                    f"Would be Thumped {len(thumped)} members.", file=thumped_file
                )
                return
            await ctx.send(f"Thumped {len(thumped)} members.", file=thumped_file)
            return
        await ctx.send(f"No users to thump")
