from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from config import Config
from app.keyboards.client_kb import get_two_column_keyboard


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
    """Обработчик для команды /menu, отправляет главное меню."""
    await message.answer("Выберите действие из меню:",
                         reply_markup=get_two_column_keyboard())