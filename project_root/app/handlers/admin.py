from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

@router.message(Command("admin"))  # Пример команды для админов
async def admin_command_handler(message: Message):
    await message.answer("Это команда для администраторов.")
