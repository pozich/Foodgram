# app/bot/db/requests.py
from sqlalchemy import select, update, or_

from app.db.database import async_session
from app.db.models import User
from config import ADMIN_IDS

async def get_or_reg_user(tg_id: int, username: str):
    async with async_session() as session:
        # 1. Ищем по ID
        result = await session.execute(select(User).where(User.tg_id == tg_id))
        user = result.scalar_one_or_none()

        if user:
            # Обновляем юзернейм, если он изменился в телеге
            user.username = username
        else:
            # 2. Если по ID нет, ищем "забронированного" по юзернейму
            if username:
                # Ищем запись, где username совпал, а ID еще нет (NULL)
                result = await session.execute(
                    select(User).where(User.username == username, User.tg_id == None)
                )
                user = result.scalar_one_or_none()
            
            if user:
                # Нашли заглушку — привязываем реальный ID
                user.tg_id = tg_id
            else:
                # 3. Совсем новый юзер
                user = User(tg_id=tg_id, username=username, role="client")
                session.add(user)
        
        await session.commit()
        
        # КЛЮЧЕВОЙ МОМЕНТ: 
        # Нам нужно "оживить" объект после коммита, чтобы обращение к .role не вызывало ошибку
        await session.refresh(user) 
        return user.role

async def set_user_role(session, target, role):
    # 1. Определяем, как ищем юзера
    if str(target).startswith('@'):
        clean_target = target.replace('@', '')
        query = select(User).where(User.username == clean_target)
    else:
        clean_target = int(target)
        query = select(User).where(User.tg_id == clean_target)

    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if user:
        # Если юзер есть — просто обновляем роль
        user.role = role
    else:
        # 2. Если юзера нет — создаем новую запись (предрегистрация)
        if str(target).startswith('@'):
            new_user = User(
                tg_id=None,
                username=target.replace('@', ''),
                role=role
            )
        else:
            new_user = User(
                tg_id=int(target),
                role=role,
                username=None # Или "Unknown"
            )
        session.add(new_user)
    
    # Сохраняем изменения
    await session.commit()
    return True
