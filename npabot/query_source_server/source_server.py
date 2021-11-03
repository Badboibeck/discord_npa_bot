from typing import Tuple, NamedTuple


class Server(NamedTuple):
    offline_name: str
    address: str
    query_port: int
    discord_guild: int
    discord_channel: int
    discord_msg: int
    embed_thumbnail: str

    @property
    def address_tuple(self) -> Tuple[str, int]:
        return self.address, self.query_port

    @property
    def steam_connect_url(self) -> str:
        return f"steam://connect/{self.address}:{self.query_port}"
