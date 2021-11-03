from typing import Dict, NamedTuple, Optional

from dixxbot.query_source_server.source_server import Server
from dixxbot.query_source_server.types import SourceInfos, Players


class SourceResults(NamedTuple):
    server: Server
    info: Optional[SourceInfos]
    players: Optional[Players]
    rules: Optional[Dict]

    @property
    def online(self) -> bool:
        return any(
            [self.info is not None, self.players is not None, self.rules is not None,]
        )

    @property
    def name(self) -> str:
        if self.info is not None and len(self.info.server_name.strip()) > 0:
            return self.info.server_name
        return self.server.offline_name

    @property
    def current_player_count(self) -> Optional[int]:
        if self.players is not None:
            return len(self.players)
        if self.info is not None:
            return self.info.player_count
        return None

    @property
    def max_players(self) -> Optional[int]:
        if self.info is not None:
            return self.info.max_players
        return None

    @property
    def current_map(self) -> Optional[str]:
        if self.info is not None:
            return self.info.map_name
        return None
