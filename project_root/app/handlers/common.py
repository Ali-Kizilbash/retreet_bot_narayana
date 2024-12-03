import os
import aiohttp
import logging
from aiogram import Router, types, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from config import Config, validate_config
from app.keyboards.client_kb import get_client_type_keyboard, get_two_column_keyboard
from app.keyboards.admin_kb import get_admin_menu
from app.keyboards.set_commands import set_bot_commands
from aiogram.fsm.context import FSMContext
from app.database.crud import add_user, update_user_type, user_is_registered
from app.database.db import get_async_session
from sqlalchemy.future import select
from app.database.models import User


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


def is_staff(user_id: int = None, username: str = None) -> bool:
    """
    Проверяет, является ли пользователь сотрудником, сверяя его ID и/или username с файлом staff_usernames.txt.
    """
    logger.debug(f"Проверяем пользователя: user_id={user_id}, username={username}")

    if not user_id and not username:
        logger.warning("Ошибка: Не указан ни ID, ни username.")
        return False

    # Проверяем наличие файла
    if not os.path.exists(Config.STAFF_USERNAMES_FILE):
        logger.error(f"Файл {Config.STAFF_USERNAMES_FILE} не найден.")
        return False

    try:
        # Загружаем данные из файла
        with open(Config.STAFF_USERNAMES_FILE, "r", encoding="utf-8") as f:
            staff_entries = f.read().splitlines()

        logger.debug(f"Список сотрудников: {staff_entries}")

        # Проверяем каждую запись
        for entry in staff_entries:
            entry_parts = entry.split()  # Разделяем строку по пробелам
            entry_id = None
            entry_username = None

            if len(entry_parts) == 2:
                # Если две части, определяем ID и username
                if entry_parts[0].startswith("@"):
                    entry_username = entry_parts[0]
                    entry_id = entry_parts[1]
                else:
                    entry_id = entry_parts[0]
                    entry_username = entry_parts[1]
            elif len(entry_parts) == 1:
                # Если только одна часть, определяем ID или username
                if entry_parts[0].startswith("@"):
                    entry_username = entry_parts[0]
                else:
                    entry_id = entry_parts[0]

            logger.debug(f"Проверяем запись: entry_id={entry_id}, entry_username={entry_username}")

            # Проверяем совпадение ID или username
            if (user_id and str(user_id) == entry_id) or (username and username == entry_username):
                logger.info(f"Пользователь {user_id} ({username}) найден в списке сотрудников.")
                return True

        logger.warning(f"Пользователь {user_id} ({username}) не найден в списке сотрудников.")
        return False

    except Exception as e:
        logger.error(f"Ошибка при проверке сотрудника: {e}")
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
    username = message.from_user.username or None  # Если отсутствует, то None
    full_name = message.from_user.full_name or "Без имени"
    user_id = message.from_user.id

    # Логируем базовую информацию о пользователе
    logger.info(f"Команда /start получена от пользователя: {username} (user_id: {user_id})")
    logger.debug(f"Детали пользователя: {message.from_user}")

    # Проверяем владельца
    if username == OWNER_USERNAME:
        logger.info(f"Пользователь {username} (user_id: {user_id}) идентифицирован как владелец.")
        await message.answer("Харибол, многоуважаемый Вениамин! Добро пожаловать в ваш бот клиентской поддержки.")
        await message.answer("Вот ваша админ-панель:", reply_markup=get_admin_menu())
        await set_bot_commands(bot, is_admin=True, user_id=user_id)
        return

    # Проверяем права сотрудника (админа)
    is_admin = False
    client_type = "individual"  # Тип по умолчанию
    if is_staff(user_id=user_id, username=username):  # Проверка через `is_staff`
        logger.info(f"Пользователь {username} (user_id: {user_id}) идентифицирован как сотрудник.")
        is_admin = True
        client_type = "admin"  # Если сотрудник, тип клиента должен быть "admin"

    # Работа с базой данных
    try:
        async with get_async_session() as session:
            user_exists = await user_is_registered(user_id, session)

            if user_exists:
                logger.info(f"Пользователь {user_id} уже существует в базе данных.")
            else:
                logger.info(f"Пользователь {user_id} отсутствует в базе. Добавляем нового пользователя.")
                await add_user(
                    user_id=user_id,
                    name=full_name,
                    username=username,
                    client_type=client_type,  # Добавляем тип клиента в зависимости от проверки
                    session=session
                )
                logger.info(f"Пользователь {user_id} успешно добавлен в базу данных.")
    except Exception as e:
        logger.error(f"Ошибка при работе с базой данных для пользователя {user_id}: {e}")
        await message.answer("Произошла ошибка при регистрации. Пожалуйста, повторите попытку позже.")
        return

    # Показ админ-панели или клиентского меню
    if is_admin:
        logger.info(f"Пользователю {username} (user_id: {user_id}) будет показано админ-меню.")
        await message.answer("Добро пожаловать, сотрудник! Вот ваша админ-панель.")
        await message.answer("Выберите действие:", reply_markup=get_admin_menu())
        await set_bot_commands(bot, is_admin=True, user_id=user_id)
    else:
        logger.info(f"Пользователю {username} (user_id: {user_id}) будет показано клиентское меню.")
        await message.answer(Config.WELCOME_MESSAGE)
        await message.answer(
            "Приветствуем! Пожалуйста, выберите, кто вы:",
            reply_markup=get_client_type_keyboard()
        )
        await set_bot_commands(bot, is_admin=False, user_id=user_id)

    # Логируем результат
    logger.debug(f"Результат обработки /start для пользователя {username} (user_id: {user_id}): {'Админ' if is_admin else 'Клиент'}")


@router.callback_query(lambda c: c.data and c.data.startswith("client_type:"))
async def process_client_type(callback_query: CallbackQuery):
    client_type = callback_query.data.split(":")[1]
    user_id = callback_query.from_user.id
    username = callback_query.from_user.username or "Без имени"
    name = callback_query.from_user.full_name or "Без имени"

    logger.info(f"Обработка выбора типа клиента: {client_type} для пользователя {user_id}")

    try:
        async with get_async_session() as session:
            if not await user_is_registered(user_id, session):
                await add_user(user_id, name, username, client_type, session)
                logger.info(f"Пользователь {user_id} добавлен как {client_type}.")
            else:
                await update_user_type(user_id, client_type, session)
                logger.info(f"Тип клиента пользователя {user_id} обновлён на {client_type}.")
    except Exception as e:
        logger.error(f"Ошибка при добавлении/обновлении пользователя: {e}")
        await callback_query.message.answer("Произошла ошибка при обработке вашего выбора. Попробуйте позже.")
        return

    # Отправка ответа клиенту
    if client_type == "organizer":
        await callback_query.message.answer("Вы выбрали категорию: Организатор мероприятий.")
        await callback_query.message.answer("Пожалуйста, выберите нужное меню:",
                                            reply_markup=get_two_column_keyboard(is_organizer=True))
    elif client_type == "individual":
        await callback_query.message.answer("Вы выбрали категорию: Индивидуальный клиент.")
        await callback_query.message.answer("Пожалуйста, выберите нужное меню:",
                                            reply_markup=get_two_column_keyboard())

    await callback_query.answer()
    logger.info(f"Выбор типа клиента обработан успешно для пользователя {user_id}. Статус: {client_type}")


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