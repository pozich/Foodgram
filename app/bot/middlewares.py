# app/bot/middlewares.py
from aiogram import BaseMiddleware

from app.db.requests.users import get_or_reg_user
from app.db.database import async_session
from config import ADMIN_IDS

class AuthMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = data.get("event_from_user")

        if not user:
            return await handler(event, data)
        
        async with async_session() as session:
            current_role = await get_or_reg_user(session, user.id, user.username)

        is_admin = (current_role == "admin" or user.id in ADMIN_IDS)
        if is_admin:
            current_role = "admin"
        
        data["role"] = current_role
        data["is_admin"] = is_admin
        
        return await handler(event, data)
