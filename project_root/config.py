# config.py

from dotenv import load_dotenv
import os

# Загрузка переменных окружения
load_dotenv()

class Config:
    # Токен и URL базы данных
    BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
    DATABASE_URL = os.getenv("DATABASE_URL")

    # Пути к ресурсам (относительно корня проекта)
    STAFF_USERNAMES_FILE = "resources/staff_usernames.txt"
    DIRECTIONS_FILE = "resources/directions.txt"
    EVENT_ORGANIZER_GUIDE_FILE = "resources/event_organizer_guide.pdf"
    RULES_FILE = "resources/rules.txt"

    # Тексты приветственных сообщений
    WELCOME_MESSAGE = (
        "🌿 Добро пожаловать! Я — бот клиентской поддержки центра Narayana в Сочи. "
        "Здесь вы найдете всё для отдыха души и тела: ретриты, йога-туры и уникальные "
        "программы в окружении природы. Готов помочь вам узнать больше и ответить на ваши вопросы!"
    )
    ALREADY_REGISTERED_MESSAGE = "С возвращением! Чем могу помочь?"

    # Параметры для работы с погодным API
    WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast?latitude=43.5855&longitude=39.7202&current_weather=true"
    
    # Словарь перевода описаний погоды
    WEATHER_CODES = {
        0: "ясно",
        1: "в основном ясно",
        2: "частично облачно",
        3: "пасмурно",
        45: "туман",
        48: "изморозь",
        51: "легкая морось",
        53: "умеренная морось",
        55: "густая морось",
        56: "лёгкая ледяная морось",
        57: "сильная ледяная морось",
        61: "легкий дождь",
        63: "умеренный дождь",
        65: "сильный дождь",
        71: "легкий снегопад",
        73: "умеренный снегопад",
        75: "сильный снегопад",
        80: "легкий ливень",
        81: "умеренный ливень",
        82: "сильный ливень",
        95: "гроза",
        96: "гроза с небольшим градом",
        99: "гроза с сильным градом"
    }


def validate_config():
    """Проверяет, загружены ли необходимые переменные окружения."""
    missing_vars = []
    if not Config.BOT_TOKEN:
        missing_vars.append("BOT_TOKEN")
    if not Config.DATABASE_URL:
        missing_vars.append("DATABASE_URL")

    if missing_vars:
        raise EnvironmentError(f"Отсутствуют необходимые переменные окружения: {', '.join(missing_vars)}")


def load_config():
    """Возвращает экземпляр Config для использования в других частях кода."""
    return Config
