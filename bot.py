import asyncio
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from app.database import init_db
from app.handlers.user import router as user_router

load_dotenv()

async def main():
    await init_db() # Запускаем БД
    
    bot = Bot(token=os.getenv("TOKEN"))
    dp = Dispatcher()
    
    dp.include_router(user_router)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
