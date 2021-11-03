from collections.abc import Iterable
from typing import Union, Iterable as IterableType

from discord import Member

from .aiters import aiter_roles


def has_role_by_id(member: Member, role_id: Union[int, IterableType[int]]) -> bool:
    member_roles = {role.id for role in member.roles}
    if isinstance(role_id, Iterable):
        check_for_roles = {rid for rid in role_id}
        roles_intersection = check_for_roles & member_roles
        return len(roles_intersection) > 0
    return role_id in member_roles


async def async_has_role_by_id(
    member: Member, role_id: Union[int, IterableType[int]]
) -> bool:
    member_roles = set()
    async for role in aiter_roles(member.roles):
        member_roles.add(role.id)
    if isinstance(role_id, Iterable):
        check_for_roles = {rid for rid in role_id}
        roles_intersection = check_for_roles & member_roles
        return len(roles_intersection) > 0
    return role_id in member_roles
