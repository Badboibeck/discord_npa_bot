import calendar
import datetime
import re
from typing import Tuple, NamedTuple, List, Set

from aioredis import ConnectionsPool
from discord import Guild, TextChannel, Embed, Message, Member, Reaction
from loguru import logger

from dixxbot.common.date_time import (
    utc_now,
    MAX_TIMES,
    ZERO_TIMES,
    convert_to_naive,
    us_est_now,
    utc_now_naive,
)
from dixxbot.cache.coming_going import (
    has_daily_run,
    has_monthly_run,
    set_daily,
    set_monthly,
)
from dixxbot import statics
from .coming_going_stats import ComingGoingStats


class CGEntry(NamedTuple):
    name: str
    msg_link: str


COMING_RE = re.compile(r".+\sPlease\swelcome\s.+\sto\sthe\sDiscord.+")
GOING_RE = re.compile(
    r":red_circle:\s\*\*(?P<user>.+#\d{4})\s\(ID\s::\s\d{18}\)\*\*\sleft\sthe\sDiscord\.\sAsk\sthem\swhat\swe\scan\sdo\sto\simprove\."
)


def get_daily_before_after(
    current_date: datetime.datetime,
) -> Tuple[datetime.datetime, datetime.datetime]:
    yesterday = current_date - datetime.timedelta(days=1)
    before = yesterday.replace(**ZERO_TIMES)
    day_before_yesterday = before - datetime.timedelta(days=1, seconds=1)
    after = day_before_yesterday.replace(**MAX_TIMES)
    return convert_to_naive(before), convert_to_naive(after)


def get_last_month_before_after(
    current_date: datetime.datetime,
) -> Tuple[datetime.datetime, datetime.datetime]:
    """returns the previous month's first and last day datetimes respectively"""
    first_day_of_current_month = current_date.replace(day=1)
    before = first_day_of_current_month.replace(**ZERO_TIMES)

    last_day_of_previous_month = first_day_of_current_month - datetime.timedelta(days=1)
    first_day_of_previous_month = last_day_of_previous_month.replace(day=1)
    last_day_of_2nd_previous_month = first_day_of_previous_month - datetime.timedelta(
        days=1
    )
    after = last_day_of_2nd_previous_month.replace(**MAX_TIMES)
    return convert_to_naive(before), convert_to_naive(after)


def get_coming_name(message: Message, match: re.Match) -> str:
    member: Member = message.mentions[0]
    return str(member)


def get_going_name(message: Message, match: re.Match) -> str:
    return match.group("user")


async def get_reaction_names(reactions: List[Reaction]) -> Set[str]:
    names = set()
    for reaction in reactions:
        async for user in reaction.users():
            names.add(f"{user.name}#{user.discriminator}")
    return names


async def get_stats(
    guild: Guild,
    channel_id: int,
    before: datetime.datetime,
    after: datetime.datetime,
    get_reactor_names: bool = False,
) -> ComingGoingStats:
    stats = ComingGoingStats(before=before, after=after)
    channel: TextChannel = guild.get_channel(channel_id=channel_id)
    async for message in channel.history(
        limit=None, before=before, after=after, oldest_first=True
    ):
        coming_match = COMING_RE.match(message.content)
        going_match = GOING_RE.match(message.content)
        has_reactions = len(message.reactions) > 0
        names = None
        if get_reactor_names:
            names = await get_reaction_names(reactions=message.reactions)
        if coming_match:
            stats.add_coming(reacted=has_reactions, names=names)

            continue
        if going_match:
            stats.add_going(reacted=has_reactions, names=names)

    return stats


async def get_oldest_in_last_24(
    guild: Guild, channel_id: int, coming: bool = True, limit: int = 10
) -> List[CGEntry]:
    entries: List[CGEntry] = list()
    channel: TextChannel = guild.get_channel(channel_id=channel_id)
    after = utc_now_naive() - datetime.timedelta(days=1)
    matcher = COMING_RE if coming else GOING_RE
    name_retriever = get_coming_name if coming else get_going_name
    async for message in channel.history(limit=None, after=after, oldest_first=True):
        match = matcher.match(message.content)
        if match and len(message.reactions) < 1:
            name = name_retriever(message=message, match=match)
            entries.append(CGEntry(name=name, msg_link=message.jump_url))
        if len(entries) >= limit:
            break
    return entries


async def process_coming_going(
    guild: Guild,
    coming_going_channel_id: int,
    report_channel_id: int,
    cache: ConnectionsPool,
):
    now = utc_now()
    now_est = us_est_now()
    after_report_time = now_est.hour == 12 or now_est.hour > 12
    daily_has_run = await has_daily_run(cache=cache, day=now.day)
    monthly_has_run = await has_monthly_run(cache=cache, month=now.month)
    report_channel: TextChannel = guild.get_channel(channel_id=report_channel_id)

    if not daily_has_run and after_report_time:
        logger.info("Running Daily Stats")
        before, after = get_daily_before_after(current_date=now)
        stats = await get_stats(
            guild=guild, channel_id=coming_going_channel_id, before=before, after=after
        )
        await report_channel.send(embed=create_daily_embed(stats=stats))
        await set_daily(cache=cache, day=now.day)
    if not monthly_has_run and now.day > 1 and after_report_time:
        logger.info("Running Monthly Stats")
        before, after = get_last_month_before_after(current_date=now)
        stats = await get_stats(
            guild=guild, channel_id=coming_going_channel_id, before=before, after=after
        )
        await report_channel.send(
            content=f"<@&{statics.TRYHARDS_ROLE_ID}>",
            embed=create_monthly_embed(stats=stats),
        )
        await set_monthly(cache=cache, month=now.month)


def create_daily_embed(stats: ComingGoingStats) -> Embed:
    period_date = stats.before - datetime.timedelta(seconds=5)
    period_str = period_date.strftime("%d-%b")
    net_joined = stats.coming - stats.going
    net_joined_positive_sign = "+" if net_joined > 0 else ""
    embed = Embed()
    embed.title = "Daily Tryhard Report"
    embed.description = f"Great Job Tryhards!\n\n**{stats.get_reacted_coming_percentage():.02f}% of {stats.coming} __Joined__ Contacted.**\n**{stats.get_reacted_going_percentage():.02f}% of {stats.going} __Left__ Contacted.\n\nNet Joined:\n```diff\n{net_joined_positive_sign}{net_joined}```**"
    embed.colour = statics.EMBED_DIXX_GOLD
    embed.add_field(name="Reporting Period", value=f"24-hr {period_str}")
    embed.set_footer(text="Our Goal is 100% contact.")
    return embed


def create_daily_reactors_embed(stats: ComingGoingStats) -> Embed:
    period_date = stats.before - datetime.timedelta(seconds=5)
    period_str = period_date.strftime("%d-%b")
    coming_str = "\n".join(
        [
            f"**{idx+1}** _{name}_ : {count}"
            for idx, (name, count) in enumerate(stats.sorted_coming_reacted_names())
            if idx < 15
        ]
    )
    going_str = "\n".join(
        [
            f"**{idx+1}** _{name}_ : {count}"
            for idx, (name, count) in enumerate(stats.sorted_going_reacted_names())
            if idx < 15
        ]
    )
    description = f"**Coming**\n{coming_str}\n\n**Going**\n{going_str}"
    embed = Embed()
    embed.title = "Daily Reacting Tryhard Report"
    embed.description = description
    embed.colour = statics.EMBED_DIXX_GOLD
    embed.set_footer(text=f"Reporting Period 24-hr {period_str} Limited to top 15.")
    return embed


def create_monthly_embed(stats: ComingGoingStats) -> Embed:
    period_start_date = stats.after + datetime.timedelta(seconds=5)
    period_end_date = stats.before - datetime.timedelta(seconds=5)

    period_start_str = period_start_date.strftime("%d-%b")
    period_end_str = period_end_date.strftime("%d-%b")
    net_joined = stats.coming - stats.going
    net_joined_positive_sign = "+" if net_joined > 0 else ""
    embed = Embed()
    embed.title = "Monthly Tryhard Report"
    embed.description = f"Great Job Tryhards!\n\n**{stats.get_reacted_coming_percentage():.02f}% of {stats.coming} __Joined__ Contacted.**\n**{stats.get_reacted_going_percentage():.02f}% of {stats.going} __Left__ Contacted.\n\nNet Joined:\n```diff\n{net_joined_positive_sign}{net_joined}```**"
    embed.colour = statics.EMBED_DIXX_PURPLE
    embed.add_field(
        name="Reporting Period", value=f"{period_start_str} to {period_end_str}"
    )
    embed.set_footer(text="Our Goal is 100% contact.")
    return embed


def create_monthly_reactors_embed(stats: ComingGoingStats) -> Embed:
    period_start_date = stats.after + datetime.timedelta(seconds=5)
    period_end_date = stats.before - datetime.timedelta(seconds=5)

    period_start_str = period_start_date.strftime("%d-%b")
    period_end_str = period_end_date.strftime("%d-%b")

    coming_str = "\n".join(
        [
            f"**{idx+1}** _{name}_ : {count}"
            for idx, (name, count) in enumerate(stats.sorted_coming_reacted_names())
            if idx < 15
        ]
    )
    going_str = "\n".join(
        [
            f"**{idx+1}** _{name}_ : {count}"
            for idx, (name, count) in enumerate(stats.sorted_going_reacted_names())
            if idx < 15
        ]
    )
    description = f"**Coming**\n{coming_str}\n\n**Going**\n{going_str}"
    embed = Embed()
    embed.title = "Monthly Reacting Tryhard Report"
    embed.description = description
    embed.colour = statics.EMBED_DIXX_GOLD
    embed.set_footer(
        text=f"Reporting Period {period_start_str} to {period_end_str} Limited to top 15."
    )
    return embed


def format_cg_entries(entries: List[CGEntry]) -> str:
    if len(entries) == 0:
        return "No Un-Emojied messages found. Nice Job TryHards!!!"
    links = [
        f"[{idx+1}. {entry.name}]({entry.msg_link}) "
        for idx, entry in enumerate(entries)
    ]
    return "\n".join(links)


def create_embed_oldest_in_last_24(
    entries: List[CGEntry], coming: bool = True, limit: int = 10
) -> Embed:
    now = utc_now()

    embed = Embed()
    embed.title = f"{'Coming' if coming else 'Going'} msgs without reactions <24hr"
    embed.description = format_cg_entries(entries=entries)
    embed.colour = statics.EMBED_DIXX_GOLD
    embed.set_footer(
        text=f"Only includes the oldest {limit} messages.  Updates every 10 mins."
    )
    embed.timestamp = now
    return embed


def get_before_after_for_month(
    month: int, year: int
) -> Tuple[datetime.datetime, datetime.datetime]:
    _, days_in_month = calendar.monthrange(year=year, month=month)
    last_day = datetime.datetime(
        year=year, month=month, day=days_in_month, **ZERO_TIMES
    )
    first_day = datetime.datetime(year=year, month=month, day=1, **MAX_TIMES)

    before = last_day + datetime.timedelta(days=1)
    after = first_day - datetime.timedelta(days=1)

    return before, after


def get_before_after_for_day(
    day: int, month: int, year: int
) -> Tuple[datetime.datetime, datetime.datetime]:
    start_of_day = datetime.datetime(year=year, month=month, day=day, **ZERO_TIMES)
    before = start_of_day + datetime.timedelta(days=1)

    yesterday = start_of_day - datetime.timedelta(seconds=5)
    after = yesterday.replace(**MAX_TIMES)
    return before, after


async def process_month(guild: Guild, channel_id: int, month: int, year: int) -> Embed:
    before, after = get_before_after_for_month(month=month, year=year)
    stats = await get_stats(
        guild=guild, channel_id=channel_id, before=before, after=after
    )
    embed = create_monthly_embed(stats=stats)
    return embed


async def process_day(
    guild: Guild, channel_id: int, day: int, month: int, year: int
) -> Embed:
    before, after = get_before_after_for_day(day=day, month=month, year=year)
    stats = await get_stats(
        guild=guild, channel_id=channel_id, before=before, after=after
    )
    embed = create_daily_embed(stats=stats)
    return embed


async def process_reactors_month(
    guild: Guild, channel_id: int, month: int, year: int
) -> Embed:
    before, after = get_before_after_for_month(month=month, year=year)
    stats = await get_stats(
        guild=guild,
        channel_id=channel_id,
        before=before,
        after=after,
        get_reactor_names=True,
    )
    embed = create_monthly_reactors_embed(stats=stats)
    return embed


async def process_reactors_day(
    guild: Guild, channel_id: int, day: int, month: int, year: int
) -> Embed:
    before, after = get_before_after_for_day(day=day, month=month, year=year)
    stats = await get_stats(
        guild=guild,
        channel_id=channel_id,
        before=before,
        after=after,
        get_reactor_names=True,
    )
    embed = create_daily_reactors_embed(stats=stats)
    return embed
