from typing import Optional, Dict

import a2s

from dixxbot.query_source_server.source_results import SourceResults
from dixxbot.query_source_server.source_server import Server
from dixxbot.query_source_server.types import SourceInfos, Players


def handle_exception(e: Exception):
    print("Exception", e)


async def get_info(server: Server) -> Optional[SourceInfos]:
    try:
        return await a2s.ainfo(server.address_tuple)
    except Exception as e:
        handle_exception(e)
        return None


async def get_players(server: Server) -> Optional[Players]:
    try:
        return await a2s.aplayers(server.address_tuple)
    except Exception as e:
        handle_exception(e)
        return None


async def get_rules(server: Server) -> Optional[Dict]:
    try:
        return await a2s.arules(server.address_tuple)
    except Exception as e:
        handle_exception(e)
        return None


async def get_results(
    server: Server,
    include_info: bool = True,
    include_players: bool = True,
    include_rules: bool = False,
) -> SourceResults:
    info = None
    players = None
    rules = None
    if include_info:
        info = await get_info(server)
    if include_players:
        players = await get_players(server)
    if include_rules:
        rules = await get_rules(server)
    return SourceResults(server=server, info=info, players=players, rules=rules)
