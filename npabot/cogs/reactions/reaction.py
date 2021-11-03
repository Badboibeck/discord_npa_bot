from typing import Dict, Optional

from discord import RawReactionActionEvent, Message, PartialEmoji, Role, TextChannel
from discord.ext.commands import Bot, Context, group, Cog

from ..base import BaseCog
from dixxbot.cache.cache import populate_cache_from_db
from dixxbot.cache.reactions_tables import (
    is_in_monitored_messages,
    get_monitored_message_action,
    get_monitor_messages,
    get_monitored_message_actions_by_name,
)
from dixxbot.cogs.common.emoji_utils import DiscordEmoji, UnifiedEmoji
from dixxbot.db.repository import reactions_repo
from .add_remove_role import add_role, remove_role


class Reactions(BaseCog):
    """
    Add actions for a when user Reacts to a message.
    """

    cog_id: int = 3

    def __init__(self, bot: Bot):
        super().__init__(bot, self.cog_id)

    @Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        actions = await self.get_emoji_actions(payload=payload)
        if actions:
            if actions["action"] == "add remove role":
                await add_role(bot=self.bot, payload=payload, role_id=actions["value"])

    @Cog.listener()
    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent):
        actions = await self.get_emoji_actions(payload=payload)
        if actions:
            if actions["action"] == "add remove role":
                await remove_role(
                    bot=self.bot, payload=payload, role_id=actions["value"]
                )

    # region Commands
    @group(pass_context=True, invoke_without_command=True, case_insensitive=True)
    async def reactions(self, ctx: Context):
        """
        Add actions for a when user Reacts to a message.
        """
        await ctx.send(self.invalid_command_text("reactions"), delete_after=10.0)

    # region Config Commands
    @reactions.command(name="new")
    async def reactions_new(self, ctx: Context, name: str, message: Message = None):
        """
        Monitors a new message.
        """
        message_id = None if message is None else message.id
        result = await reactions_repo.insert_monitored_message(
            engine=self.bot.db,
            name=name,
            message_id=message_id,
            channel_id=message.channel.id,
        )
        if result:
            await populate_cache_from_db(cache=self.bot.aio_cache, db=self.bot.db)
        await ctx.send(
            f"{name} monitored message was {'successfully' if result else 'unsuccessfully'} inserted."
        )

    @reactions.group(
        pass_context=True, invoke_without_command=True, case_insensitive=True
    )
    async def edit(self, ctx: Context):
        """
        Changes which message to monitor and updates reactions to monitor.
        """
        await ctx.send(self.invalid_command_text("reactions edit"), delete_after=10.0)

    @edit.command(name="message_id")
    async def edit_message_id(self, ctx: Context, name: str, message: Message):
        """
        Changes which message to monitor.
        """
        result = await reactions_repo.set_monitored_message_id(
            engine=self.bot.db,
            name=name,
            message_id=message.id,
            channel_id=message.channel.id,
        )
        if not result.found:
            await ctx.send(f"**{name}** monitored message name was **not** found.")
            return
        if result.success:
            await populate_cache_from_db(cache=self.bot.aio_cache, db=self.bot.db)
        await ctx.send(
            f"{name} monitored message was {'successfully' if result.success else 'unsuccessfully'} updated."
        )

    @edit.command(name="add_remove_role")
    async def edit_action_add_add_remove_role(
        self, ctx: Context, monitored_name: str, emoji: DiscordEmoji, role: Role,
    ):
        """
        Updates or adds emoji to reactions to monitor.
        """
        # get monitored message
        monitored_msg = await reactions_repo.get_monitored_by_name(
            engine=self.bot.db, name=monitored_name
        )

        if monitored_msg is None:
            await ctx.send(
                f"**{monitored_name}** monitored message name was **not** found."
            )
            return

        unified_emoji = UnifiedEmoji(emoji=emoji)

        result = await reactions_repo.upsert_action_map_entry(
            engine=self.bot.db,
            emoji_id=unified_emoji.id,
            action="add remove role",
            action_value=role.id,
            reaction_monitored_message_id=monitored_msg["id"],
        )
        if result:
            if monitored_msg["channelId"] is not None:
                msg_channel: TextChannel = self.bot.get_channel(
                    monitored_msg["channelId"]
                )
                mon_msg: Message = await msg_channel.fetch_message(
                    monitored_msg["messageId"]
                )
                await mon_msg.add_reaction(emoji)
            await populate_cache_from_db(cache=self.bot.aio_cache, db=self.bot.db)
        await ctx.send(
            f"Action Entry was {'successfully' if result else 'unsuccessfully'} updated."
        )

    @reactions.group(
        pass_context=True, invoke_without_command=True, case_insensitive=True
    )
    async def remove(self, ctx: Context):
        """
        Remove monitored message and/or role.
        """
        await ctx.send(self.invalid_command_text("reactions remove"), delete_after=10.0)

    @remove.command(name="monitored_message")
    async def remove_message_id(self, ctx: Context, name: str):
        """
        Removes tracking a monitored message name.
        """
        result = await reactions_repo.remove_monitored_message(
            engine=self.bot.db, name=name
        )
        if not result.found:
            await ctx.send(f"**{name}** monitored message name was **not** found.")
        if result.success:
            await populate_cache_from_db(cache=self.bot.aio_cache, db=self.bot.db)
        await ctx.send(
            f"**{name}** monitored message name was {'successfully' if result.success else 'unsuccessfully'} removed."
        )

    @remove.command(name="add_remove_role")
    async def remove_add_remove_role(
        self, ctx: Context, monitored_name: str, emoji: DiscordEmoji
    ):
        """
        Removes tracking an emoji from a monitored message
        """
        # get monitored message
        monitored_msg = await reactions_repo.get_monitored_by_name(
            engine=self.bot.db, name=monitored_name
        )

        unified_emoji = UnifiedEmoji(emoji=emoji)

        result = await reactions_repo.remove_action_map_entry(
            engine=self.bot.db,
            emoji_id=unified_emoji.id,
            action="add remove role",
            reaction_monitored_message_id=monitored_msg["id"],
        )
        if not result.found:
            await ctx.send(f"Action Entry name was **not** found.")
            return
        if result.success:
            if monitored_msg["channelId"] is not None:
                msg_channel: TextChannel = self.bot.get_channel(
                    monitored_msg["channelId"]
                )
                mon_msg: Message = await msg_channel.fetch_message(
                    monitored_msg["messageId"]
                )
                await mon_msg.clear_reaction(emoji=emoji)
            await populate_cache_from_db(cache=self.bot.aio_cache, db=self.bot.db)
        await ctx.send(
            f"Action Entry was {'successfully' if result.success else 'unsuccessfully'} removed."
        )

    # endregion

    # region Show Commands
    @reactions.group(
        pass_context=True, invoke_without_command=True, case_insensitive=True
    )
    async def show(self, ctx: Context):
        """
        List Messages and Reactions being monitored.
        """
        await ctx.send(self.invalid_command_text("reactions show"), delete_after=10.0)

    @show.command(name="monitored")
    async def reactions_list_monitored(self, ctx: Context):
        """
        List Messages being monitored by with name.
        """
        mon_msgs = await get_monitor_messages(cache=self.bot.aio_cache)
        texts = [f"{key}: {id}" for key, id in mon_msgs.items()]
        text = "\n".join(texts)
        await ctx.send(f"**Key: ID**\n{text}")

    @show.command(name="actions")
    async def reactions_list_actions(self, ctx: Context, name: str):
        """
        List Reactions of a named monitored message.
        """
        actions = await get_monitored_message_actions_by_name(
            cache=self.bot.aio_cache, name=name
        )
        texts = ["Emoji:  Action -> Value"]
        for action in actions:
            emoji = await ctx.guild.fetch_emoji(action.emoji)
            texts.append(f"{emoji}:  {action.action} -> {action.value}")
        await ctx.send("\n".join(texts))
        if not actions:
            await ctx.send("No Actions found.")

    # endregion
    # endregion

    async def get_emoji_actions(
        self, payload: RawReactionActionEvent
    ) -> Optional[Dict[str, str]]:
        is_mon_mess = await is_in_monitored_messages(
            cache=self.bot.aio_cache, message_id=payload.message_id
        )
        if not is_mon_mess:
            return None
        if payload.emoji.id:
            actions = await get_monitored_message_action(
                cache=self.bot.aio_cache,
                message_id=payload.message_id,
                emoji_id=payload.emoji.id,
            )
            if not actions:
                return None
            return actions
