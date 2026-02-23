# app/bot/db/requests.py
from sqlalchemy import select

from app.db.database import async_session
from app.db.models import User
from config import ADMIN_IDS

async def reg_user(tg_id: int, username: str = None):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            new_role = 'admin' if tg_id in ADMIN_IDS else 'client'
            session.add(User(tg_id=tg_id, username=username, role=new_role))
            await session.commit()
        elif user.username != username:
            user.username = username
            await session.commit()

async def get_user_role(tg_id: int) -> str:
    async with async_session() as session:
        query = select(User.role).where(User.tg_id == tg_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()
