from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

@router.message(Command("support"))  # Пример команды для поддержки
async def support_command_handler(message: Message):
    await message.answer("Это команда для поддержки.")
