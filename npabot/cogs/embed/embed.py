from copy import deepcopy
import io
from typing import Dict, List, Optional, Tuple

from discord import (
    Embed,
    TextChannel,
    Message,
    File,
    Attachment,
    HTTPException,
    Forbidden,
    NotFound,
)
from discord.ext.commands import Bot, Context, group
from loguru import logger
import ujson

from ..base import BaseCog
from .errors import TooManyEmbeds

EMBED_FIELDS = [
    "title",
    "description",
    "url",
    "timestamp",
    "color",
    "footer",
    "image",
    "thumbnail",
    "video",
    "provider",
    "author",
    "fields",
]

EMBED_FOOTER_FIELDS = ["text", "icon_url", "proxy_icon_url"]


class Embeds(BaseCog):
    """
    Publishes Embeded messages
    """

    cog_id: int = 4

    def __init__(self, bot: Bot):
        super().__init__(bot=bot, cog_id=self.cog_id)

    @group(pass_context=True, invoke_without_command=True, case_insensitive=True)
    async def embed(self, ctx: Context):
        """
        Publishes Embeded messages
        """
        await ctx.send(self.invalid_command_text("embed"), delete_after=10.0)

    @staticmethod
    def _json_decode(json: str) -> Dict:
        try:
            json_object = ujson.decode(json)
            embed_object = json_object
            if isinstance(json_object, list):
                if len(json_object) > 1:
                    raise TooManyEmbeds("More than one Embed was in decoded json")
                embed_object = json_object[0]
            return embed_object
        except ValueError as e:
            raise e
        except TooManyEmbeds as e:
            raise e

    @staticmethod
    def _get_content_and_embed(
        embed_dict: Dict,
    ) -> Tuple[Optional[str], Optional[Embed]]:
        content = None
        if "content" in embed_dict:
            content = deepcopy(embed_dict["content"])
            del embed_dict["content"]
        embed = Embed.from_dict(embed_dict)
        if not embed.to_dict():
            raise ValueError("Invalid Embed")
        return content, embed

    @embed.command(name="create")
    async def embed_create(self, ctx: Context, channel: TextChannel, *, json: str):
        """
        Create Embedded message
        """
        try:
            embed_object = self._json_decode(json=json)
            content = None
            if "content" in embed_object:
                content = deepcopy(embed_object["content"])
                del embed_object["content"]
            embed = Embed.from_dict(embed_object)
            if not embed.to_dict():
                raise ValueError("Invalid Embed")
            await channel.send(content=content, embed=embed)
        except ValueError:
            await ctx.send(
                "Invalid JSON passed. "
                "See https://discordapp.com/developers/docs/resources/channel#embed-object, and/or https://jsonformatter.curiousconcept.com/#",
                delete_after=10.0,
            )
        except TooManyEmbeds:
            await ctx.send(
                "Only one embed can be sent please remove additional embeds.",
                delete_after=10.0,
            )

    @embed.command(name="replace")
    async def embed_edit(self, ctx: Context, message: Message, *, json: str):
        """
        Replaces existing embed message
        """
        try:
            embed_object = self._json_decode(json)
            embed = Embed.from_dict(embed_object)
            if not embed.to_dict():
                raise ValueError("Invalid Embed")
            await message.edit(embed=embed)
        except ValueError:
            await ctx.send(
                "Invalid JSON passed. "
                "See https://discordapp.com/developers/docs/resources/channel#embed-object, and/or https://jsonformatter.curiousconcept.com/#",
                delete_after=10.0,
            )
        except TooManyEmbeds:
            await ctx.send(
                "Only one embed can be sent please remove additional embeds.",
                delete_after=10.0,
            )

    @embed.command(name="generator")
    async def embed_generator(self, ctx: Context):
        """
        Provides a link to an embed generator for the json.
        """
        await ctx.send("https://discohook.org/")

    @embed.command(name="linter")
    async def embed_linter(self, ctx: Context):
        """
        Provides a link to an JSON linter.
        """
        await ctx.send("https://jsonformatter.curiousconcept.com/#")

    @embed.command(name="source")
    async def embed_source(self, ctx: Context, message: Message):
        embeds = [embed.to_dict() for embed in message.embeds]
        if len(embeds) == 0:
            await ctx.send("No embed found in message.")
            return
        embeds[0]["content"] = message.content
        json_embeds = ujson.dumps(embeds, indent=4)
        if len(json_embeds) > 2000:
            embed_file = File(io.StringIO(json_embeds), filename="embed.txt")
            await ctx.send(
                "Embed source is greater than 2000 characters.  Attached file",
                file=embed_file,
            )
            return
        await ctx.send(f"```json\n{json_embeds}\n```")

    @embed.group(
        pass_context=True,
        invoke_without_command=True,
        name="file",
        case_insensitive=True,
    )
    async def from_file(self, ctx: Context):
        """
        Publishes an embed with over 2k characters by using a file.
        """
        await ctx.send(self.invalid_command_text("embed file"), delete_after=10.0)

    @from_file.command(name="create")
    async def from_file_create(self, ctx: Context, channel: TextChannel):
        """
        Create an embed with over 2k characters by using a file.
        """
        msg: Message = ctx.message
        attachments: List[Attachment] = msg.attachments
        if len(attachments) == 0:
            await ctx.send(
                "No file attachments were present. Please attach a single embed file and try again.",
                delete_after=10.0,
            )
        if len(attachments) > 1:
            await ctx.send(
                "Too many file attachments were present. Please attach a single embed file and try again.",
                delete_after=10.0,
            )
        try:
            data = await self._read_attachment_as_utf_8(attachment=attachments[0])
            embed_dict = self._json_decode(json=data)
            content, embed = self._get_content_and_embed(embed_dict=embed_dict)
            await channel.send(content=content, embed=embed)
        except NotFound:
            await ctx.send(
                f"File attachment was not found via: url: '{attachments[0].url}' or proxy_url: '{attachments[0].proxy_url}'",
                delete_after=10.0,
            )
        except Exception as e:
            await self._handle_exceptions(exception=e, ctx=ctx)

    @from_file.command(name="replace")
    async def from_file_replace(self, ctx: Context, replace_message: Message):
        """
        Replace an embed with over 2k characters by using a file.
        """
        message: Message = ctx.message
        attachments: List[Attachment] = message.attachments
        if len(attachments) == 0:
            await ctx.send(
                "No file attachments were present. Please attach a single embed file and try again.",
                delete_after=10.0,
            )
        if len(attachments) > 1:
            await ctx.send(
                "Too many file attachments were present. Please attach a single embed file and try again.",
                delete_after=10.0,
            )
        try:
            data = await self._read_attachment_as_utf_8(attachment=attachments[0])
            embed_dict = self._json_decode(json=data)
            content, embed = self._get_content_and_embed(embed_dict=embed_dict)
            await replace_message.edit(content=content, embed=embed)
        except NotFound:
            await ctx.send(
                f"File attachment was not found via: url: '{attachments[0].url}' or proxy_url: '{attachments[0].proxy_url}'",
                delete_after=10.0,
            )
        except Exception as e:
            await self._handle_exceptions(exception=e, ctx=ctx)

    @from_file.command(name="source")
    async def from_file_embed_source(self, ctx: Context, message: Message):
        """
        Send the embed source to file.
        """
        embeds = [embed.to_dict() for embed in message.embeds]
        if len(embeds) == 0:
            await ctx.send("No embed found in message.")
            return
        embeds[0]["content"] = message.content
        json_embeds = ujson.dumps(embeds, indent=4)
        embed_file = File(io.StringIO(json_embeds), filename="embed.txt")
        await ctx.send("Here is your file:", file=embed_file)

    async def _handle_exceptions(self, exception: Exception, ctx: Context):
        try:
            raise exception
        except Forbidden:
            await ctx.send(
                "Bot is forbidden from reading attachment content check permissions.",
                delete_after=10.0,
            )
        except HTTPException as e:
            logger.exception("error downloading file for embed create:", e)
            await ctx.send("Unknown error downloading the file.", delete_after=10.0)
        except UnicodeDecodeError:
            await ctx.send(
                "Attachment does not appear to be a utf-8 text document.",
                delete_after=10.0,
            )
        except ValueError:
            await ctx.send(
                "Invalid JSON passed. "
                "See https://discordapp.com/developers/docs/resources/channel#embed-object, and/or https://jsonformatter.curiousconcept.com/#",
                delete_after=10.0,
            )
        except TooManyEmbeds:
            await ctx.send(
                "Only one embed can be sent please remove additional embeds.",
                delete_after=10.0,
            )
        except Exception as e:
            logger.exception("Unknown error during from_file_create", e)
            await ctx.send("Unknown error occurred", delete_after=10.0)

    async def _read_attachment_as_utf_8(self, attachment: Attachment) -> str:
        try:
            raw = await self._robust_attachment_read(attachment=attachment)
            return self._decode_bytes(source=raw)
        except Exception as e:
            raise e

    @staticmethod
    def _decode_bytes(source: bytes) -> str:
        try:
            return source.decode("utf-8")
        except UnicodeDecodeError as e:
            raise e
        except Exception as e:
            raise e

    @staticmethod
    async def _robust_attachment_read(attachment: Attachment) -> bytes:
        try:
            return await attachment.read()
        except NotFound:
            try:
                return await attachment.read(use_cached=True)
            except NotFound as e:
                raise e
            except HTTPException as e:
                raise e
        except HTTPException as e:
            raise e
