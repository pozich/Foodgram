# bot/main.py
import asyncio
import logging
from os import getenv
import httpx
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from dotenv import load_dotenv

load_dotenv()
TOKEN = getenv("BOT_TOKEN")
API_URL = "http://api:8000"
ADMINS_ID = getenv("ADMINS_ID")

async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    
    dp = Dispatcher()
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    @dp.message(CommandStart())
    async def command_start_handler(message: types.Message) -> None:
        user_id = str(message.from_user.id)
        role = "admin" if user_id == ADMINS_ID else "user"
        
        user_data = {
            "tg_id": message.from_user.id,
            "username": message.from_user.username,
            "role": role
        }

        webapp_button = KeyboardButton(
            text="🚀 Открыть Foodgram", 
            web_app=WebAppInfo(url=getenv('WEBAPP_URL'))
        )
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[webapp_button]], 
            resize_keyboard=True
        )

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f"{API_URL}/users/", json=user_data)
                
                if response.status_code in [200, 201]:
                    text = f"Привет, {message.from_user.full_name}! Ты успешно зарегистрирован."
                else:
                    text = "С возвращением в Foodgram!"
                
                await message.answer(text, reply_markup=keyboard)

            except Exception as e:
                logging.error(f"Ошибка при связи с API: {e}")
                await message.answer(
                    "Не удалось связаться с базой, но ты можешь попробовать открыть приложение:", 
                    reply_markup=keyboard
                )

    logging.info("Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")
