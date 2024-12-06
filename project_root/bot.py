#основной файл
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from config import load_config, validate_config
from app.database.db import close_db, create_db_and_tables
from app.handlers import (
    common_router,
    client_router,
    admin_router,
    support_router,
    commands_router,
    broadcast_router
)
from app.keyboards.set_commands import set_bot_commands

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

print("Загрузка файла bot.py")

# Основная функция
async def main():
    try:
        # Проверка и загрузка конфигурации
        validate_config()
        logger.info("Конфигурация успешно проверена.")
        config = load_config()
        logger.info("Конфигурация загружена успешно.")
        logger.info(f"Длина токена: {len(config.BOT_TOKEN) if config.BOT_TOKEN else 'Токен отсутствует'}")

        if not config.BOT_TOKEN or not isinstance(config.BOT_TOKEN, str) or len(config.BOT_TOKEN.split(":")) != 2:
            logger.error("Ошибка: Токен бота не загружен или имеет неверный формат.")
            exit(1)

        # Инициализация базы данных
        logger.info("Инициализация базы данных.")
        await create_db_and_tables()
        logger.info("База данных и таблицы успешно созданы.")

        # Инициализация бота
        bot = Bot(
            token=config.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode="HTML")
        )
        bot_user = await bot.get_me()
        logger.info(f"Бот успешно авторизован. Информация о боте: {bot_user}")

        # Инициализация диспетчера
        dp = Dispatcher(storage=MemoryStorage())

        # Подключение роутеров
        dp.include_router(common_router)
        dp.include_router(client_router)
        dp.include_router(admin_router)
        dp.include_router(support_router)
        dp.include_router(commands_router)
        dp.include_router(broadcast_router)

        # Установка команд меню
        await set_bot_commands(bot)

        # Запуск бота
        try:
            logger.info("Запуск polling для бота.")
            await dp.start_polling(bot)
        except Exception as e:
            logger.error(f"Ошибка при запуске polling: {e}")
        finally:
            logger.info("Остановка бота. Закрытие соединений.")
            await bot.session.close()
            await close_db()
            logger.info("Сессия бота и подключение к базе данных закрыты.")

    except Exception as e:
        logger.error(f"Фатальная ошибка: {e}")
        await close_db()
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())
