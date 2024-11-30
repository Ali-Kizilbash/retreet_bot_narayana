from aiogram import Bot
from aiogram.types import BotCommand
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def set_bot_commands(bot: Bot, is_admin: bool = False):
    """Устанавливает команды для встроенного меню бота."""
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="menu", description="Показать главное меню"),
        BotCommand(command="shop", description="Перейти в магазин"),
        BotCommand(command="website", description="Перейти на сайт"),
    ]

    # Добавляем команду manager только для клиентов
    if not is_admin:
        commands.append(BotCommand(command="manager", description="Связаться с менеджером"))

    try:
        await bot.set_my_commands(commands)
        logger.info("Команды для встроенного меню успешно установлены.")
    except Exception as e:
        logger.error(f"Ошибка при установке команд: {e}")
