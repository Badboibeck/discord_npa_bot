from typing import List

from dixxbot.statics import SOURCE_SERVERS
from dixxbot.query_source_server.source_server import Server


async def get_servers() -> List[Server]:
    return [Server(**server) for server in SOURCE_SERVERS]
