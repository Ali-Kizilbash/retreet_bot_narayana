from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from config import Config
from app.keyboards.client_kb import get_two_column_keyboard
from app.keyboards.admin_kb import get_admin_menu
from app.handlers.state import user_status
from app.handlers.common import is_staff
import logging

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)



router = Router()

@router.message(Command("shop"))
async def shop_command_handler(message: Message):
    """Обработчик для команды /shop, отправляет ссылку на интернет-магазин."""
    shop_link = Config.LINKS["store"][0]["url"]
    await message.answer(f"Добро пожаловать в наш интернет-магазин! Ознакомьтесь с ассортиментом по ссылке: {shop_link}")

@router.message(Command("website"))
async def website_command_handler(message: Message):
    """Обработчик для команды /website, отправляет ссылку на сайт."""
    website_link = Config.LINKS["website"][0]["url"]
    await message.answer(f"Перейдите на наш сайт для дополнительной информации: {website_link}")


@router.message(Command("menu"))
async def show_main_menu(message: Message):
    """Обработчик для команды /menu. Всегда проверяет статус через is_staff."""
    user_id = message.from_user.id
    username = message.from_user.username
    logger.info(f"Команда /menu получена от пользователя: user_id={user_id}, username={username}")

    # Проверяем, является ли пользователь администратором
    is_admin = is_staff(user_id=user_id, username=f"@{username}" if username else None)
    logger.debug(f"Проверка администратора: user_id={user_id}, username={username}, is_admin={is_admin}")

    if is_admin:
        # Если админ, показываем админское меню
        logger.info(f"Пользователь {user_id} ({username}) получает админ-панель.")
        await message.answer("Админ-панель:", reply_markup=get_admin_menu())
    else:
        # Если не админ, показываем клиентское меню
        is_organizer = user_status.get(user_id) == "organizer"  # Временная проверка
        logger.info(f"Пользователь {user_id} ({username}) получает клиентское меню. Организатор: {is_organizer}")
        await message.answer(
            "Выберите действие из меню:",
            reply_markup=get_two_column_keyboard(is_organizer=is_organizer)
        )

