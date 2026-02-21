import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.models import Base
from dotenv import load_dotenv

load_dotenv()

engine = create_async_engine(os.getenv("DATABASE_URL"), echo=True)
async_session = async_sessionmaker(engine)

async def init_db():
    async with engine.begin() as conn:
        # Это создаст таблицы users и posts, если их нет
        await conn.run_sync(Base.metadata.create_all)
