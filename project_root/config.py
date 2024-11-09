from dotenv import load_dotenv
import os

# Загружаем переменные окружения для конфиденциальных данных
load_dotenv()


class Config:
    # Токен и URL базы данных из переменных окружения  
    BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
    DATABASE_URL = os.getenv("DATABASE_URL")

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
