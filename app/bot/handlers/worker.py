# app/bot/handlers/worker.py
from aiogram import Router, types
from aiogram.filters import CommandStart

from app.bot.filters import RoleFilter  
from app.bot.keyboards import worker_kb      

router = Router()

router.message.filter(RoleFilter(role="worker"))

@router.message(CommandStart())
async def worker_start(message: types.Message):
    await message.answer(
        "Ты рабочий хахахахаха!!", 
        reply_markup=worker_kb()
    )
