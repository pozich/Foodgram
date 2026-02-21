import json
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from sqlalchemy import select

# Импортируем твои наработки
from app.kb import main_kb
from app.database import async_session
from app.models import Post, User

# Создаем роутер, чтобы bot.py мог его увидеть
router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    """Хендлер команды /start: выдает кнопку с Web App"""
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n"
        "Добро пожаловать в Foodgram — сервис фудшеринга.\n"
        "Нажми на кнопку ниже, чтобы поделиться едой!",
        reply_markup=main_kb()
    )

@router.message(F.web_app_data)
async def handle_web_app_data(message: Message):
    """Хендлер получения данных из Web App формы"""
    # 1. Парсим JSON, который прислал JavaScript из index.html
    try:
        data = json.loads(message.web_app_data.data)
        title = data.get('title')
        description = data.get('desc')
        location = data.get('loc')
    except Exception as e:
        await message.answer("Ошибка при обработке данных из формы.")
        return

    # 2. Работа с базой данных
    async with async_session() as session:
        # Проверяем, есть ли такой юзер в нашей таблице users
        result = await session.execute(
            select(User).where(User.tg_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()

        # Если юзера нет — регистрируем его
        if not user:
            user = User(
                tg_id=message.from_user.id, 
                username=message.from_user.username
            )
            session.add(user)
            await session.flush()  # Чтобы получить ID юзера для связи с постом

        # Создаем запись об объявлении
        new_post = Post(
            title=title,
            description=description,
            location=location,
            user_id=user.id
        )
        session.add(new_post)
        
        # Сохраняем изменения в БД
        await session.commit()

    # 3. Отвечаем пользователю
    await message.answer(
        f"✅ **Объявление опубликовано!**\n\n"
        f"🍴 **Продукт:** {title}\n"
        f"📍 **Где:** {location}\n\n"
        f"Спасибо, что помогаете планете! 🌍"
    )
