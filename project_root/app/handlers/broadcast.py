from aiogram import Router, types, F
from aiogram.types import Message, Document
from aiogram.filters import Command
import logging

router = Router()
logger = logging.getLogger(__name__)

# Тестовый список клиентов для рассылки (позже заменить на запрос из базы данных)
TEST_CLIENT_IDS = [1975738954, 309106647, 615756708]

# Допустимые расширения для документов
ALLOWED_EXTENSIONS = {"txt", "doc", "pdf", "epub", "fb2"}

@router.message(Command("broadcast"))
async def broadcast_command_handler(message: Message):
    """Команда для начала рассылки, запрашивает текст или документ для рассылки."""
    await message.answer("Пожалуйста, отправьте текстовое сообщение и/или документ для рассылки.")

@router.message(F.content_type.in_([types.ContentType.TEXT, types.ContentType.DOCUMENT]))
async def handle_broadcast(message: Message):
    """Обработчик для рассылки текстов и/или документов."""
    
    # Проверка и рассылка текстового сообщения
    if message.content_type == types.ContentType.TEXT:
        text = message.text
        await message.answer("Начинаю рассылку текстового сообщения...")
        for user_id in TEST_CLIENT_IDS:
            try:
                await message.bot.send_message(user_id, text)
                logger.info(f"Текстовое сообщение отправлено пользователю {user_id}")
            except Exception as e:
                logger.error(f"Не удалось отправить текст пользователю {user_id}: {e}")

    # Проверка и рассылка документа
    if message.content_type == types.ContentType.DOCUMENT:
        document: Document = message.document
        file_extension = document.file_name.split(".")[-1].lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            await message.answer("Этот формат файла не поддерживается. Допустимые форматы: txt, doc, pdf, epub, fb2.")
            return

        await message.answer("Начинаю рассылку документа...")
        for user_id in TEST_CLIENT_IDS:
            try:
                await message.bot.send_document(user_id, document.file_id, caption="Документ для вас")
                logger.info(f"Документ {document.file_name} отправлен пользователю {user_id}")
            except Exception as e:
                logger.error(f"Не удалось отправить документ пользователю {user_id}: {e}")

    # Если ни текст, ни документ не были отправлены, информируем об этом
    if message.content_type not in [types.ContentType.TEXT, types.ContentType.DOCUMENT]:
        await message.answer("Пожалуйста, отправьте либо текст, либо документ для рассылки.")

    await message.answer("Рассылка завершена.")