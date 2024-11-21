import os
import aiohttp
import logging
from aiogram import Router, types 
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command 
from config import Config, validate_config #валидатор конфига
from app.utils.roles import OWNER_USERNAME, is_staff #Проверка на сотрудника
from app.keyboards.admin_kb import get_admin_menu  # Админ-панель
from app.keyboards.client_kb import get_two_column_keyboard, get_client_type_keyboard #Клавиатуры
from app.database.crud import get_client_by_user_id, register_client, update_client_type #CRUD
from sqlalchemy.ext.asyncio import AsyncSession

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Проверяем наличие необходимых переменных окружения
try:
    validate_config()
    print("Конфигурация успешно проверена.")
except EnvironmentError as e:
    print(f"Ошибка конфигурации: {e}")
    exit(1)

router = Router()


def load_text(file_path):
    """Загружает текст из указанного файла."""
    if not os.path.exists(file_path):
        logger.warning(f"Файл {file_path} не найден.")
        return "Файл не найден."
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        logger.error(f"Ошибка при загрузке текста из {file_path}: {e}")
        return "Ошибка при загрузке файла."


@router.message(Command("start"))
async def start_command(message: Message, session: AsyncSession):
    """Обработчик команды /start. Регистрирует нового клиента или приветствует существующего."""
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name or ""

    logger.info(f"Команда /start от пользователя: {username} (ID: {user_id})")

    # Проверка, является ли пользователь сотрудником
    if is_staff(user_id=user_id, username=f"@{username}" if username else None):
        if username == OWNER_USERNAME:
            await message.answer("Харибол, многоуважаемый Вениамин! Добро пожаловать в ваш бот клиентской поддержки.")
        else:
            await message.answer("Добро пожаловать, сотрудник! Вот ваша админ-панель.")
        await message.answer("Выберите действие:", reply_markup=get_admin_menu())
        return

    # Проверяем в базе данных, зарегистрирован ли клиент
    client = await get_client_by_user_id(session, user_id)

    if client:
        # Если клиент уже зарегистрирован
        await message.answer(Config.ALREADY_REGISTERED_MESSAGE)
        await message.answer("Выберите действие из меню:", reply_markup=get_two_column_keyboard())
    else:
        # Регистрируем нового клиента
        await register_client(session, user_id, first_name, last_name, client_type=None)
        await message.answer(Config.WELCOME_MESSAGE)
        await message.answer(
            "Приветствуем! Пожалуйста, выберите, кто вы:",
            reply_markup=get_client_type_keyboard()
        )


@router.callback_query(lambda c: c.data and c.data.startswith("client_type:"))
async def process_client_type(callback_query: CallbackQuery, session: AsyncSession):
    """Обработка выбора типа клиента."""
    client_type = callback_query.data.split(":")[1]
    user_id = callback_query.from_user.id
    logger.info(f"Пользователь выбрал тип клиента: {client_type}")

    try:
        # Обновляем тип клиента в базе данных
        await update_client_type(session, user_id, client_type)

        # Показываем меню в зависимости от выбранного типа
        if client_type == "organizer":
            await callback_query.message.answer(
                "Вы выбрали категорию: Организатор мероприятий."
            )
            await callback_query.message.answer(
                "Пожалуйста, выберите действие из меню:",
                reply_markup=get_two_column_keyboard(is_organizer=True)
            )
        elif client_type == "individual":
            await callback_query.message.answer(
                "Вы выбрали категорию: Индивидуальный клиент."
            )
            await callback_query.message.answer(
                "Пожалуйста, выберите действие из меню:",
                reply_markup=get_two_column_keyboard()
            )
        await callback_query.answer()
    except Exception as e:
        logger.error(f"Ошибка при обработке выбора типа клиента: {e}")
        await callback_query.message.answer("Произошла ошибка. Попробуйте снова.")


@router.message(Command("menu"))
async def show_main_menu(message: Message, session: AsyncSession):
    """Обработчик команды /menu. Показывает меню в зависимости от роли пользователя."""
    user_id = message.from_user.id
    username = message.from_user.username

    # Если пользователь сотрудник, показываем админ-панель
    if is_staff(user_id=user_id, username=f"@{username}" if username else None):
        await message.answer("Админ-панель:", reply_markup=get_admin_menu())
        return

    # Проверяем тип клиента в базе данных
    client = await get_client_by_user_id(session, user_id)

    if not client:
        # Если клиент не найден в базе данных, предлагаем выбрать тип
        await message.answer("Выберите, кто вы:", reply_markup=get_client_type_keyboard())
        return

    # Показываем соответствующее меню
    if client.client_type == "organizer":
        await message.answer(
            "Меню организатора:", reply_markup=get_two_column_keyboard(is_organizer=True)
        )
    elif client.client_type == "individual":
        await message.answer(
            "Меню индивидуального клиента:", reply_markup=get_two_column_keyboard()
        )


@router.callback_query(lambda c: c.data == "weather")
async def send_weather(callback_query: CallbackQuery):
    """Отправка текущей погоды в Сочи."""
    weather_info = await get_weather()
    await callback_query.answer()
    await callback_query.message.answer(weather_info)


async def get_weather():
    """Получение текущей погоды в Сочи."""
    url = Config.WEATHER_API_URL
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                temp = data["current_weather"]["temperature"]
                windspeed = data["current_weather"]["windspeed"]
                weather_code = data["current_weather"]["weathercode"]
                weather_description_ru = Config.WEATHER_CODES.get(weather_code, "Неизвестная погода")
                return f"Сейчас в Сочи: {temp}°C, {weather_description_ru}, скорость ветра: {windspeed} км/ч."
            return "Не удалось получить данные о погоде. Попробуйте позже."
