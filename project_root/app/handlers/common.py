from aiogram import Router, types
from aiogram.types import CallbackQuery, InputFile
from aiogram.filters import Command
from config import Config, validate_config
from app.database.crud import user_is_registered, register_user  # Импорт функций для работы с БД
from app.database.db import get_async_session  # Импорт функции для получения сессии базы данных
from app.keyboards.client_kb import (
    get_client_type_keyboard,
    get_general_menu_keyboard,
    get_organizer_menu_keyboard
)  # Импорт клавиатур
from app.keyboards.admin_kb import get_admin_menu  # Импорт клавиатуры для админ-панели
import os

# Проверяем наличие необходимых переменных окружения
try:
    validate_config()
    print("Конфигурация успешно проверена.")
except EnvironmentError as e:
    print(f"Ошибка конфигурации: {e}")
    exit(1)  # Завершаем выполнение, если отсутствуют необходимые переменные

router = Router()
STAFF_USERNAMES_FILE = "staff_usernames.txt"  # Файл с никнеймами сотрудников
OWNER_USERNAME = "@Veniamin_tk"  # Никнейм владельца бота


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


@router.message(Command("start"))  # Используем Command для регистрации команды /start
async def start_command(message: types.Message):
    username = message.from_user.username
    print(f"Команда /start получена от пользователя: {username}")

    if not username:
        await message.answer("Для работы с ботом, пожалуйста, установите username в настройках Telegram.")
        return

    if username == OWNER_USERNAME:
        print("Показываем админ-панель владельцу.")
        await message.answer("Харибол, многоуважаемый Вениамин! Добро пожаловать в ваш бот клиентской поддержки.")
        await message.answer("Вот ваша админ-панель:", reply_markup=get_admin_menu())
    elif username and is_staff(f"@{username}"):
        print("Показываем админ-панель сотруднику.")
        await message.answer("Добро пожаловать, сотрудник! Вот ваша админ-панель.")
        await message.answer("Выберите действие:", reply_markup=get_admin_menu())
    else:
        print("Пользователь не является админом или сотрудником.")
        async for session in get_async_session():
            if await user_is_registered(message.from_user.id, session):
                await message.answer(Config.ALREADY_REGISTERED_MESSAGE)
            else:
                await message.answer(Config.WELCOME_MESSAGE)
                await register_user(message.from_user.id, session)
                # После регистрации показываем меню с выбором категории
                await message.answer(
                    "Приветствуем! Пожалуйста, выберите, кто вы:",
                    reply_markup=get_client_type_keyboard()
                )


@router.callback_query(lambda c: c.data and c.data.startswith("client_type:"))
async def process_client_type(callback_query: CallbackQuery):
    client_type = callback_query.data.split(":")[1]
    print(f"Обработка выбора типа клиента: {client_type}")
    
    try:
        if client_type == "organizer":
            await callback_query.message.answer("Вы выбрали категорию: Организатор мероприятий.")
            await callback_query.message.answer(
                "Пожалуйста, выберите действие:",
                reply_markup=get_organizer_menu_keyboard()
            )
        elif client_type == "individual":
            await callback_query.message.answer("Вы выбрали категорию: Индивидуальный клиент.")

        await callback_query.message.answer(
            "Выберите нужную информацию:",
            reply_markup=get_general_menu_keyboard()
        )
        await callback_query.answer()  # Закрываем всплывающее уведомление
        print("Выбор типа клиента обработан успешно.")
    except Exception as e:
        print(f"Ошибка при обработке выбора типа клиента: {e}")


@router.callback_query(lambda c: c.data == "organizer_guide")
async def send_organizer_guide(callback_query: CallbackQuery):
    pdf_path = "resources/event_organizer_guide.pdf"
    print(f"Запрос на отправку руководства организатора. Путь к файлу: {pdf_path}")
    if not os.path.exists(pdf_path):
        await callback_query.message.answer("Памятка для организаторов не найдена.")
        print("Файл event_organizer_guide.pdf не найден.")
    else:
        try:
            pdf_file = InputFile(pdf_path)
            await callback_query.message.answer_document(pdf_file, caption="Вот памятка для организаторов мероприятий. Ознакомьтесь с условиями.")
            print("Руководство организатора отправлено успешно.")
        except Exception as e:
            print(f"Ошибка при отправке руководства организатора: {e}")
    await callback_query.answer()


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
