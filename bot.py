# main.py
import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiohttp import web

from app.bot.handlers import router
from app.bot.middlewares import AuthMiddleware 
from app.db.database import init_db, async_session
from app.web import setup_web_handlers
from app import setup_logging 

load_dotenv()

async def start_webapp():
    app = web.Application()
    app['db_session'] = async_session

    setup_web_handlers(app)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8000)
    await site.start()
    return runner

async def main():
    setup_logging()
    await init_db() 
    
    bot = Bot(token=os.getenv("TOKEN"))
    dp = Dispatcher()

    dp.update.outer_middleware(AuthMiddleware())    
    dp.include_router(router)
    
    web_runner = await start_webapp()
    
    try:
        await dp.start_polling(bot)
    finally:
        await web_runner.cleanup()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
