import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.database.db import create_db_and_tables  # Функция для создания базы и таблиц
from app.config import load_config  # Конфигурация
from dotenv import load_dotenv
import os

# Загружаем переменные окружения из .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
async def main():
    config = load_config()  # Загрузка конфигураций
    bot = Bot(token=TOKEN, parse_mode="HTML")
    dp = Dispatcher(storage=MemoryStorage())

    # Инициализация базы данных и создание таблиц, если их нет
    await create_db_and_tables()

    # Запуск обработчиков
    dp.include_router(app.handlers.common.router)  # Подключаем общие обработчики
    dp.include_router(app.handlers.client.router)  # Подключаем обработчики для клиентов
    dp.include_router(app.handlers.admin.router)  # Подключаем обработчики для администраторов

    # Запуск бота
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

# Запуск основного цикла
if __name__ == "__main__":
    asyncio.run(main())
