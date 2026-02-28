# app/db/requests/bakery.py
from sqlalchemy import select, or_
from app.db.models import User # если в User есть связь с пекарней

async def get_all_sellers(session):
    """Для таблицы в админке"""
    result = await session.execute(
        select(User).where(or_(User.role == "seller", User.role == "admin"))
    )
    return result.scalars().all()

async def add_bakery(session, name, owner_id):
    # Логика добавления пекарни будет здесь
    pass
