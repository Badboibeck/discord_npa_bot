import calendar

from discord import Guild, TextChannel, Message
from discord.ext import tasks
from discord.ext.commands import Cog, group, Context
from loguru import logger

from dixxbot import statics
from dixxbot.bot import Bot
from dixxbot.cogs.common.invalid_command_text import invalid_command_text
from dixxbot.common.date_time import utc_now, date_as_utc
from .member_count import update_member_count
from .coming_going import (
    process_coming_going,
    process_month,
    process_day,
    get_oldest_in_last_24,
    create_embed_oldest_in_last_24,
    process_reactors_day,
    process_reactors_month,
)


class Stats(Cog):
    def __init__(self, bot: Bot, loops_enabled: bool = True):
        self.bot = bot
        self.cog_id = 5
        self.loops_enabled = loops_enabled
        self.ready = False
        self.coming_going_assistant_loop.start()
        if self.loops_enabled:
            self.update_loop.start()
            self.coming_going_loop.start()

    @Cog.listener()
    async def on_ready(self):
        self.ready = True

    @tasks.loop(minutes=5)
    async def update_loop(self):
        if self.ready:
            logger.debug("update member count task loop running.")
            await self.handle_member_count()

    @tasks.loop(minutes=5)
    async def coming_going_loop(self):
        if self.ready:
            guild: Guild = self.bot.get_guild(statics.DIXXCORD_GUILD_ID)
            await process_coming_going(
                guild=guild,
                coming_going_channel_id=statics.COMMUNITY_COMING_GOING_CHANNEL_ID,
                report_channel_id=statics.POWER_PLAYERS_TRYHARDS_CHANNEL_ID,
                cache=self.bot.aio_cache,
            )

    @tasks.loop(minutes=10)
    async def coming_going_assistant_loop(self):
        if self.ready:
            await self._update_assistant_embed(coming=True)
            await self._update_assistant_embed(coming=False)

    async def handle_member_count(self):
        logger.info("Updating member count")
        guild: Guild = self.bot.get_guild(statics.DIXXCORD_GUILD_ID)
        await update_member_count(guild=guild)

    @group(pass_context=True, invoke_without_command=True, case_insensitive=True)
    async def stats(self, ctx: Context):
        await ctx.send(invalid_command_text("stats"), delete_after=10.0)

    @stats.group(
        pass_context=True,
        invoke_without_command=True,
        name="coming-going",
        case_insensitive=True,
    )
    async def coming_going(self, ctx: Context):
        await ctx.send(invalid_command_text("stats coming-going"), delete_after=10.0)

    @stats.group(
        pass_context=True,
        invoke_without_command=True,
        name="assistant",
        case_insensitive=True,
    )
    async def assistant(self, ctx: Context):
        await ctx.send(invalid_command_text("stats assistant"), delete_after=10.0)

    @assistant.group(
        pass_context=True,
        invoke_without_command=True,
        name="update",
        case_insensitive=True,
    )
    async def assistant_update(self, ctx: Context):
        await ctx.send(
            invalid_command_text("stats assistant update"), delete_after=10.0
        )

    @coming_going.command()
    async def monthly(self, ctx: Context, month: int, year: int):
        """
        Gets the monthly report for a specific month
        """
        if ctx.channel.id != statics.REDS_SOFTWARE_TEST_CHANNEL_ID:
            return
        if not 0 < month < 13:
            await ctx.send(
                f"Invalid month {month} provided. Please use a month in range of 1-12",
                delete_after=10.0,
            )
            return
        if not 999 < year < 10000:
            await ctx.send(
                f"Invalid year {year} provided. Please use a year in range of 1000-9999",
                delete_after=10.0,
            )
            return

        now = utc_now()
        requested_date = date_as_utc(year=year, month=month)

        if requested_date > now:
            await ctx.send(
                f"I attempted to predict the future, but a sneaky slithery snake slipped in.",
                delete_after=10.0,
            )
            return

        embed = await process_month(
            guild=ctx.guild,
            channel_id=statics.COMMUNITY_COMING_GOING_CHANNEL_ID,
            month=month,
            year=year,
        )

        await ctx.send(embed=embed)

    @coming_going.group(
        pass_context=True,
        invoke_without_command=True,
        name="reactors",
        case_insensitive=True,
    )
    async def reactors(self, ctx: Context):
        await ctx.send(
            invalid_command_text("stats coming-going reactors"), delete_after=10.0
        )

    @reactors.command(name="monthly")
    async def reactors_monthly(self, ctx: Context, month: int, year: int):
        """
            Gets the monthly reacting counts for a specific month
        """
        if ctx.channel.id != statics.REDS_SOFTWARE_TEST_CHANNEL_ID:
            return
        if not 0 < month < 13:
            await ctx.send(
                f"Invalid month {month} provided. Please use a month in range of 1-12",
                delete_after=10.0,
            )
            return
        if not 999 < year < 10000:
            await ctx.send(
                f"Invalid year {year} provided. Please use a year in range of 1000-9999",
                delete_after=10.0,
            )
            return

        now = utc_now()
        requested_date = date_as_utc(year=year, month=month)

        if requested_date > now:
            await ctx.send(
                f"I attempted to predict the future, but a sneaky slithery snake slipped in.",
                delete_after=10.0,
            )
            return

        embed = await process_reactors_month(
            guild=ctx.guild,
            channel_id=statics.COMMUNITY_COMING_GOING_CHANNEL_ID,
            month=month,
            year=year,
        )

        await ctx.send(embed=embed)

    @reactors.command(name="daily")
    async def reactors_daily(self, ctx: Context, day: int, month: int, year: int):
        """
            Gets the monthly report for a specific month
        """
        if ctx.channel.id != statics.REDS_SOFTWARE_TEST_CHANNEL_ID:
            return
        if not 0 < month < 13:
            await ctx.send(
                f"Invalid month {month} provided. Please use a month in range of 1-12",
                delete_after=10.0,
            )
            return
        if not 999 < year < 10000:
            await ctx.send(
                f"Invalid year {year} provided. Please use a year in range of 1000-9999",
                delete_after=10.0,
            )
            return

        _, days_in_month = calendar.monthrange(month=month, year=year)
        outside_month = days_in_month + 1
        if not 0 < day < outside_month:
            await ctx.send(
                f"Invalid day {day} provided for the month of {month:02d}/{year}. Please use a day in range of 1 to {days_in_month}",
                delete_after=10.0,
            )
            return

        now = utc_now()
        requested_date = date_as_utc(year=year, month=month, day=day)

        if requested_date > now:
            await ctx.send(
                f"I attempted to predict the future, but a sneaky slithery snake slipped in.",
                delete_after=10.0,
            )
            return

        embed = await process_reactors_day(
            guild=ctx.guild,
            channel_id=statics.COMMUNITY_COMING_GOING_CHANNEL_ID,
            day=day,
            month=month,
            year=year,
        )

        await ctx.send(embed=embed)

    @coming_going.command()
    async def daily(self, ctx: Context, day: int, month: int, year: int):
        """
        Gets the monthly report for a specific month
        """
        if ctx.channel.id != statics.REDS_SOFTWARE_TEST_CHANNEL_ID:
            return
        if not 0 < month < 13:
            await ctx.send(
                f"Invalid month {month} provided. Please use a month in range of 1-12",
                delete_after=10.0,
            )
            return
        if not 999 < year < 10000:
            await ctx.send(
                f"Invalid year {year} provided. Please use a year in range of 1000-9999",
                delete_after=10.0,
            )
            return

        _, days_in_month = calendar.monthrange(month=month, year=year)
        outside_month = days_in_month + 1
        if not 0 < day < outside_month:
            await ctx.send(
                f"Invalid day {day} provided for the month of {month:02d}/{year}. Please use a day in range of 1 to {days_in_month}",
                delete_after=10.0,
            )
            return

        now = utc_now()
        requested_date = date_as_utc(year=year, month=month, day=day)

        if requested_date > now:
            await ctx.send(
                f"I attempted to predict the future, but a sneaky slithery snake slipped in.",
                delete_after=10.0,
            )
            return

        embed = await process_day(
            guild=ctx.guild,
            channel_id=statics.COMMUNITY_COMING_GOING_CHANNEL_ID,
            day=day,
            month=month,
            year=year,
        )

        await ctx.send(embed=embed)

    async def _update_assistant_embed(self, coming: bool):
        guild: Guild = self.bot.get_guild(statics.DIXXCORD_GUILD_ID)
        channel: TextChannel = guild.get_channel(
            channel_id=statics.POWER_PLAYERS_TRYHARD_ASSISTANT_CHANNEL_ID
        )
        coming_embed = 797125248474153021
        going_embed = 797125283014377512
        message: Message = await channel.fetch_message(
            id=coming_embed if coming else going_embed
        )
        limit: int = 10
        entries = await get_oldest_in_last_24(
            guild=guild,
            channel_id=statics.COMMUNITY_COMING_GOING_CHANNEL_ID,
            coming=coming,
            limit=limit,
        )
        embed = create_embed_oldest_in_last_24(
            entries=entries, coming=coming, limit=limit
        )
        await message.edit(embed=embed)

    @assistant_update.command(name="coming")
    async def stats_assistant_update_coming(self, ctx: Context):
        await self._update_assistant_embed(coming=True)

    @assistant_update.command(name="going")
    async def stats_assistant_update_going(self, ctx: Context):
        await self._update_assistant_embed(coming=False)
