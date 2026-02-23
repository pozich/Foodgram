# app/bot/handlers/client.py
from aiogram import Router, types
from aiogram.filters import CommandStart

from app.bot.filters import RoleFilter  
from app.bot.keyboards import client_kb      

router = Router()

router.message.filter(RoleFilter(role="client"))

@router.message(CommandStart())
async def client_start(message: types.Message):
    await message.answer(
        "Ты клиент!! (шок)", 
        reply_markup=client_kb()
    )
