from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import Message, Document, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.database.crud import get_client_by_user_id, update_client_type
from app.database.db import async_session
import logging

router = Router()
logger = logging.getLogger(__name__)

SUPPORT_CHAT_ID = -1002319130163  # Убедитесь, что это правильный ID вашей группы поддержки

# Список допустимых расширений для документов
allowed_extensions = {"pdf", "epub", "fb2", "txt"}


# Определение состояния
class SupportStates(StatesGroup):
    waiting_for_question = State()
    waiting_for_reply = State()  # Состояние для ожидания ответа менеджера

@router.message(Command("manager"))
async def manager_command_handler(message: Message, state: FSMContext):
    """Запрашивает вопрос у пользователя, переходя в состояние ожидания."""
    logger.info(f"Команда /manager вызвана пользователем: {message.from_user.username}")
    await message.answer("Вы обратились в службу поддержки. Пожалуйста, опишите свою проблему, и мы ответим вам в ближайшее время.")
    await state.set_state(SupportStates.waiting_for_question)

@router.message(SupportStates.waiting_for_question, F.content_type == types.ContentType.TEXT)
async def receive_support_question(message: Message, state: FSMContext):
    """Получает вопрос от пользователя и пересылает его в чат поддержки с кнопкой для ответа."""
    user_id = message.from_user.id
    username = message.from_user.username or "Без имени"
    question = message.text

    # Создаем кнопку для быстрого ответа
    reply_button = InlineKeyboardButton(text="Ответить", callback_data=f"reply_to:{user_id}")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[reply_button]])

    # Пересылаем вопрос в группу поддержки
    await message.bot.send_message(
        SUPPORT_CHAT_ID,
        f"Вопрос от @{username} ({user_id}):\n{question}",
        reply_markup=keyboard
    )

    # Подтверждаем отправку и сбрасываем состояние
    await message.answer("Ваш вопрос был отправлен в службу поддержки. Ожидайте ответа.")
    await state.clear()

@router.message(SupportStates.waiting_for_question, F.content_type == types.ContentType.DOCUMENT)
async def forward_document_to_support(message: Message, state: FSMContext):
    """Пересылает документ от клиента в чат поддержки, если бот находится в состоянии ожидания вопроса."""
    document: Document = message.document
    file_extension = document.file_name.split(".")[-1].lower()

    if file_extension not in allowed_extensions:
        await message.answer("Этот формат файла не поддерживается. Пожалуйста, отправьте PDF, EPUB, FB2 или TXT файл.")
        return

    user_id = message.from_user.id
    username = message.from_user.username or "Без имени"
    support_text = f"Документ от пользователя @{username} ({user_id}):"

    # Создаем кнопку для быстрого ответа
    reply_button = InlineKeyboardButton(text="Ответить", callback_data=f"reply_to:{user_id}")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[reply_button]])

    # Пересылаем документ в группу поддержки
    await message.bot.send_document(SUPPORT_CHAT_ID, document=document.file_id, caption=support_text, reply_markup=keyboard)
    await message.answer("Ваш документ был отправлен в поддержку.")
    await state.clear()

@router.callback_query(lambda c: c.data and c.data.startswith("reply_to:"))
async def prompt_reply(callback_query: CallbackQuery, state: FSMContext):
    """Обработчик для нажатия кнопки 'Ответить' менеджером."""
    user_id = int(callback_query.data.split(":")[1])

    # Сохраняем user_id в состояние FSM для последующего использования в ответе
    await state.update_data(reply_to_user_id=user_id)

    # Уведомляем менеджера о возможности отправки ответа
    await callback_query.message.answer(
        f"Введите ответ для пользователя {user_id}. Просто отправьте текст или документ, и он будет автоматически переслан клиенту.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Отмена", callback_data=f"cancel_reply:{user_id}")]]
        )
    )
    await state.set_state(SupportStates.waiting_for_reply)  # Устанавливаем состояние ожидания ответа
    await callback_query.answer()  # Завершаем callback_query ответ

@router.message(SupportStates.waiting_for_reply, F.content_type == types.ContentType.TEXT)
async def send_reply_to_client(message: Message, state: FSMContext):
    """Отправка текстового ответа клиенту от менеджера."""
    data = await state.get_data()
    user_id = data.get("reply_to_user_id")

    if not user_id:
        await message.answer("Ошибка: Не найден пользователь для ответа.")
        return

    # Отправляем ответ клиенту
    await message.bot.send_message(user_id, f"Ответ от поддержки: {message.text}")
    await message.answer("Ваш ответ был отправлен клиенту.")

    # Сброс состояния
    await state.clear()

@router.message(SupportStates.waiting_for_reply, F.content_type == types.ContentType.DOCUMENT)
async def send_document_reply_to_client(message: Message, state: FSMContext):
    """Отправка документа клиенту от менеджера."""
    data = await state.get_data()
    user_id = data.get("reply_to_user_id")

    if not user_id:
        await message.answer("Ошибка: Не найден пользователь для ответа.")
        return

    # Пересылаем документ клиенту
    await message.bot.send_document(user_id, message.document.file_id, caption="Ответ от поддержки")
    await message.answer("Ваш документ был отправлен клиенту.")

    # Сброс состояния
    await state.clear()

@router.callback_query(lambda c: c.data and c.data.startswith("cancel_reply:"))
async def cancel_reply(callback_query: CallbackQuery, state: FSMContext):
    """Отмена отправки ответа клиенту."""
    await state.clear()
    await callback_query.message.answer("Ответ был отменен.")
    await callback_query.answer()


class EditClientStates(StatesGroup):
    waiting_for_client_id = State()
    waiting_for_new_type = State()

@router.message(EditClientStates.waiting_for_client_id)
async def process_client_id(message: Message, state: FSMContext):
    async with async_session() as session:
        client = await get_client_by_user_id(session, int(message.text))
        if client:
            await state.update_data(client_id=client.id)
            await message.answer("Введите новый тип клиента (organizer, individual):")
            await state.set_state(EditClientStates.waiting_for_new_type)
        else:
            await message.answer("Клиент не найден. Попробуйте еще раз.")

@router.message(EditClientStates.waiting_for_new_type)
async def process_new_type(message: Message, state: FSMContext):
    data = await state.get_data()
    client_id = data.get("client_id")
    new_type = message.text

    async with async_session() as session:
        await update_client_type(session, client_id, new_type)
        await message.answer(f"Тип клиента успешно обновлен на {new_type}.")
        await state.clear()
