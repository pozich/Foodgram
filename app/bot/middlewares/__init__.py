# app/bot/middlewares/__init__.py

from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from app.db.requests import get_or_reg_user
from config import ADMIN_IDS

class AuthMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        # В aiogram 3.x правильнее брать юзера так:
        user = data.get("event_from_user")

        if not user:
            return await handler(event, data)
        
        # Получаем или регистрируем за один заход
        current_role = await get_or_reg_user(user.id, user.username)
        
        data["role"] = current_role
        data["is_admin"] = (current_role == "admin" or user.id in ADMIN_IDS)
        
        return await handler(event, data)
