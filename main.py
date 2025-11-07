import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from bot.db.session import init_db
from bot.handlers import common, ocr, stats, echo


async def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting bot...")

    await init_db()
    logging.info("Database initialized")

    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.include_router(common.router)
    dp.include_router(stats.router)
    dp.include_router(ocr.router)

    # Echo router should be last
    dp.include_router(echo.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
