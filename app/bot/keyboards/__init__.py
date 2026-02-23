# app/bot/keyboards/__init__.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

from config import WEB_URL

def admin_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="Админ-панель", 
                    web_app=WebAppInfo(url=f"{WEB_URL}/admin.html")
                )
            ]
        ],
        resize_keyboard=True,  
        input_field_placeholder="Выберите действие..."
    )
