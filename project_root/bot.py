import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.database.db import create_db_and_tables  # Функция для создания базы и таблиц
from config import load_config  # Конфигурация
from aiogram.client.bot import DefaultBotProperties


# Настройка логирования
logging.basicConfig(level=logging.INFO)


# Инициализация бота и диспетчера
async def main():
    config = load_config()  # Загрузка конфигурации
    bot = Bot(token=config.BOT_TOKEN,
              default=DefaultBotProperties(parse_mode="HTML")) # Используем токен из конфигурации
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
