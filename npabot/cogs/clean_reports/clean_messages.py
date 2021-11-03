import asyncio
from typing import Dict, Optional, List

from discord import (
    RawReactionActionEvent,
    Role,
    Member,
    Forbidden,
    HTTPException,
    NotFound,
)
from discord.ext.commands import Bot, Cog
from loguru import logger

from ..base import BaseCog
from ..common.get_message import get_message_from_channel_msg_id
from dixxbot.statics import (
    EMOTE_CHECK_MARK_BUTTON,
    GOAT_ROLE_ID,
    REDS_ROLE_ID,
    ADMIN_HLL_SR_ROLE_ID,
    ADMIN_SQD_SR_ROLE_ID,
    ADMIN_RUST_ROLE_ID,
    DIXX_DEVS_ROLE_ID,
    OPERATORS_ROLE_ID,
    HLL_ADMIN_SUPPORT_REPORT_CHANNEL_ID,
    SQD_ADMIN_SUPPORT_REPORT_CHANNEL_ID,
    RUST_ADMIN_SUPPORT_REPORT_CHANNEL_ID,
)

ALLOWED_ROLE_IDS = {
    # DIXX_DEVS_ROLE_ID,
    GOAT_ROLE_ID,
    REDS_ROLE_ID,
    ADMIN_HLL_SR_ROLE_ID,
    ADMIN_SQD_SR_ROLE_ID,
    ADMIN_RUST_ROLE_ID,
    OPERATORS_ROLE_ID,
}

DELAY = 5.00 * 60


def in_allowed_roles(roles: List[Role]) -> bool:
    for role in roles:
        if role.id in ALLOWED_ROLE_IDS:
            return True
    return False


class CleanReports(BaseCog):
    """Removes message after reaction by certain roles with a delay"""

    cog_id: int = 9

    def __init__(self, bot: Bot):
        super().__init__(bot, self.cog_id)

    @Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        if payload.channel_id not in [
            HLL_ADMIN_SUPPORT_REPORT_CHANNEL_ID,
            SQD_ADMIN_SUPPORT_REPORT_CHANNEL_ID,
            RUST_ADMIN_SUPPORT_REPORT_CHANNEL_ID,
        ]:
            return
        if payload.event_type != "REACTION_ADD":
            return
        if str(payload.emoji) != EMOTE_CHECK_MARK_BUTTON:
            return
        if payload.message_id in [8, 8]:
            return
        member: Optional[Member] = payload.member
        if member is None:
            return
        if not in_allowed_roles(roles=member.roles):
            return
        await asyncio.sleep(DELAY)
        msg = await get_message_from_channel_msg_id(
            bot=self.bot, channel_id=payload.channel_id, msg_id=payload.message_id
        )
        try:
            await msg.delete()
        except Forbidden:
            logger.error(
                f"CleanReports <Channel: {payload.channel_id}, Message: {payload.message_id}> - Permission denied to delete."
            )
        except NotFound:
            pass
        except HTTPException as e:
            logger.exception(
                f"CleanReports <Channel: {payload.channel_id}, Message: {payload.message_id}> - HTTP error",
                e,
            )
        except Exception as e:
            logger.exception(
                f"CleanReports <Channel: {payload.channel_id}, Message: {payload.message_id}> - Unknown Exception",
                e,
            )
