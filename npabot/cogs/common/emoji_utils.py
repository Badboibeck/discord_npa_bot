from typing import Optional, Union

from discord import Emoji, PartialEmoji
from discord.ext.commands import Bot

DiscordEmoji = Union[Emoji, PartialEmoji, str]


def get_emoji_id(emoji: DiscordEmoji) -> str:
    emoji_id = ""
    if isinstance(emoji, str):
        emoji_id = emoji.encode("raw_unicode_escape").decode()
    if isinstance(emoji, PartialEmoji):
        if emoji.is_custom_emoji():
            emoji_id = emoji.id
        if emoji.is_unicode_emoji():
            emoji_id = emoji.name.encode("raw_unicode_escape").decode()
    if isinstance(emoji, Emoji):
        emoji_id = emoji.id
    return emoji_id


def is_custom_emoji(emoji: DiscordEmoji) -> bool:
    if isinstance(emoji, PartialEmoji):
        return emoji.is_custom_emoji()
    if isinstance(emoji, Emoji):
        return True
    return False


class UnifiedEmoji(object):
    id: str
    is_custom: bool
    display: str

    def __init__(self, emoji: DiscordEmoji):
        self.id = get_emoji_id(emoji=emoji)
        self.is_custom = is_custom_emoji(emoji=emoji)
        self.display = f"{emoji}"

    def __repr__(self):
        return f"{self.display}: <ID: {self.id}, IS_CUSTOM: {self.is_custom}>"


def emoji_id_as_int(emoji_id: str) -> Optional[int]:
    try:
        return int(emoji_id)
    except ValueError or TypeError:
        return None


def get_emoji_from_id(bot: Bot, emoji_id: str) -> Optional[Union[Emoji, str]]:
    id_as_int = emoji_id_as_int(emoji_id=emoji_id)
    if id_as_int is not None:
        return bot.get_emoji(id=id_as_int)
    return emoji_id.encode().decode("raw_unicode_escape")
