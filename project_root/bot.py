import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from config import load_config  # Конфигурация
from app.database.db import create_db_and_tables  # Функция для создания базы и таблиц
import app.handlers.common
import app.handlers.client
import app.handlers.admin

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Основная функция
async def main():
    # Загрузка конфигурации
    config = load_config()
    
    # Инициализация бота с DefaultBotProperties для parse_mode
    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    
    # Инициализация диспетчера с памятью для состояния
    dp = Dispatcher(storage=MemoryStorage())
    
    # Инициализация базы данных и создание таблиц, если их нет
    await create_db_and_tables()
    
    # Подключение роутеров (обработчиков)
    dp.include_router(app.handlers.common.router)
    dp.include_router(app.handlers.client.router)
    dp.include_router(app.handlers.admin.router)

    # Запуск бота
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

# Запуск основного цикла
if __name__ == "__main__":
    asyncio.run(main())
