from aiogram import Router #client.py
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

@router.message(Command("help"))  # Пример обработчика команды /help
async def help_command_handler(message: Message):
    await message.answer("Это команда /help.")
