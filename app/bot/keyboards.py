# app/bot/keyboards.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from config import WEB_URL

ROLE_BUTTONS = {
        "admin": KeyboardButton(text="Админка", web_app=WebAppInfo(url=f"{WEB_URL}/admin.html")),
        "seller": KeyboardButton(text="Профиль", web_app=WebAppInfo(url=f"{WEB_URL}/seller.html")),
        "worker": KeyboardButton(text="Профиль", web_app=WebAppInfo(url=f"{WEB_URL}/worker.html"))
        }


def _base_kb(*buttons: KeyboardButton) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(*buttons)
    return builder.as_markup(
            resize_keyboard=True,
            input_field_placeholder="Выберите действие..."
            )

def menu_kb(role: str = "client") -> ReplyKeyboardMarkup:
    shop_btn = KeyboardButton(text="Магазин", web_app=WebAppInfo(url=f"{WEB_URL}/client.html"))

    spec_btn = ROLE_BUTTONS.get(role)

    if spec_btn:
        return _base_kb(shop_btn, spec_btn)
    return _base_kb(shop_btn)
