# app/handlers.py
from aiogram import Router, types
from aiogram.filters import CommandStart

from app.bot.keyboards import menu_kb

router = Router()

GREETINGS = {
        "admin": "Вы являетесь самым умным, красивым и великолепным человеком (создателем бота)",
        "seller": "Добро пожаловать, по всем вопросам @pozich",
        "worker": "Ты работник, работай, иначе зп не повысят :)",
        "client": "Мы рады что вы пользуетесь сервисом, приятнава покушать вам :з"
        }

@router.message(CommandStart())
async def cmd_start(message: types.Message, role: str):
    text = GREETINGS.get(role, GREETINGS["client"])

    await message.answer(
            text, 
            reply_markup=menu_kb(role=role)
            )


