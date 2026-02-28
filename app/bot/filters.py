# app/bot/filters.py

from aiogram.filters import BaseFilter
from aiogram.types import Message

class IsAdmin(BaseFilter):
    async def __call__(self, message: Message, is_admin: bool = False) -> bool:
        return is_admin

class RoleFilter(BaseFilter):
    def __init__(self, role: str | list[str]):
        self.role = role

    async def __call__(self, message: Message, role: str | None = None) -> bool:
        if isinstance(self.role, list):
            return role in self.role

        return role == self.role
