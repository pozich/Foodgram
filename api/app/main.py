# api/app/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from dotenv import load_dotenv
import os

from app.database import engine, get_db  # Убедись, что get_db есть в database.py
from app.models import Base, User, OwnerProfile, Tier

load_dotenv()
ADMINS_ID = int(os.getenv("ADMINS_ID", 0))
app = FastAPI()

# Схема для получения данных от бота
class UserCreate(BaseModel):
    tg_id: int
    username: str | None = None
    role: str = "user"

@app.get("/owner/profile")
async def get_owner_full_profile(tg_id: int, db: AsyncSession = Depends(get_db)):
    # 1. Проверяем, не ты ли это (супер-админ из .env)
    is_admin_from_env = (tg_id == ADMINS_ID)

    result = await db.execute(
        select(User)
        .where(User.tg_id == tg_id)
        .options(
            selectinload(User.owner_profile).selectinload(OwnerProfile.bakeries),
            selectinload(User.owner_profile).selectinload(OwnerProfile.tier)
        )
    )
    user = result.scalar_one_or_none()
    
    # Если тебя нет в базе, но ID совпадает с админским — создадим тебя "на лету" (опционально)
    # Или просто разрешим доступ, если роль в базе 'owner' ИЛИ ты из .env
    if not user or (user.role != 'owner' and not is_admin_from_env):
        raise HTTPException(status_code=403, detail="Доступ только для владельцев")

    # Если ты админ из env, но в базе у тебя еще нет пекарен, вернем пустой список
    return {
        "user": user,
        "tier": user.owner_profile.tier if user and user.owner_profile else {"name": "Admin Mode", "commission": 0},
        "bakeries": user.owner_profile.bakeries if user and user.owner_profile else []
    }

@app.post("/users/")
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    # Проверяем, существует ли уже такой пользователь
    query = select(User).where(User.tg_id == user_data.tg_id)
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        return {"status": "ok", "message": "User already exists"}

    # Создаем нового пользователя
    new_user = User(
        tg_id=user_data.tg_id,
        username=user_data.username,
        role=user_data.role
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return {"status": "created", "user_id": new_user.id}

@app.get("/")
def read_root():
    return {"message": "Foodgram API is running"}
