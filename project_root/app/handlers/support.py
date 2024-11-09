# handlers/support.py

import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("support"))
async def support_command_handler(message: Message):
    logger.info(f"Команда /support вызвана пользователем: {message.from_user.username}")
    await message.answer("Вы обратились в службу поддержки. Как мы можем помочь?")
