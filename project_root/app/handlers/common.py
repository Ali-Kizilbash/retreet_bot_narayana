import os
import aiohttp
import logging
from aiogram import Router, types
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from config import Config, validate_config
from app.database.db import async_session
from app.database.crud import register_client
from app.keyboards.client_kb import get_client_type_keyboard, get_two_column_keyboard
from app.keyboards.admin_kb import get_admin_menu
from ..utils.roles import is_staff, OWNER_USERNAME

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Проверка конфигурации
try:
    validate_config()
    logger.info("Конфигурация успешно проверена.")
except EnvironmentError as e:
    logger.error(f"Ошибка конфигурации: {e}")
    exit(1)

router = Router()


async def send_file(callback_query: CallbackQuery, file_path: str, caption: str):
    """Отправляет файл, если он существует."""
    await callback_query.answer()  # Ответ на callback-запрос
    if not os.path.exists(file_path):
        await callback_query.message.answer(f"Файл не найден: {file_path}")
        logger.warning(f"Файл не найден: {file_path}")
    else:
        try:
            file = FSInputFile(file_path)
            await callback_query.bot.send_document(
                chat_id=callback_query.from_user.id,
                document=file,
                caption=caption
            )
            logger.info(f"Файл {file_path} успешно отправлен.")
        except Exception as e:
            logger.error(f"Ошибка при отправке файла {file_path}: {e}")
            await callback_query.message.answer("Произошла ошибка при отправке файла.")

@router.message(Command("start"))
async def start_command(message: Message):
    username = message.from_user.username
    logger.info(f"Команда /start получена от пользователя: {username}")

    # Регистрация пользователя в базе данных
    async with async_session() as session:
        await register_client(
            session,
            user_id=message.from_user.id,
            first_name=message.from_user.first_name or "Без имени",
            last_name=message.from_user.last_name or "Без фамилии",
            client_type="individual"
        )
        logger.info(f"Пользователь {message.from_user.id} зарегистрирован.")

    if username == OWNER_USERNAME:
        await message.answer("Харибол Вениамин! Вот ваша админ панель!", reply_markup=get_admin_menu())
    elif is_staff(f"@{username}"):
        await message.answer("Добро пожаловать, сотрудник! Вот твоя админ панель.", reply_markup=get_admin_menu())
    else:
        await message.answer(Config.WELCOME_MESSAGE)
        await message.answer(
            "Приветствуем! Пожалуйста, выберите, кто вы:",
            reply_markup=get_client_type_keyboard()
        )

@router.callback_query(lambda c: c.data and c.data.startswith("client_type:"))
async def process_client_type(callback_query: CallbackQuery):
    client_type = callback_query.data.split(":")[1]
    logger.info(f"Обработка выбора типа клиента: {client_type}")

    try:
        if client_type == "organizer":
            await callback_query.message.answer(
                "Вы выбрали категорию: Организатор мероприятий.",
                reply_markup=get_two_column_keyboard(is_organizer=True)
            )
        elif client_type == "individual":
            await callback_query.message.answer(
                "Вы выбрали категорию: Индивидуальный клиент.",
                reply_markup=get_two_column_keyboard()
            )
        await callback_query.answer()
    except Exception as e:
        logger.error(f"Ошибка при обработке выбора типа клиента: {e}")

@router.callback_query(lambda c: c.data == "organizer_guide")
async def send_organizer_guide(callback_query: CallbackQuery):
    await send_file(callback_query, Config.EVENT_ORGANIZER_GUIDE_FILE, "Вот предложение для организаторов мероприятий.")

@router.callback_query(lambda c: c.data == "rules")
async def send_rules(callback_query: CallbackQuery):
    await send_file(callback_query, Config.RULES_FILE, "Правила проживания.")

@router.callback_query(lambda c: c.data == "directions")
async def send_directions(callback_query: CallbackQuery):
    await send_file(callback_query, Config.DIRECTIONS_FILE, "Инструкция по прибытии.")

async def get_weather():
    """Получает текущую погоду в Сочи."""
    url = Config.WEATHER_API_URL
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                temp = data["current_weather"]["temperature"]
                windspeed = data["current_weather"]["windspeed"]
                weather_code = data["current_weather"]["weathercode"]
                description = Config.WEATHER_CODES.get(weather_code, "Неизвестная погода")
                return f"Сейчас в Сочи: {temp}°C, {description}, скорость ветра: {windspeed} км/ч."
            return "Не удалось получить данные о погоде."

@router.callback_query(lambda c: c.data == "weather")
async def send_weather(callback_query: CallbackQuery):
    weather_info = await get_weather()
    await callback_query.message.answer(weather_info)
    await callback_query.answer()

async def send_links(callback_query: CallbackQuery, links):
    """Отправляет список ссылок."""
    message_text = "\n".join([f"{link['name']}: [ссылка]({link['url']})" for link in links])
    await callback_query.message.answer(message_text, parse_mode="Markdown")

@router.callback_query(lambda c: c.data == "social_networks")
async def send_social_networks(callback_query: CallbackQuery):
    await send_links(callback_query, Config.LINKS["social_networks"])
    await callback_query.answer()

@router.callback_query(lambda c: c.data == "announcements")
async def send_announcements(callback_query: CallbackQuery):
    await send_links(callback_query, Config.LINKS["announcements"])
    await callback_query.answer()

@router.callback_query(lambda c: c.data == "maps")
async def send_maps(callback_query: CallbackQuery):
    await send_links(callback_query, Config.LINKS["maps"])
    await callback_query.answer()

@router.callback_query(lambda c: c.data == "contact_details")
async def send_contact_details(callback_query: CallbackQuery):
    await send_links(callback_query, Config.LINKS["contact_details"])
    await callback_query.answer()

@router.callback_query(lambda c: c.data == "website")
async def send_website(callback_query: CallbackQuery):
    await send_links(callback_query, Config.LINKS["website"])
    await callback_query.answer()

@router.callback_query(lambda c: c.data == "store")
async def send_store(callback_query: CallbackQuery):
    await send_links(callback_query, Config.LINKS["store"])
    await callback_query.answer()

@router.callback_query(lambda c: c.data == "organizer_chat")
async def send_organizer_chat(callback_query: CallbackQuery):
    await send_links(callback_query, Config.LINKS["organizer_chat"])
    await callback_query.answer()

@router.callback_query(lambda c: c.data == "video")
async def send_video(callback_query: CallbackQuery):
    await send_links(callback_query, Config.LINKS["video"])
    await callback_query.answer()
