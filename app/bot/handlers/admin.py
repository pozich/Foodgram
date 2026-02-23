# app/bot/handlers/admin.py
from aiogram import Router, types
from aiogram.filters import CommandStart

from app.bot.filters import IsAdmin
from app.bot.keyboards import admin_kb

router = Router()
router.message.filter(IsAdmin())

@router.message(CommandStart())
async def admin_start(message: types.Message):
    await message.answer("Ты админ!! (шок)", reply_markup=admin_kb())
