import os
import aiohttp
import logging
from aiogram import Router, types, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from config import Config, validate_config
from app.database.crud import user_is_registered, register_user
from app.database.db import get_async_session
from app.keyboards.client_kb import get_client_type_keyboard, get_two_column_keyboard
from app.keyboards.admin_kb import get_admin_menu
from app.keyboards.set_commands import set_bot_commands

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
STAFF_USERNAMES_FILE = os.path.join("resources", "staff_usernames.txt")
OWNER_USERNAME = "@Veniamin_tk"


def is_staff(username: str) -> bool:
    """Проверяет, является ли пользователь сотрудником, сверяя его username с файлом staff_usernames.txt."""
    print(f"Проверка на сотрудника для username: {username}")
    if not os.path.exists(STAFF_USERNAMES_FILE):
        print(f"Файл {STAFF_USERNAMES_FILE} не найден.")
        return False

    try:
        with open(STAFF_USERNAMES_FILE, "r") as f:
            staff_usernames = f.read().splitlines()
            print(f"Загруженные сотрудники: {staff_usernames}")
            return username in staff_usernames or username == OWNER_USERNAME
    except FileNotFoundError:
        print(f"Файл {STAFF_USERNAMES_FILE} не найден.")
        return False


def load_text(file_path):
    """Загружает текст из указанного файла."""
    print(f"Загрузка текста из файла: {file_path}")
    if not os.path.exists(file_path):
        print(f"Файл {file_path} не найден.")
        return "Файл не найден."
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            print(f"Текст из {file_path} загружен успешно.")
            return content
    except Exception as e:
        print(f"Ошибка при загрузке текста из {file_path}: {e}")
        return "Ошибка при загрузке файла."


@router.message(Command("start"))
async def start_command(message: Message, bot: Bot):
    username = message.from_user.username
    user_id = message.from_user.id
    print(f"Команда /start получена от пользователя: {username} (user_id: {user_id})")

    is_admin = False  # Флаг для проверки прав пользователя

    if username == OWNER_USERNAME:
        print("Показываем админ-панель владельцу.")
        await message.answer("Харибол, многоуважаемый Вениамин! Добро пожаловать в ваш бот клиентской поддержки.")
        await message.answer("Вот ваша админ-панель:", reply_markup=get_admin_menu())
        is_admin = True
    elif username and is_staff(f"@{username}"):
        print("Показываем админ-панель сотруднику.")
        await message.answer("Добро пожаловать, сотрудник! Вот ваша админ-панель.")
        await message.answer("Выберите действие:", reply_markup=get_admin_menu())
        is_admin = True
    else:
        await message.answer(Config.WELCOME_MESSAGE)
        await message.answer(
            "Приветствуем! Пожалуйста, выберите, кто вы:",
            reply_markup=get_client_type_keyboard()
        )

    # Устанавливаем команды только для текущего пользователя
    await set_bot_commands(bot, is_admin=is_admin, user_id=user_id)


@router.callback_query(lambda c: c.data and c.data.startswith("client_type:"))
async def process_client_type(callback_query: CallbackQuery):
    client_type = callback_query.data.split(":")[1]
    logger.info(f"Обработка выбора типа клиента: {client_type}")

    try:
        if client_type == "organizer":
            logger.info("Пользователь выбрал категорию: Организатор мероприятий.")
            await callback_query.message.answer(
                "Вы выбрали категорию: Организатор мероприятий."
            )
            await callback_query.message.answer(
                "Пожалуйста, выберите нужное меню:",
                reply_markup=get_two_column_keyboard(is_organizer=True)  # Меню с доп. кнопками для организаторов
            )
        elif client_type == "individual":
            logger.info("Пользователь выбрал категорию: Индивидуальный клиент.")
            await callback_query.message.answer(
                "Вы выбрали категорию: Индивидуальный клиент."
            )
            await callback_query.message.answer(
                "Пожалуйста, выберите нужное меню:",
                reply_markup=get_two_column_keyboard()  # Меню для индивидуальных клиентов
            )

        await callback_query.answer()  # Закрываем всплывающее уведомление
        logger.info("Выбор типа клиента обработан успешно.")
    except Exception as e:
        logger.error(f"Ошибка при обработке выбора типа клиента: {e}")



@router.callback_query(lambda c: c.data == "organizer_guide")
async def send_organizer_guide(callback_query: CallbackQuery):
    # Немедленно отвечаем на callback-запрос
    await callback_query.answer()

    pdf_path = os.path.abspath(Config.EVENT_ORGANIZER_GUIDE_FILE)
    logger.info(f"Путь к PDF-файлу: {pdf_path}")

    if not os.path.exists(pdf_path):
        await callback_query.message.answer("Предложение для организаторов не найдено.")
        logger.warning(f"Файл не найден по пути: {pdf_path}")
    else:
        try:
            # Используем FSInputFile для отправки файла из файловой системы
            pdf_file = FSInputFile(pdf_path)
            await callback_query.bot.send_document(
                chat_id=callback_query.from_user.id,
                document=pdf_file,
                caption="Вот предложение для организаторов мероприятий. Ознакомьтесь с условиями.")

            logger.info("Файл успешно отправлен.")
        except Exception as e:
            logger.error(f"Ошибка при отправке руководства организатора: {e}")
            await callback_query.message.answer("Произошла ошибка при отправке руководства организатора.")



@router.callback_query(lambda c: c.data == "rules")
async def send_rules(callback_query: CallbackQuery):
    rules_text = load_text("resources/rules.txt")  # Загружаем текст правил проживания
    print("Отправка правил проживания.")
    try:
        await callback_query.message.answer(rules_text)
        await callback_query.answer()
        print("Правила проживания успешно отправлены.")
    except Exception as e:
        print(f"Ошибка при отправке правил проживания: {e}")


@router.callback_query(lambda c: c.data == "directions")
async def send_directions(callback_query: CallbackQuery):
    directions_text = load_text("resources/directions.txt")  # Загружаем текст с инструкцией по прибытии
    print("Отправка инструкции по прибытии.")
    try:
        await callback_query.message.answer(directions_text)
        await callback_query.answer()
        print("Инструкция по прибытии успешно отправлена.")
    except Exception as e:
        print(f"Ошибка при отправке инструкции по прибытии: {e}")


# Функция для получения погоды
async def get_weather():
    url = Config.WEATHER_API_URL
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                
                # Получаем необходимые данные
                temp = data["current_weather"]["temperature"]
                windspeed = data["current_weather"]["windspeed"]
                weather_code = data["current_weather"]["weathercode"]

                # Преобразуем weathercode в описание на русском
                weather_description_ru = Config.WEATHER_CODES.get(weather_code, "Неизвестная погода")

                return f"Сейчас в Сочи: {temp}°C, {weather_description_ru}, скорость ветра: {windspeed} км/ч."
            else:
                return "Не удалось получить данные о погоде. Попробуйте позже."


# Обработчик для кнопки "Узнать погоду"
@router.callback_query(lambda c: c.data == "weather")
async def send_weather(callback_query: CallbackQuery):
    await callback_query.answer()  # Немедленно отвечаем на callback-запрос
    weather_info = await get_weather()
    await callback_query.message.answer(weather_info)


async def send_links(callback_query: CallbackQuery, links):
    """Отправка списка ссылок."""
    message_text = ""
    for link in links:
        message_text += f"{link['name']}: [ссылка]({link['url']})\n"
    
    await callback_query.message.answer(message_text, parse_mode="Markdown")

@router.callback_query(lambda c: c.data == "social_networks")
async def send_social_networks(callback_query: CallbackQuery):
    await callback_query.answer()
    await send_links(callback_query, Config.LINKS["social_networks"])

@router.callback_query(lambda c: c.data == "announcements")
async def send_announcements(callback_query: CallbackQuery):
    await callback_query.answer()
    await send_links(callback_query, Config.LINKS["announcements"])

@router.callback_query(lambda c: c.data == "maps")
async def send_maps(callback_query: CallbackQuery):
    await callback_query.answer()
    await send_links(callback_query, Config.LINKS["maps"])

async def send_contact_details_from_config(callback_query: CallbackQuery):
    """Отправляет контакты из Config.LINKS['contact_details'], включая текстовые и ссылочные данные."""
    contact_details = Config.LINKS["contact_details"]
    message_text = "Наши контакты:\n\n"

    for contact in contact_details:
        if "name" in contact and "url" in contact:
            # Если это ссылка
            message_text += f"{contact['name']}: [ссылка]({contact['url']})\n"
        elif "text" in contact:
            # Если это текст
            message_text += f"{contact['text']}\n"

    await callback_query.message.answer(message_text, parse_mode="Markdown")

@router.callback_query(lambda c: c.data == "contact_details")
async def send_contact_details(callback_query: CallbackQuery):
    """Обрабатывает отправку контактных данных."""
    await callback_query.answer()  # Немедленно отвечаем на callback-запрос
    await send_contact_details_from_config(callback_query)


@router.callback_query(lambda c: c.data == "website")
async def send_website(callback_query: CallbackQuery):
    await callback_query.answer()
    await send_links(callback_query, Config.LINKS["website"])

@router.callback_query(lambda c: c.data == "store")
async def send_store(callback_query: CallbackQuery):
    await callback_query.answer()
    await send_links(callback_query, Config.LINKS["store"])

@router.callback_query(lambda c: c.data == "organizer_chat")
async def send_organizer_chat(callback_query: CallbackQuery):
    await callback_query.answer()
    await send_links(callback_query, Config.LINKS["organizer_chat"])

@router.callback_query(lambda c: c.data == "video")
async def send_video(callback_query: CallbackQuery):
    await callback_query.answer()
    await send_links(callback_query, Config.LINKS["video"])

@router.callback_query(lambda c: c.data == "rules")
async def send_rules(callback_query: CallbackQuery):
    rules_text = load_text(Config.RULES_FILE)
    await callback_query.answer()
    await callback_query.message.answer(rules_text)

@router.callback_query(lambda c: c.data == "directions")
async def send_directions(callback_query: CallbackQuery):
    directions_text = load_text(Config.DIRECTIONS_FILE)
    await callback_query.answer()
    await callback_query.message.answer(directions_text)

@router.callback_query(lambda c: c.data == "organizer_guide")
async def send_organizer_guide(callback_query: CallbackQuery):
    await callback_query.answer()  # Немедленно отвечаем на callback-запрос

    pdf_path = Config.EVENT_ORGANIZER_GUIDE_FILE
    if not os.path.exists(pdf_path):
        await callback_query.message.answer("Предложение для организаторов не найдено.")
    else:
        pdf_file = FSInputFile(pdf_path)
        await callback_query.bot.send_document(
            chat_id=callback_query.from_user.id,
            document=pdf_file,
            caption="Вот предложение для организаторов мероприятий. Ознакомьтесь с условиями."
        )