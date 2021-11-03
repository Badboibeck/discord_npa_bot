from discord import Message, TextChannel
from discord.ext.commands import Bot


async def get_message_from_channel_msg_id(
    bot: Bot, channel_id: int, msg_id: int
) -> Message:
    channel: TextChannel = bot.get_channel(channel_id)
    msg: Message = await channel.fetch_message(msg_id)
    return msg
