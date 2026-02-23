# app/bot/handlers/seller.py
from aiogram import Router, types
from aiogram.filters import CommandStart

from app.bot.filters import RoleFilter  
from app.bot.keyboards import seller_kb      

router = Router()

router.message.filter(RoleFilter(role="seller"))

@router.message(CommandStart())
async def seller_start(message: types.Message):
    await message.answer(
        "Ты продовэц!!", 
        reply_markup=seller_kb()
    )
