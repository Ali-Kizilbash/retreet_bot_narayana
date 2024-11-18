# config.py

from dotenv import load_dotenv
import os

# Загрузка переменных окружения
load_dotenv()


class Config:
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

    # Ссылки по категориям
    LINKS = {
        "social_networks": [
            {"name": "Instagram", "url": "https://instagram.com/narayana.center"},
            {"name": "Instagram 2", "url": "https://www.instagram.com/narayana_center?igsh=ZXdjOHVjNWpjMDQy"},
            {"name": "VK страница", "url": "https://vk.com/narayana.center"},
            {"name": "VK группа", "url": "https://vk.com/narayana.sochi"},
            {"name": "VK страница 2", "url": "https://vk.com/narayana_center108"},
            {"name": "Соц. сеть йогов", "url": "https://t.me/Narayana_social"}
        ],
        "announcements": [
            {"name": "Анонсы мероприятий", "url": "https://t.me/narayana_retreat_center"},
            {"name": "Анонсы мероприятий 2", "url": "https://t.me/narayanacenter"}
        ],
        "maps": [
            {"name": "Google Maps", "url": "https://www.google.ru/maps/place/Нараяна/@43.6809883,39.6058015,17z"},
            {"name": "Яндекс Карты", "url": "https://yandex.ru/maps/org/narayana/192015920362/?ll=39.607847%2C43.680902"},
            {"name": "2Гис", "url": "https://2gis.ru/sochi/firm/70000001049866178?m=39.607907%2C43.680824%2F16"}
        ],
        "contact_details": [
            {"name": "Почта", "url": "mailto:info@narayana.center"}
        ],
        "website": [
            {"name": "Наш сайт", "url": "https://narayana.center"},
            {"name": "Таплинк", "url": "https://narayana.taplink.ws/"}
        ],
        "store": [
            {"name": "Интернет магазин", "url": "http://shop.narayana.center/"}
        ],
        "organizer_chat": [
            {"name": "Чат для организаторов", "url": "https://t.me/Retreats_Narayana"}
        ],
        "video": [
            {"name": "Нараяна", "url": "https://youtube.com/@centernarayana"},
            {"name": "Видео-обзор Ретрит-центра", "url": "https://youtu.be/26R-lgMgfOY"}
        ]
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
