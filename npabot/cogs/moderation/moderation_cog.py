from datetime import datetime
import re

import discord
from discord.ext.commands import (
    Bot,
    Cog,
    group,
)
from ..base import BaseCog
from dixxbot.cogs.common.invalid_command_text import invalid_command_text
from ..common.has_x import async_has_role_by_id
from .utils.embed import (
    whois_user_info,
    help_command_embed,
    help_desk_embed,
    author_help_desk_embed,
)
from .utils.util import mod_log_and_report, error_handle
from dixxbot.statics import (
    DIXX_DEVS_ROLE_ID,
    GOAT_ROLE_ID,
    REDS_ROLE_ID,
    OPERATORS_ROLE_ID,
    NPA_MINI_MOD_ROLE_ID,
    COMMUNITY_COMING_GOING_CHANNEL_ID,
    GENERAL_CHAT_CHANNEL_ID,
    NPA_MOD_ROLE_ID,
    EMOTE_X,
    DIXXCORD_GUILD_ID,
    HELP_DESK_CHANNEL_ID,
    HELP_DESK_LOG_CHANNEL_ID,
    RUST_ADMIN_SUPPORT_REPORT_CHANNEL_ID,
    SQD_ADMIN_SUPPORT_REPORT_CHANNEL_ID,
    HLL_ADMIN_SUPPORT_REPORT_CHANNEL_ID,
    REGS_ROLE_ID,
    BOOSTERS_ROLE_ID,
    PATRONS_ROLE_ID,
    ARTIFICIAL_INTELLIGENCE_ROLE_ID,
)


class Moderation(BaseCog):
    """Deals with all things Moderation:

    Admin Actions,
    Coming and Going Messages
    """

    cog_id: int = 13

    def __init__(self, bot: Bot):
        super().__init__(bot, self.cog_id)

    @Cog.listener()
    async def on_member_join(self, member):
        channel = self.bot.get_channel(COMMUNITY_COMING_GOING_CHANNEL_ID)
        await channel.send(
            f":arrow_up: Please welcome {member.mention} to the Discord. Help give them a warm welcome in <#{GENERAL_CHAT_CHANNEL_ID}>."
        )

    @Cog.listener()
    async def on_member_remove(self, member):
        date_format_joined = "%a, %d %b %Y %H:%M"
        time_in_guild = datetime.utcnow() - member.joined_at
        channel = self.bot.get_channel(COMMUNITY_COMING_GOING_CHANNEL_ID)
        await channel.send(
            f":red_circle: **{member} (ID :: {member.id})** left the Discord. Ask them what we can do to improve.\n**Member Joined on:** {member.joined_at.strftime(date_format_joined)} **Time in Community:** {time_in_guild.days} days"
        )

    @Cog.listener()
    async def on_message(self, message):
        url_regex = re.compile(
            r"(?P<url>https?[:.]?\s?\/\/(?:\s*[^\/\s.]+)+(?:\s*\.\s*[^\/\s.]+)*(?:\s*\/\s*[^\/\s]+)*)"
        )
        url_check = url_regex.search(message.content)
        links_allowed = [
            "https://npa.gg",
            "http://npa.gg",
            "https://tooeasy.gg",
            "http://tooeasy.gg",
            "https://nohalfassers.com",
            "http://nohalfassers.com",
            "https://npa.gg/support",
            "https://www.patreon.com/NPAgg",
        ]
        channels_allowed = [
            HELP_DESK_CHANNEL_ID,
            RUST_ADMIN_SUPPORT_REPORT_CHANNEL_ID,
            SQD_ADMIN_SUPPORT_REPORT_CHANNEL_ID,
            HLL_ADMIN_SUPPORT_REPORT_CHANNEL_ID,
        ]
        log_channel = self.bot.get_channel(HELP_DESK_LOG_CHANNEL_ID)

        if message.author == self.bot.user:
            return
        if message.channel is self.bot.get_channel(HELP_DESK_CHANNEL_ID):
            await log_channel.send(embed=help_desk_embed(message))
            try:
                await message.author.send(embed=author_help_desk_embed(message))
            except:
                await log_channel.send("Unable to DM user.")
            finally:
                await message.delete()
        # RETURNS IF NO URLS ARE FOUND IN A MESSAGE
        if url_check is None:
            return
        if (
            message.channel.id not in channels_allowed
            and url_check.group("url") not in links_allowed
        ):
            # MODS URLS POSTED BY JUMPERS THAT IS NOT IN A ALLOWED CHANNEL OR ALLOWED URL
            if not await async_has_role_by_id(
                member=message.author,
                role_id=[
                    REGS_ROLE_ID,
                    BOOSTERS_ROLE_ID,
                    PATRONS_ROLE_ID,
                    ARTIFICIAL_INTELLIGENCE_ROLE_ID,
                ],
            ):
                await message.delete()
                await message.channel.send(
                    f"{message.author.mention} Hey Jumper! Thanks for participating! Unfortunately only REGS and above can post links. \n Visit Level Up in <#806223510010986526> to learn more!",
                    delete_after=300.0,
                )

    @group(name="mod", pass_context=True, invoke_without_command=True)
    async def mod(self, ctx):
        """
        Moderation Cog
        """
        await ctx.send(invalid_command_text("role"), delete_after=10.0)

    # +------------------------------------------------------------+
    # |                    WARNING! WARNING!                       |
    # +------------------------------------------------------------+
    @mod.command(name="warn")
    async def warn(self, ctx, member: discord.Member, reason, *, other_reason=None):
        """Warns a member from the server.

        To use this command you must be a Operator or higher.
        """
        author = ctx.author
        reason_format = reason.lower().strip()
        reason_message = None
        mod_reasons = [
            {
                "reason": ["1", "toxic", "toxicity"],
                "reason_message": "NPA staff members have noted your behavior as toxic. Please refrain from toxicity in NPA.",
            },
            {
                "reason": ["2", "racist", "racism"],
                "reason_message": "Racist behavior is not tolerated at NPA. Please refrain from racism.",
            },
            {
                "reason": ["3", "discrimination", "discrim", "homophobic"],
                "reason_message": "Discriminatory behavior is not tolerated at NPA. Please refrain from discriminatory behavior.",
            },
            {
                "reason": ["4", "nsfw", "obscene"],
                "reason_message": "Obscene, offensive, or NSFW content is restricted. Please be mindful of content posted in the community.",
            },
            {
                "reason": ["5", "cheats"],
                "reason_message": "Sharing, using, or promoting cheats is prohibited. Please be mindful of content posted in the community.",
            },
            {
                "reason": ["6", "politics", "religion"],
                "reason_message": "Any discussion around politics or religion should be kept to DMs. Please be mindful of content posted in the community.",
            },
            {
                "reason": ["7", "promotion"],
                "reason_message": "Do not promote your content without permission from a REDS Staff member first.",
            },
            {
                "reason": ["8", "spam"],
                "reason_message": "Spamming is not tolerated at NPA. Please be mindful of content posted in the community.",
            },
            {
                "reason": ["9", "english"],
                "reason_message": "This is an English only Discord. Thank you.",
            },
            {"reason": ["0", "other"], "reason_message": other_reason},
        ]
        if not await async_has_role_by_id(
            member=author,
            role_id=[
                GOAT_ROLE_ID,
                REDS_ROLE_ID,
                OPERATORS_ROLE_ID,
                NPA_MOD_ROLE_ID,
                NPA_MINI_MOD_ROLE_ID,
            ],
        ):
            await ctx.message.add_reaction(EMOTE_X)
            await ctx.channel.send(
                "You are missing permission(s) to run this command.",
                delete_after=20.0,
            )
            return

        if await async_has_role_by_id(
            member=member,
            role_id=[
                GOAT_ROLE_ID,
                REDS_ROLE_ID,
                OPERATORS_ROLE_ID,
                NPA_MOD_ROLE_ID,
                NPA_MINI_MOD_ROLE_ID,
            ],
        ):
            await ctx.message.add_reaction(EMOTE_X)
            await ctx.channel.send(
                "Unable to use this command on this member. Please inform a Goat if there is a issue.",
                delete_after=20.0,
            )
            return

        for reason_obj in mod_reasons:
            if reason_format in reason_obj["reason"]:
                reason_message = reason_obj["reason_message"]

        if reason_message is None:
            reason_helper = [
                " :: ".join(reason_obj["reason"]) for reason_obj in mod_reasons
            ]
            final_reason_helper = "\n".join(reason_helper)

            await ctx.channel.send(
                f"Reason not found. Please review the options below:```\n{final_reason_helper}\n```",
                delete_after=20.0,
            )
            await ctx.message.add_reaction(EMOTE_X)
            return

        await member.send(reason_message)
        await mod_log_and_report(self, author, ctx, member, reason_message)

    # +------------------------------------------------------------+
    # |                    KICK THEM OUT!                          |
    # +------------------------------------------------------------+
    @mod.command(name="kick")
    async def kick(self, ctx, member: discord.Member, reason, *, other_reason=None):
        """Kicks a member from the server.

        In order for this to work, the bot must have Kick Member permissions.

        To use this command you must be a Operator or higher.
        """
        author = ctx.author
        channel = self.bot.get_channel(COMMUNITY_COMING_GOING_CHANNEL_ID)
        reason_format = reason.lower().strip()
        reason_message = None
        mod_reasons = [
            {
                "reason": ["1", "toxic", "toxicity"],
                "reason_message": "NPA staff members have noted your behavior as toxic. Please refrain from toxicity in NPA. **(Final Warning)**",
            },
            {
                "reason": ["2", "racist", "racism"],
                "reason_message": "NPA staff members have noted your racist behavior. Please refrain from racism. **(Final Warning)**",
            },
            {
                "reason": ["3", "discrimination", "discrim", "homophobic"],
                "reason_message": "NPA staff members have noted your discriminatory behavior. Please refrain from discriminatory behavior. **(Final Warning)**",
            },
            {
                "reason": ["4", "nsfw", "obscene"],
                "reason_message": "NPA staff members have noted your obscene, offensive, or NSFW content. Please be mindful of content posted in the community. **(Final Warning)**",
            },
            {
                "reason": ["5", "cheats"],
                "reason_message": "NPA staff members have noted your sharing, using, or promoting cheats. Please be mindful of content posted in the community. **(Final Warning)**",
            },
            {
                "reason": ["6", "politics", "religion"],
                "reason_message": "NPA staff members have noted your discussion around politics or religion. Please be mindful of content posted in the community. **(Final Warning)**",
            },
            {
                "reason": ["7", "promotion"],
                "reason_message": "NPA staff members have noted the promotion of your content without permission from a REDS Staff member first. **(Final Warning)**",
            },
            {
                "reason": ["8", "spam"],
                "reason_message": "NPA staff members have noted your spamming. Please be mindful of content posted in the community. **(Final Warning)**",
            },
            {
                "reason": ["9", "english"],
                "reason_message": "NPA staff members have noted your constant use of Non-English language in the Discord. This is an English only Discord. Thank you. **(Final Warning)**",
            },
            {
                "reason": ["10", "underage", "young", "kid"],
                "reason_message": "The NPA community is for 18+. Unfortunately, you don't meet that requirement. You're welcome to return when you're 18. **If you return immediately, you will be banned.**",
            },
            {"reason": ["0", "other"], "reason_message": other_reason},
        ]

        if not await async_has_role_by_id(
            member=author,
            role_id=[
                GOAT_ROLE_ID,
                REDS_ROLE_ID,
                OPERATORS_ROLE_ID,
                NPA_MOD_ROLE_ID,
                NPA_MINI_MOD_ROLE_ID,
            ],
        ):
            await ctx.message.add_reaction(EMOTE_X)
            await ctx.channel.send(
                "You are missing permission(s) to run this command.",
                delete_after=20.0,
            )
            return

        if await async_has_role_by_id(
            member=member,
            role_id=[
                GOAT_ROLE_ID,
                REDS_ROLE_ID,
                OPERATORS_ROLE_ID,
                NPA_MOD_ROLE_ID,
                NPA_MINI_MOD_ROLE_ID,
            ],
        ):
            await ctx.message.add_reaction(EMOTE_X)
            await ctx.channel.send(
                "Unable to use this command on this member. Please inform a Goat if there is a issue.",
                delete_after=20.0,
            )
            return

        for reason_obj in mod_reasons:
            if reason_format in reason_obj["reason"]:
                reason_message = reason_obj["reason_message"]

        if reason_message is None:
            reason_helper = [
                " :: ".join(reason_obj["reason"]) for reason_obj in mod_reasons
            ]
            final_reason_helper = "\n".join(reason_helper)

            await ctx.channel.send(
                f"Reason not found. Please review the options below:```\n{final_reason_helper}\n```",
                delete_after=20.0,
            )
            await ctx.message.add_reaction(EMOTE_X)
            return
        try:
            await member.send(reason_message)
        finally:
            await mod_log_and_report(self, author, ctx, member, reason_message)
            await channel.send(
                f"{EMOTE_X} **{member}** was kicked from the community by {author}."
            )
            await ctx.guild.kick(member, reason=reason_message)

    # +------------------------------------------------------------+
    # |             KICK THEM OUT + CLEAN THEM OUT!                |
    # +------------------------------------------------------------+

    @mod.command(name="softban")
    async def softban(self, ctx, member: discord.Member, reason, *, other_reason=None):
        """Soft bans a member from the server.

        A softban is basically banning the member from the server but
        then unbanning the member as well. This allows you to essentially
        kick the member while removing their messages.

        In order for this to work, the bot must have Ban Member permissions.

        To use this command you must be a Operator or higher.
        """
        author = ctx.author
        channel = self.bot.get_channel(COMMUNITY_COMING_GOING_CHANNEL_ID)
        reason_format = reason.lower().strip()
        reason_message = None
        mod_reasons = [
            {
                "reason": ["1", "toxic", "toxicity"],
                "reason_message": "NPA staff members have noted your behavior as toxic. Please refrain from toxicity in NPA. **(Final Warning)**",
            },
            {
                "reason": ["2", "racist", "racism"],
                "reason_message": "NPA staff members have noted your racist behavior. Please refrain from racism. **(Final Warning)**",
            },
            {
                "reason": ["3", "discrimination", "discrim", "homophobic"],
                "reason_message": "NPA staff members have noted your discriminatory behavior. Please refrain from discriminatory behavior. **(Final Warning)**",
            },
            {
                "reason": ["4", "nsfw", "obscene"],
                "reason_message": "NPA staff members have noted your obscene, offensive, or NSFW content. Please be mindful of content posted in the community. **(Final Warning)**",
            },
            {
                "reason": ["5", "cheats"],
                "reason_message": "NPA staff members have noted your sharing, using, or promoting cheats. Please be mindful of content posted in the community. **(Final Warning)**",
            },
            {
                "reason": ["6", "politics", "religion"],
                "reason_message": "NPA staff members have noted your discussion around politics or religion. Please be mindful of content posted in the community. **(Final Warning)**",
            },
            {
                "reason": ["7", "promotion"],
                "reason_message": "NPA staff members have noted the promotion of your content without permission from a REDS Staff member first. **(Final Warning)**",
            },
            {
                "reason": ["8", "spam"],
                "reason_message": "NPA staff members have noted your spamming. Please be mindful of content posted in the community. **(Final Warning)**",
            },
            {
                "reason": ["9", "english"],
                "reason_message": "NPA staff members have noted your constant use of Non-English language in the Discord. This is an English only Discord. Thank you. **(Final Warning)**",
            },
            {
                "reason": ["10", "underage", "young", "kid"],
                "reason_message": "The NPA community is for **18+**. Unfortunately, you don't meet that requirement. You're welcome to return when you're 18. **If you return immediately, you will be banned.**",
            },
            {"reason": ["0", "other"], "reason_message": other_reason},
        ]

        if not await async_has_role_by_id(
            member=author,
            role_id=[
                GOAT_ROLE_ID,
                REDS_ROLE_ID,
                OPERATORS_ROLE_ID,
                NPA_MOD_ROLE_ID,
                NPA_MINI_MOD_ROLE_ID,
            ],
        ):
            await ctx.message.add_reaction(EMOTE_X)
            await ctx.channel.send(
                "You are missing permission(s) to run this command.",
                delete_after=20.0,
            )
            return

        if await async_has_role_by_id(
            member=member,
            role_id=[
                GOAT_ROLE_ID,
                REDS_ROLE_ID,
                OPERATORS_ROLE_ID,
                NPA_MOD_ROLE_ID,
                NPA_MINI_MOD_ROLE_ID,
            ],
        ):
            await ctx.message.add_reaction(EMOTE_X)
            await ctx.channel.send(
                "Unable to use this command on this member. Please inform a Goat if there is a issue.",
                delete_after=20.0,
            )
            return

        for reason_obj in mod_reasons:
            if reason_format in reason_obj["reason"]:
                reason_message = reason_obj["reason_message"]

        if reason_message is None:
            reason_helper = [
                " :: ".join(reason_obj["reason"]) for reason_obj in mod_reasons
            ]
            final_reason_helper = "\n".join(reason_helper)

            await ctx.channel.send(
                f"Reason not found. Please review the options below:```\n{final_reason_helper}\n```",
                delete_after=20.0,
            )
            await ctx.message.add_reaction(EMOTE_X)
            return
        try:
            await member.send(reason_message)
        finally:
            await mod_log_and_report(self, author, ctx, member, reason_message)
            await channel.send(
                f"{EMOTE_X} **{member}** was kicked from the community by {author}."
            )
            await ctx.guild.ban(member, reason=f"Softban for {reason_message}")
            await ctx.guild.unban(member, reason=f"Softban for {reason_message}")

    # +------------------------------------------------------------+
    # |                       BAN HAMMER!                          |
    # +------------------------------------------------------------+

    @mod.command(name="ban")
    async def ban(self, ctx, member: discord.User, reason, *, other_reason=None):
        """Bans a member from the server.

        You can also ban from ID to ban regardless whether they're
        in the server or not.

        In order for this to work, the bot must have Ban Member permissions.

        To use this command you must be a NPA MOD or higher.
        """
        guild = self.bot.get_guild(DIXXCORD_GUILD_ID)
        author = ctx.author
        channel = self.bot.get_channel(COMMUNITY_COMING_GOING_CHANNEL_ID)
        reason_format = reason.lower().strip()
        reason_message = None
        mod_reasons = [
            {
                "reason": ["1", "toxic", "toxicity"],
                "reason_message": "NPA staff members have noted your behavior as toxic. As a result, you are no longer welcome at NPA. Ban appeals are allowed, though rarely successful. You can appeal at https://npa.gg/support.",
            },
            {
                "reason": ["2", "racist", "racism"],
                "reason_message": "NPA staff members have noted your racist behavior. As a result, you are no longer welcome at NPA. Ban appeals are allowed, though rarely successful. You can appeal at https://npa.gg/support.",
            },
            {
                "reason": ["3", "discrimination", "discrim", "homophobic"],
                "reason_message": "NPA staff members have noted your discriminatory behavior. As a result, you are no longer welcome at NPA. Ban appeals are allowed, though rarely successful. You can appeal at https://npa.gg/support.",
            },
            {
                "reason": ["4", "nsfw", "obscene"],
                "reason_message": "NPA staff members have noted your obscene, offensive, or NSFW content. As a result, you are no longer welcome at NPA. Ban appeals are allowed, though rarely successful. You can appeal at https://npa.gg/support.",
            },
            {
                "reason": ["5", "cheats"],
                "reason_message": "NPA staff members have noted your sharing, using, or promoting cheats. As a result, you are no longer welcome at NPA. Ban appeals are allowed, though rarely successful. You can appeal at https://npa.gg/support.",
            },
            {
                "reason": ["6", "politics", "religion"],
                "reason_message": "NPA staff members have noted your discussion around politics or religion. As a result, you are no longer welcome at NPA. Ban appeals are allowed, though rarely successful. You can appeal at https://npa.gg/support.",
            },
            {
                "reason": ["7", "promotion"],
                "reason_message": "NPA staff members have noted the promotion of your content without permission from a REDS Staff member first. As a result, you are no longer welcome at NPA. Ban appeals are allowed, though rarely successful. You can appeal at https://npa.gg/support.",
            },
            {
                "reason": ["8", "spam"],
                "reason_message": "NPA staff members have noted your spamming. Please be mindful of content posted in the community. As a result, you are no longer welcome at NPA. Ban appeals are allowed, though rarely successful. You can appeal at https://npa.gg/support.",
            },
            {
                "reason": ["9", "english"],
                "reason_message": "NPA staff members have noted your constant use of Non-English language in the Discord. As a result, you are no longer welcome at NPA. Ban appeals are allowed, though rarely successful. You can appeal at https://npa.gg/support.",
            },
            {
                "reason": ["10", "underage", "young", "kid"],
                "reason_message": "The NPA community is for **18+**. Ban appeals are allowed, though rarely successful. You can appeal at npa.gg/support.",
            },
            {"reason": ["0", "other"], "reason_message": other_reason},
        ]

        for reason_obj in mod_reasons:
            if reason_format in reason_obj["reason"]:
                reason_message = reason_obj["reason_message"]

        if reason_message is None:
            reason_helper = [
                " :: ".join(reason_obj["reason"]) for reason_obj in mod_reasons
            ]
            final_reason_helper = "\n".join(reason_helper)

            await ctx.channel.send(
                f"Reason not found. Please review the options below:```\n{final_reason_helper}\n```",
                delete_after=20.0,
            )
            await ctx.message.add_reaction(EMOTE_X)
            return
        if not await async_has_role_by_id(
            member=author,
            role_id=[GOAT_ROLE_ID, REDS_ROLE_ID, NPA_MOD_ROLE_ID],
        ):
            await ctx.message.add_reaction(EMOTE_X)
            await ctx.channel.send(
                "You are missing permission(s) to run this command.",
                delete_after=20.0,
            )
            return
        guild_member = guild.get_member(member.id)
        if guild_member is not None:
            if await async_has_role_by_id(
                member=guild_member,
                role_id=[
                    GOAT_ROLE_ID,
                    REDS_ROLE_ID,
                    OPERATORS_ROLE_ID,
                    NPA_MOD_ROLE_ID,
                    NPA_MINI_MOD_ROLE_ID,
                ],
            ):
                await ctx.message.add_reaction(EMOTE_X)
                await ctx.channel.send(
                    "Unable to use this command on this member. Please inform a Goat if there is a issue.",
                    delete_after=20.0,
                )
                return
        try:
            await member.send(reason_message)
        finally:
            await mod_log_and_report(self, author, ctx, member, reason_message)
            await channel.send(
                f":hammer: **{member}** was banned from the community by {author}."
            )
            await ctx.guild.ban(user=member, reason=reason_message)

    # +------------------------------------------------------------+
    # |                    REMOVE A BAN!                           |
    # +------------------------------------------------------------+

    @mod.command(name="unban")
    async def unban(self, ctx, member: discord.User, reason, *, other_reason=None):
        """Unbans a member from the server.

        You must pass the users id in order to use this command.

        Reason and Evidence are not a required input.

        In order for this to work, the bot must have Ban Member permissions.

        To use this command you must be a NPA MOD or higher.
        """
        author = ctx.author
        reason_format = reason.lower().strip()
        reason_message = None
        mod_reasons = [
            {
                "reason": ["1", "appeal"],
                "reason_message": "The member went through the appeal process and is allowed to return to the NPA Discord.",
            },
            {
                "reason": ["2", "time"],
                "reason_message": "The member has been banned for appropriate amount of time and is allowed to return to the NPA Discord.",
            },
            {
                "reason": ["3", "wrongful"],
                "reason_message": "The member was wrongfully banned and is allowed to return to the NPA Discord.",
            },
            {"reason": ["0", "other"], "reason_message": other_reason},
        ]

        if not await async_has_role_by_id(
            member=author,
            role_id=[GOAT_ROLE_ID, REDS_ROLE_ID, NPA_MOD_ROLE_ID],
        ):
            await ctx.message.add_reaction(EMOTE_X)
            await ctx.channel.send(
                "You are missing permission(s) to run this command.",
                delete_after=20.0,
            )
            return

        for reason_obj in mod_reasons:
            if reason_format in reason_obj["reason"]:
                reason_message = reason_obj["reason_message"]

        if reason_message is None:
            reason_helper = [
                " :: ".join(reason_obj["reason"]) for reason_obj in mod_reasons
            ]
            final_reason_helper = "\n".join(reason_helper)

            await ctx.channel.send(
                f"Reason not found. Please review the options below:```\n{final_reason_helper}\n```",
                delete_after=20.0,
            )
            await ctx.message.add_reaction(EMOTE_X)
            return

        await ctx.guild.unban(user=member, reason=reason_message)
        await mod_log_and_report(self, author, ctx, member, reason_message)

    # +------------------------------------------------------------+
    # |                      whois command                         |
    # +------------------------------------------------------------+

    @mod.command(name="whois")
    async def whois(self, ctx, member: discord.Member):
        """Returns information on the member.

        To use this command you must be a Operator or higher.
        """
        author = ctx.author
        if not await async_has_role_by_id(
            member=author,
            role_id=[
                DIXX_DEVS_ROLE_ID,
                GOAT_ROLE_ID,
                REDS_ROLE_ID,
                OPERATORS_ROLE_ID,
                NPA_MOD_ROLE_ID,
                NPA_MINI_MOD_ROLE_ID,
            ],
        ):
            await ctx.send("Not authorized.", delete_after=10.0)
            await ctx.message.add_reaction(EMOTE_X)
            return
        await ctx.send(embed=whois_user_info(member))

    # +------------------------------------------------------------+
    # |                     ERROR HANDLERS                         |
    # +------------------------------------------------------------+
    @warn.error
    async def warn_handler(self, ctx, error):
        await error_handle(ctx, error)

    @kick.error
    async def kick_handler(self, ctx, error):
        await error_handle(ctx, error)

    @softban.error
    async def softban_handler(self, ctx, error):
        await error_handle(ctx, error)

    @ban.error
    async def ban_handler(self, ctx, error):
        await error_handle(ctx, error)

    @unban.error
    async def unban_handler(self, ctx, error):
        await error_handle(ctx, error)

    @whois.error
    async def whois_handler(self, ctx, error):
        await error_handle(ctx, error)

    # +------------------------------------------------------------+
    # |                     HELP COMMAND                           |
    # +------------------------------------------------------------+

    @mod.command(name="help")
    async def help(self, ctx):
        """Returns information on the mod commands.

        To use this command you must be a Operator or higher.
        """
        author = ctx.author
        if not await async_has_role_by_id(
            member=author,
            role_id=[
                DIXX_DEVS_ROLE_ID,
                GOAT_ROLE_ID,
                REDS_ROLE_ID,
                OPERATORS_ROLE_ID,
                NPA_MOD_ROLE_ID,
                NPA_MINI_MOD_ROLE_ID,
            ],
        ):
            await ctx.send("Not authorized.", delete_after=10.0)
            await ctx.message.add_reaction(EMOTE_X)
            return

        await ctx.send(embed=help_command_embed(), delete_after=120.0)
