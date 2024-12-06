# broadcast.py

import os
import logging
from aiogram import Router, types, F, Bot
from aiogram.types import Message, Document, CallbackQuery, ContentType
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from app.keyboards.admin_kb import get_broadcast_client_type_menu
from app.handlers.common import is_staff  # Функция проверки прав администратора
from app.database.db import get_async_session
from app.database.models import User
from sqlalchemy.future import select

router = Router()
logger = logging.getLogger(__name__)

class BroadcastStates(StatesGroup):
    waiting_for_client_type = State()
    waiting_for_message_or_document = State()
    waiting_for_confirmation = State()

@router.message(Command("broadcast"))
async def start_broadcast(message: Message, state: FSMContext):
    """Начало процесса рассылки сообщений через команду /broadcast."""
    user_id = message.from_user.id
    username = message.from_user.username or "Без имени"
    logger.info(f"Команда /broadcast получена от пользователя: user_id={user_id}, username={username}")

    if not is_staff(user_id=user_id, username=username):
        logger.warning(f"Пользователь {user_id} ({username}) попытался использовать /broadcast без прав.")
        await message.answer("У вас нет прав для выполнения этой команды.")
        return

    try:
        await message.answer("Выберите категорию клиентов для рассылки:", reply_markup=get_broadcast_client_type_menu())
        await state.set_state(BroadcastStates.waiting_for_client_type)
        logger.info("Меню выбора категории клиентов для рассылки успешно отображено.")
    except Exception as e:
        logger.error(f"Ошибка при отображении меню рассылки: {e}")
        await message.answer("Произошла ошибка при отображении меню рассылки.")

@router.callback_query(lambda c: c.data == "broadcast_select_client_type")
async def handle_broadcast_select_client_type(callback_query: CallbackQuery, state: FSMContext):
    """Обработка нажатия кнопки 'Запустить рассылку' в админ-панели."""
    try:
        await callback_query.message.answer("Выберите категорию клиентов для рассылки:", reply_markup=get_broadcast_client_type_menu())
        await state.set_state(BroadcastStates.waiting_for_client_type)
        await callback_query.answer()
        logger.info("Меню выбора категории клиентов для рассылки успешно отображено через кнопку.")
    except Exception as e:
        logger.error(f"Ошибка при отображении меню рассылки: {e}")
        await callback_query.message.answer("Произошла ошибка при отображении меню рассылки.")
        await callback_query.answer()

@router.callback_query(BroadcastStates.waiting_for_client_type)
async def select_client_type(callback_query: CallbackQuery, state: FSMContext):
    """Обработка выбора категории клиентов для рассылки."""
    broadcast_client_type = callback_query.data
    logger.info(f"Тип клиентов для рассылки установлен: {broadcast_client_type}")

    # Преобразуем callback_data в тип клиента, если необходимо
    # Например, "broadcast_individual" -> "individual"
    if broadcast_client_type.startswith("broadcast_"):
        broadcast_client_type = broadcast_client_type.replace("broadcast_", "")

    await state.update_data(broadcast_client_type=broadcast_client_type)
    await callback_query.message.answer("Пожалуйста, отправьте сообщение или документ для рассылки.")
    await state.set_state(BroadcastStates.waiting_for_message_or_document)
    await callback_query.answer()

@router.message(
    BroadcastStates.waiting_for_message_or_document,
    F.content_type.in_([ContentType.TEXT, ContentType.DOCUMENT, ContentType.PHOTO])
)
async def handle_broadcast_message(message: Message, state: FSMContext):
    """Обработка сообщения или документа для рассылки."""
    data = await state.get_data()
    broadcast_client_type = data.get("broadcast_client_type")

    if not broadcast_client_type:
        await message.answer("Пожалуйста, сначала выберите категорию клиентов для рассылки.")
        logger.warning("Рассылка начата без выбора категории клиентов.")
        return

    # Получение списка клиентов из базы данных
    client_ids = []
    try:
        session = await get_async_session()
        async with session:
            result = await session.execute(
                select(User).where(User.client_type == broadcast_client_type)
            )
            all_users = result.scalars().all()

            for user in all_users:
                if not is_staff(user_id=user.id, username=user.username):
                    client_ids.append(user.id)
    except Exception as e:
        logger.error(f"Ошибка при получении списка клиентов: {e}")
        await message.answer("Произошла ошибка при подготовке рассылки. Попробуйте позже.")
        await state.clear()
        return

    if not client_ids:
        await message.answer("Нет клиентов для рассылки.")
        await state.clear()
        logger.info("Нет клиентов для рассылки.")
        return

    # Сохранение информации о рассылке в состоянии
    await state.update_data(
        message_to_broadcast=message,
        client_ids=client_ids
    )

    await message.answer(f"Сообщение готово к отправке {len(client_ids)} пользователям. Отправить?", reply_markup=get_confirmation_keyboard())
    await state.set_state(BroadcastStates.waiting_for_confirmation)
    logger.info(f"Готовность к рассылке сообщений {len(client_ids)} пользователям.")

def get_confirmation_keyboard():
    """Клавиатура с кнопками подтверждения и отмены."""
    buttons = [
        [types.InlineKeyboardButton(text="✅ Отправить", callback_data="confirm_broadcast")],
        [types.InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_broadcast")]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)

@router.callback_query(BroadcastStates.waiting_for_confirmation, lambda c: c.data == "confirm_broadcast")
async def confirm_broadcast(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    """Подтверждение и отправка рассылки."""
    data = await state.get_data()
    message_to_broadcast: Message = data.get("message_to_broadcast")
    client_ids = data.get("client_ids", [])

    try:
        await callback_query.message.answer("Начинаю рассылку...")
        await callback_query.answer()

        success_count = 0
        failure_count = 0

        for user_id in client_ids:
            try:
                if message_to_broadcast.content_type == ContentType.TEXT:
                    await bot.send_message(chat_id=user_id, text=message_to_broadcast.text)
                elif message_to_broadcast.content_type == ContentType.DOCUMENT:
                    await bot.send_document(chat_id=user_id, document=message_to_broadcast.document.file_id, caption=message_to_broadcast.caption)
                elif message_to_broadcast.content_type == ContentType.PHOTO:
                    await bot.send_photo(chat_id=user_id, photo=message_to_broadcast.photo[-1].file_id, caption=message_to_broadcast.caption)
                success_count += 1
            except Exception as e:
                logger.error(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
                failure_count += 1

        await callback_query.message.answer(f"Рассылка завершена. Успешно: {success_count}, Ошибок: {failure_count}.")
        await state.clear()
        logger.info(f"Рассылка завершена. Успешно: {success_count}, Ошибок: {failure_count}.")
    except Exception as e:
        logger.error(f"Ошибка при отправке рассылки: {e}")
        await callback_query.message.answer("Произошла ошибка при отправке рассылки.")
    finally:
        await callback_query.answer()

@router.callback_query(BroadcastStates.waiting_for_confirmation, lambda c: c.data == "cancel_broadcast")
async def cancel_broadcast(callback_query: CallbackQuery, state: FSMContext):
    """Отмена рассылки."""
    try:
        await callback_query.message.answer("Рассылка отменена.")
        await state.clear()
        await callback_query.answer()
        logger.info("Рассылка отменена пользователем.")
    except Exception as e:
        logger.error(f"Ошибка при отмене рассылки: {e}")
        await callback_query.message.answer("Произошла ошибка при отмене рассылки.")
        await callback_query.answer()
