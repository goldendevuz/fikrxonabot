import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import init_db

from handlers.start import router as start_router
from handlers.search import router as search_router
from handlers.categories import router as categories_router
from handlers.recommend import router as recommend_router
from handlers.admin import router as admin_router

logging.basicConfig(level=logging.INFO)


async def main():
    init_db()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    dp.include_router(admin_router)
    dp.include_router(start_router)
    dp.include_router(search_router)
    dp.include_router(categories_router)
    dp.include_router(recommend_router)

    logging.info("✅ Fikrxona bot ishga tushdi!")
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
