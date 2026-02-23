# bot.py
import asyncio
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from app.db.database import init_db
from app.bot.middlewares import AuthMiddleware 
from app.bot.handlers import routers

load_dotenv()

async def main():
    await init_db() 
    
    bot = Bot(token=os.getenv("TOKEN"))
    dp = Dispatcher()

    dp.update.outer_middleware(AuthMiddleware())    
    dp.include_routers(*routers)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
