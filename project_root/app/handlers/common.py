from aiogram import Router, types
from config import Config
from app.database.crud import user_is_registered, register_user  # Импортируем функции
from app.database.db import get_async_session  # Функция для получения сессии базы данных

router = Router()

@router.message(commands=["start"])
async def start_command(message: types.Message):
    async with get_async_session() as session:
        # Проверяем, зарегистрирован ли пользователь
        if await user_is_registered(message.from_user.id, session):
            await message.answer(Config.ALREADY_REGISTERED_MESSAGE)
        else:
            await message.answer(Config.WELCOME_MESSAGE)
            await register_user(message.from_user.id, session)
