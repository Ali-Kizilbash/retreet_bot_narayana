import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from config import load_config, validate_config
from app.handlers import (common_router, client_router,
                          admin_router, support_router)


# Импорт функции для установки команд
from app.keyboards.set_commands import set_bot_commands

# Настройка логирования
logging.basicConfig(level=logging.INFO)

print("Загрузка файла bot.py")  # Сообщение о загрузке файла

# Основная функция
async def main():
    # Проверка конфигурации
    try:
        validate_config()
        print("Конфигурация успешно проверена.")
    except EnvironmentError as e:
        print(f"Ошибка конфигурации: {e}")
        exit(1)  # Завершаем выполнение, если отсутствуют необходимые переменные

    # Загрузка конфигурации и проверка токена
    config = load_config()
    print("Конфигурация загружена успешно.")
    print("Полный токен бота:", config.BOT_TOKEN)  # Полный токен для проверки
    print("Длина токена:", len(config.BOT_TOKEN) if config.BOT_TOKEN else "Токен отсутствует")

    # Проверка, правильно ли токен загружен (он должен быть строкой и иметь правильную длину)
    if not config.BOT_TOKEN or not isinstance(config.BOT_TOKEN, str):
        print("Ошибка: Токен бота не загружен или имеет неверный формат.")
        exit(1)
    elif len(config.BOT_TOKEN.split(":")) != 2:
        print("Ошибка: Токен бота имеет неправильный формат.")
        exit(1)

    # Инициализация бота и проверка авторизации
    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    try:
        bot_user = await bot.get_me()  # Проверка, что бот может авторизоваться
        print("Бот успешно авторизован. Информация о боте:", bot_user)
    except Exception as e:
        print("Ошибка авторизации бота:", e)
        exit(1)

    # Установка команд меню
    await set_bot_commands(bot)

    # Инициализация диспетчера
    dp = Dispatcher(storage=MemoryStorage())
    
    # Подключение роутеров (обработчиков)
    dp.include_router(common_router)
    dp.include_router(client_router)
    dp.include_router(admin_router)
    dp.include_router(support_router)  # Добавляем support_router, если он существует
    print("Роутеры подключены.")

    # Запуск бота
    try:
        print("Запуск бота...")
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")
    finally:
        print("Закрытие сессии бота.")
        await bot.session.close()

# Запуск основного цикла
if __name__ == "__main__":
    print("Запуск основного цикла.")
    asyncio.run(main())
