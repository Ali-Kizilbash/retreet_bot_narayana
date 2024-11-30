from aiogram import Bot, types
from aiogram.types import BotCommand
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def set_bot_commands(bot: Bot, is_admin: bool = False, user_id: int = None):
    """Устанавливает команды для встроенного меню Telegram для конкретного пользователя."""
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
        if user_id:
            # Устанавливаем команды только для конкретного пользователя
            await bot.set_my_commands(commands, scope=types.BotCommandScopeChat(chat_id=user_id))
        else:
            # Устанавливаем команды для всех (общий fallback)
            await bot.set_my_commands(commands)

        logger.info(f"Команды успешно установлены для {'админа' if is_admin else 'клиента'} (user_id: {user_id}).")
    except Exception as e:
        logger.error(f"Ошибка при установке команд: {e}")
