from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from config import Config
from app.keyboards.client_kb import get_two_column_keyboard
from app.handlers.common import user_status


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

        # Используем is_staff для проверки администратора
        if is_staff(user_id=user_id, username=f"@{username}" if username else None):
            # Если админ, показываем админское меню
            await message.answer("Админ-панель:", reply_markup=get_admin_menu())
        else:
            # Если не админ, определяем статус клиента (например, organizer или individual)
            is_organizer = user_status.get(user_id) == "organizer"  # Временная проверка
            await message.answer(
                "Выберите действие из меню:",
                reply_markup=get_two_column_keyboard(is_organizer=is_organizer)
            )
