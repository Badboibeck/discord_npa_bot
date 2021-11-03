from discord import Guild, CategoryChannel

from dixxbot import statics


async def update_member_count(guild: Guild):
    channel: CategoryChannel = guild.get_channel(
        channel_id=statics.STATS_MEMBER_COUNT_CHANNEL_ID
    )
    await channel.edit(
        reason="Updating member count", name=f"「{guild.member_count}」members"
    )
