# app/bot/middlewares/__init__.py

from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from app.db.requests import reg_user, get_user_role
from config import ADMIN_IDS

class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any]
    ) -> Any:
        
        real_event = event.event
        user = getattr(real_event, 'from_user', None)

        if not user:
            return await handler(event, data)
        
        await reg_user(user.id, user.username)
        
        current_role = await get_user_role(user.id)
        
        data["role"] = current_role
        data["is_admin"] = (current_role == "admin" or user.id in ADMIN_IDS)
        
        return await handler(event, data)
