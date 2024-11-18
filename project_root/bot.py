import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from config import load_config, validate_config
from app.handlers import (common_router, client_router, admin_router,
                          support_router, commands_router,
                          broadcast_router)
from app.database.db import create_db_and_tables
from app.database.crud import register_client
from app.database.db import async_session
from app.database.db import test_connection

# Импорт функции для установки команд
from app.keyboards.set_commands import set_bot_commands

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]  # Вывод логов в консоль
)

logger = logging.getLogger(__name__)


async def migrate_existing_users(bot: Bot):
    """Миграция существующих пользователей (примерная логика)."""
    user_ids = [123456789, 987654321]  # ID существующих пользователей
    async with async_session() as session:
        for user_id in user_ids:
            try:
                user = await bot.get_chat_member(chat_id=user_id, user_id=user_id)
                await register_client(
                    session,
                    user_id=user.user.id,
                    first_name=user.user.first_name,
                    last_name=user.user.last_name,
                    client_type="unknown"  # Можно обновить вручную после миграции
                )
                logger.info(f"Пользователь {user.user.id} мигрирован.")
            except Exception as e:
                logger.error(f"Ошибка при миграции пользователя {user_id}: {e}")


async def main():
    # Проверка конфигурации
    try:
        validate_config()
        logger.info("Конфигурация успешно проверена.")
    except EnvironmentError as e:
        logger.error(f"Ошибка конфигурации: {e}")
        exit(1)

    # Загрузка конфигурации
    config = load_config()

    # Создание базы данных и таблиц
    try:
        logger.info("Инициализация базы данных...")
        await create_db_and_tables()
        logger.info("База данных успешно инициализирована.")
    except Exception as e:
        logger.error(f"Ошибка при создании базы данных: {e}")
        exit(1)

    # Инициализация бота
    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))

    # Миграция существующих пользователей
    try:
        logger.info("Миграция существующих пользователей...")
        await migrate_existing_users(bot)
    except Exception as e:
        logger.error(f"Ошибка при миграции пользователей: {e}")

    # Установка команд меню
    await set_bot_commands(bot)

    # Инициализация диспетчера
    dp = Dispatcher(storage=MemoryStorage())

    # Подключение маршрутизаторов
    dp.include_router(common_router)
    dp.include_router(client_router)
    dp.include_router(admin_router)
    dp.include_router(support_router)
    dp.include_router(commands_router)
    dp.include_router(broadcast_router)

    try:
        logger.info("Запуск polling для бота.")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске polling: {e}")
    finally:
        await bot.session.close()
        logger.info("Сессия бота закрыта.")


asyncio.run(test_connection())


if __name__ == "__main__":
    asyncio.run(main())
