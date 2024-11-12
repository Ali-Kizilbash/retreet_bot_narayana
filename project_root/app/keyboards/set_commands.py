from aiogram import Bot
from aiogram.types import BotCommand
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def set_bot_commands(bot: Bot):
    """Устанавливает команды для встроенного меню бота."""
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="menu", description="Показать главное меню"),
        BotCommand(command="shop", description="Перейти в магазин"),
        BotCommand(command="manager", description="Связаться с менеджером"),
        BotCommand(command="website", description="Перейти на сайт")  # Обновлено: добавлена команда website
    ]
    try:
        await bot.set_my_commands(commands)
        logger.info("Команды для встроенного меню успешно установлены.")
    except Exception as e:
        logger.error(f"Ошибка при установке команд: {e}")
