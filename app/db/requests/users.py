# app/db/requests/users.py
from sqlalchemy import select, or_
from app.db.models import User

async def _get_user_by_id_or_name(session, target):
    if str(target).startswith('@'):
        username = target.replace('@', '')
        query = select(User).where(User.username == username)
    else:
        try:
            query = select(User).where(User.tg_id == int(target))
        except ValueError:
            return None
    
    result = await session.execute(query)
    return result.scalar_one_or_none()

async def get_or_reg_user(session, tg_id: int, username: str):
    result = await session.execute(select(User).where(User.tg_id == tg_id))
    user = result.scalar_one_or_none()

    if user:
        user.username = username
    else:
        if username:
            result = await session.execute(
                select(User).where(User.username == username, or_(User.tg_id == None, User.tg_id == 0))
            )
            user = result.scalar_one_or_none()
        
        if user:
            user.tg_id = tg_id
        else:
            user = User(tg_id=tg_id, username=username, role="client")
            session.add(user)
    
    await session.commit()
    await session.refresh(user)
    return user.role

async def set_user_role(session, target, role):
    try:
        user = await _get_user_by_id_or_name(session, target)

        if user:
            user.role = role
        else:
            is_username = str(target).startswith('@')
            new_user = User(
                tg_id=0 if is_username else int(target),
                username=target.replace('@', '') if is_username else None,
                role=role
            )
            session.add(new_user)
        
        await session.commit()
        return True
    except Exception:
        await session.rollback()
        return False

async def get_all_sellers(session):
    stmt = select(User).where(User.role == 'seller').order_by(User.id)
    result = await session.execute(stmt)
    return result.scalars().all()
