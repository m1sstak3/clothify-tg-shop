import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from core.config import BOT_TOKEN
from database.db import init_db
from handlers.user_handlers import router as user_router
from handlers.admin_handlers import router as admin_router

async def main():
    # Настройка базового логгирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    
    logging.info("Starting bot initialization...")
    
    # Инициализация бота с токеном из .env
    bot = Bot(token=BOT_TOKEN)
    # MemoryStorage для хранения FSM-состояний в ОЗУ (на MVP достаточно)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Регистрация роутеров (Admin-роутер идет первым, чтобы админ-команды перехватывались им)
    dp.include_router(admin_router)
    dp.include_router(user_router)
    
    # Инициализация базы данных SQLite
    await init_db()
    logging.info("Database initialized successfully.")
    
    # Сброс вебхуков при старте long-polling
    await bot.delete_webhook(drop_pending_updates=True)
    
    bot_info = await bot.get_me()
    logging.info(f"Bot @{bot_info.username} is starting polling...")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot successfully gracefully stopped.")
