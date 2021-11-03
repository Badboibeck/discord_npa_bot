from typing import Iterable, AsyncGenerator

from discord import Role, Member


async def aiter_roles(roles: Iterable[Role]) -> AsyncGenerator[Role, None]:
    for role in roles:
        yield role


async def aiter_members(members: Iterable[Member]) -> AsyncGenerator[Member, None]:
    for member in members:
        yield member
