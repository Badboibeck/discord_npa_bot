import re
from urllib.parse import SplitResult, urlsplit

from discord.ext.commands import Bot, Context, command

from ..base import BaseCog


ASIN_REGEX = re.compile(r".*/(?:dp|product)/(?P<asin>[A-Z0-9]+)/*.*")
NETLOCS = ["www.amazon.com", "amazon.com"]
AFFILIATE_TAG = "npagg-20"


class Amazon(BaseCog):
    """Deals with Amazon"""

    cog_id: int = 12

    def __init__(self, bot: Bot, disable_channel_check: bool = True):
        super().__init__(bot, self.cog_id, disable_channel_check=disable_channel_check)

    @command()
    async def amazon(self, ctx: Context, link: str):
        """
        Given a product link will provide an affiliate tagged link to same product.
        """
        try:
            result = urlsplit(link)
            if not all([result.scheme, result.netloc]):
                await ctx.send("Link is invalid please check and try again.")
                return
            if not result.netloc.lower() in NETLOCS:
                await ctx.send("Link does not appear to be for Amazon")
                return
            asin_match = ASIN_REGEX.match(result.path)
            if asin_match is None:
                await ctx.send("Unable to find ASIN of product from link.")
                return
            affiliate = SplitResult(
                scheme=result.scheme,
                netloc=result.netloc,
                path=result.path,
                fragment=result.fragment,
                query=f"tag={AFFILIATE_TAG}",
            )
            await ctx.send(affiliate.geturl())
        except ValueError:
            await ctx.send("Error parsing link please ensure link is valid.")
