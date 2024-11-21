import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from config import load_config, validate_config
from app.handlers import (common_router, client_router, admin_router,
                          support_router, commands_router,
                          broadcast_router)
from app.database.db import async_session, create_db_and_tables, check_session
from sqlalchemy.ext.asyncio import AsyncSession

# Импорт функции для установки команд
from app.keyboards.set_commands import set_bot_commands

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]  # Вывод логов в консоль
)

logger = logging.getLogger(__name__)

print("Загрузка файла bot.py")


class DbSessionMiddleware:
    """Middleware для предоставления сессии базы данных в обработчики."""
    
    async def __call__(self, handler, event, data):
        async with async_session() as session:
            data["session"] = session  # Передаем сессию в данные для обработчика
            return await handler(event, data)


# Основная функция
async def main():
    # Проверка конфигурации
    try:
        validate_config()
        logger.info("Конфигурация успешно проверена.")
    except EnvironmentError as e:
        logger.error(f"Ошибка конфигурации: {e}")
        exit(1)  # Завершаем выполнение, если отсутствуют необходимые переменные

    # Загрузка конфигурации и проверка токена
    config = load_config()
    logger.info("Конфигурация загружена успешно.")
    logger.info(f"Полный токен бота: {config.BOT_TOKEN}")
    logger.info(f"Длина токена: {len(config.BOT_TOKEN) if config.BOT_TOKEN else 'Токен отсутствует'}")

    # Проверка токена
    if not config.BOT_TOKEN or not isinstance(config.BOT_TOKEN, str) or len(config.BOT_TOKEN.split(":")) != 2:
        logger.error("Ошибка: Токен бота не загружен или имеет неверный формат.")
        exit(1)

    # Проверка подключения к базе данных
    try:
        logger.info("Проверяем подключение к базе данных...")
        await check_session()  # Проверка подключения
        await create_db_and_tables()  # Создание таблиц
        logger.info("Подключение к базе данных успешно проверено и таблицы созданы.")
    except Exception as e:
        logger.error(f"Ошибка подключения к базе данных: {e}")
        exit(1)

    # Инициализация бота
    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    try:
        bot_user = await bot.get_me()
        logger.info(f"Бот успешно авторизован. Информация о боте: {bot_user}")
    except Exception as e:
        logger.error(f"Ошибка авторизации бота: {e}")
        exit(1)

    # Установка команд меню
    await set_bot_commands(bot)

    # Инициализация диспетчера с MemoryStorage
    dp = Dispatcher(storage=MemoryStorage())  # Использование MemoryStorage для хранения состояний

    # Добавляем Middleware для передачи сессии базы данных
    dp.message.middleware(DbSessionMiddleware())
    dp.callback_query.middleware(DbSessionMiddleware())

    # Подключение маршрутизаторов
    dp.include_router(common_router)
    dp.include_router(client_router)
    dp.include_router(admin_router)
    dp.include_router(support_router)
    dp.include_router(commands_router)
    dp.include_router(broadcast_router)

    # Запуск бота с логированием состояния
    try:
        logger.info("Запуск polling для бота.")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске polling: {e}")
    finally:
        await bot.session.close()
        logger.info("Сессия бота закрыта.")


if __name__ == "__main__":
    asyncio.run(main())
