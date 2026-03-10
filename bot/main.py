# bot/main.py
import asyncio
import logging
from os import getenv
import httpx
import html
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, MenuButtonWebApp
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from dotenv import load_dotenv

load_dotenv()
TOKEN = getenv("BOT_TOKEN")
API_URL = "http://api:8000"
ADMINS_ID = getenv("ADMINS_ID")



async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    dp = Dispatcher()
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Устанавливаем кнопку Mini App в меню ПРЯМО ЗДЕСЬ
    webapp_url = getenv('WEBAPP_URL')
    logging.info(f"Setting Menu Button with URL: {webapp_url}")
    try:
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(
                text="Открыть Foodgram",
                web_app=WebAppInfo(url=webapp_url)
            )
        )
        logging.info("Menu Button successfully set!")
    except Exception as e:
        logging.error(f"Failed to set Menu Button: {e}")

    @dp.message(CommandStart())
    async def command_start_handler(message: types.Message) -> None:
        user_id = str(message.from_user.id)
        role = "owner" if user_id == ADMINS_ID else "user"
        
        user_data = {
            "tg_id": message.from_user.id,
            "username": message.from_user.username,
            "role": role
        }

        webapp_button = InlineKeyboardButton(
            text="🚀 Открыть Foodgram", 
            web_app=WebAppInfo(url=getenv('WEBAPP_URL'))
        )
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[webapp_button]]
        )

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f"{API_URL}/users/", json=user_data)
                data = response.json()
                safe_name = html.escape(message.from_user.full_name)

                if data.get("status") == "created":
                    text = f"Привет, {safe_name}! Ты успешно зарегистрирован. Открой меню Foodgram по кнопке ниже или рядом с полем ввода."
                else:
                    text = f"С возвращением, {safe_name}! Ты уже авторизован. Приложение доступно по кнопке ниже."
                
                await message.answer(text, reply_markup=keyboard)

            except Exception as e:
                logging.error(f"Ошибка при связи с API: {e}")
                await message.answer("С возвращением! Меню доступно по кнопке открытия внизу.", reply_markup=keyboard)

    logging.info("Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")
