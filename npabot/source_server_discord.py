from discord import Client, Embed, Guild, TextChannel, Message

from dixxbot.common.date_time import utc_now
from dixxbot.query_source_server.querier import get_results
from dixxbot.query_source_server.retrieve_servers import get_servers
from dixxbot.query_source_server.source_results import SourceResults


def value_or_default(value, default):
    if value is not None:
        return value
    return default


def make_embed(results: SourceResults) -> Embed:
    embed_dict = {
        "title": f"**{results.name}**{'' if results.online else ' is Offline'}",
        "color": 1687570 if results.online else 12587538,
        "footer": {"text": "Never Play Alone, Copyright © 2021"},
        "timestamp": utc_now().isoformat(),
        "thumbnail": {"url": results.server.embed_thumbnail},
    }
    if results.online:
        embed_dict["fields"] = [
            {
                "name": "Map",
                "value": value_or_default(results.current_map, "Map info unavailable"),
                "inline": True,
            },
            {
                "name": "Players",
                "value": f"{value_or_default(results.current_player_count, 'unknown')}/{value_or_default(results.max_players, 'unknown')}",
                "inline": True,
            },
            {
                "name": "Connect",
                "value": results.server.steam_connect_url,
                "inline": False,
            },
        ]
    return Embed.from_dict(embed_dict)


def get_client(logger) -> Client:
    client = Client()

    @client.event
    async def on_ready():
        print(f"We have logged in as {client.user}")
        servers = await get_servers()

        print("Retrieving server data")
        for server in servers:
            results = await get_results(server=server)
            embed = make_embed(results=results)
            guild: Guild = client.get_guild(server.discord_guild)
            channel: TextChannel = guild.get_channel(server.discord_channel)
            msg: Message = await channel.fetch_message(server.discord_msg)
            await msg.edit(embed=embed)
        await client.close()

    return client
