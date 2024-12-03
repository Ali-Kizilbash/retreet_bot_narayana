# broadcast.py

import os
from aiogram import Router, types, F
from aiogram.types import Message, Document, CallbackQuery
from aiogram.filters import Command
from config import Config
from app.handlers.common import is_staff
from app.database.db import get_async_session
from sqlalchemy.future import select
from app.database.models import User
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from app.keyboards.admin_kb import get_broadcast_client_type_menu  # Убедитесь, что импорт корректен

import logging

router = Router()
logger = logging.getLogger(__name__)

# Допустимые расширения для документов
ALLOWED_EXTENSIONS = {"txt", "doc", "pdf", "epub", "fb2"}


# Состояния для FSM
class BroadcastStates(StatesGroup):
    waiting_for_client_type = State()
    waiting_for_message_or_document = State()


@router.callback_query(lambda c: c.data == "broadcast_select_client_type")
async def broadcast_select_client_type(callback_query: CallbackQuery, state: FSMContext):
    """
    Начало процесса рассылки: выбор категории клиентов.
    """
    await state.set_state(BroadcastStates.waiting_for_client_type)
    await callback_query.message.answer(
        "Выберите категорию клиентов для рассылки:",
        reply_markup=get_broadcast_client_type_menu()
    )
    await callback_query.answer()
    logger.info("Меню выбора категории клиентов для рассылки успешно отображено.")


@router.callback_query(lambda c: c.data in ["broadcast_individual", "broadcast_organizer"])
async def handle_client_type_selection(callback_query: CallbackQuery, state: FSMContext):
    """
    Обработчик выбора типа клиентов для рассылки.
    """
    selected_type = "individual" if callback_query.data == "broadcast_individual" else "organizer"
    await state.update_data(broadcast_client_type=selected_type)

    await callback_query.message.answer(
        f"Вы выбрали категорию: {'Индивидуальные клиенты' if selected_type == 'individual' else 'Организаторы мероприятий'}.\n"
        "Теперь отправьте текст или документ для рассылки."
    )
    await state.set_state(BroadcastStates.waiting_for_message_or_document)
    await callback_query.answer()
    logger.info(f"Тип клиентов для рассылки установлен: {selected_type}")


@router.message(Command("broadcast"))
async def broadcast_command_handler(message: Message, state: FSMContext):
    """
    Команда для начала рассылки, доступна только сотрудникам или владельцу.
    """
    user_id = message.from_user.id
    username = f"@{message.from_user.username}" if message.from_user.username else ""

    if not is_staff(user_id=user_id, username=username):
        await message.answer("У вас нет прав на выполнение этой команды.")
        logger.warning(f"Пользователь {user_id} ({username}) попытался начать рассылку без прав.")
        return

    await state.set_state(BroadcastStates.waiting_for_client_type)
    await message.answer(
        "Пожалуйста, выберите категорию клиентов для рассылки:",
        reply_markup=get_broadcast_client_type_menu()
    )
    logger.info(f"Пользователь {user_id} ({username}) начал процесс рассылки.")


@router.message(BroadcastStates.waiting_for_message_or_document, F.content_type.in_([types.ContentType.TEXT, types.ContentType.DOCUMENT]))
async def handle_broadcast(message: Message, state: FSMContext):
    """
    Обработчик для рассылки текстов и/или документов.
    """
    data = await state.get_data()
    broadcast_client_type = data.get("broadcast_client_type")

    if not broadcast_client_type:
        await message.answer("Пожалуйста, сначала выберите категорию клиентов для рассылки.")
        logger.warning("Рассылка начата без выбора категории клиентов.")
        return

    # Получение списка клиентов из базы данных
    client_ids = []
    try:
        async with get_async_session() as session:
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
        return

    if not client_ids:
        await message.answer("Нет клиентов для рассылки.")
        await state.clear()
        logger.info("Нет клиентов для рассылки.")
        return

    # Рассылка
    if message.content_type == types.ContentType.TEXT:
        text = message.text
        await message.answer("Начинаю рассылку текстового сообщения...")
        logger.info("Начало рассылки текстового сообщения.")
        for client_id in client_ids:
            try:
                await message.bot.send_message(client_id, text)
                logger.info(f"Текстовое сообщение отправлено пользователю {client_id}")
            except Exception as e:
                logger.error(f"Не удалось отправить текст пользователю {client_id}: {e}")
    elif message.content_type == types.ContentType.DOCUMENT:
        document: Document = message.document
        if document.file_name.split(".")[-1].lower() not in ALLOWED_EXTENSIONS:
            await message.answer("Этот формат файла не поддерживается.")
            logger.warning(f"Пользователь {message.from_user.id} попытался отправить неподдерживаемый файл: {document.file_name}")
            return
        await message.answer("Начинаю рассылку документа...")
        logger.info("Начало рассылки документа.")
        for client_id in client_ids:
            try:
                await message.bot.send_document(client_id, document.file_id, caption="Документ для вас")
                logger.info(f"Документ {document.file_name} отправлен пользователю {client_id}")
            except Exception as e:
                logger.error(f"Не удалось отправить документ пользователю {client_id}: {e}")

    await message.answer("Рассылка завершена.")
    await state.clear()
    logger.info("Рассылка завершена.")
