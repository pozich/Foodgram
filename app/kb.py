from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

def main_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🍎 Поделиться едой", 
                            web_app=WebAppInfo(url="https://pozich.github.io/Foodgram/"))]
        ],
        resize_keyboard=True
    )
