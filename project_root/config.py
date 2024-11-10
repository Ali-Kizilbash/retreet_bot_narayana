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
    ALREADY_REGISTERED_MESSAGE = (
        "С возвращением! Чем могу помочь?"
    )


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
