import asyncio
import os
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiohttp import web

from app.db.database import init_db, async_session
from app.bot.middlewares import AuthMiddleware 
from app.web import setup_web_handlers
from app.bot.handlers import routers

load_dotenv()

async def start_webapp():
    app = web.Application()
    app['db_session'] = async_session

    # Теперь всё настраивается одной функцией
    setup_web_handlers(app)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8000)
    await site.start()
    logging.info("✅ WebApp запущен на http://localhost:8000")
    return runner

async def main():
    logging.basicConfig(level=logging.INFO)
    await init_db() 
    
    bot = Bot(token=os.getenv("TOKEN"))
    dp = Dispatcher()

    dp.update.outer_middleware(AuthMiddleware())    
    dp.include_routers(*routers)
    
    web_runner = await start_webapp()
    
    try:
        logging.info("🚀 Бот и WebApp запущены!")
        await dp.start_polling(bot)
    finally:
        await web_runner.cleanup()
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен")
