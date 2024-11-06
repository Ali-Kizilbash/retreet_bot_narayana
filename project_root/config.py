from dotenv import load_dotenv
import os

# Загружаем переменные окружения для конфиденциальных данных
load_dotenv()


class Config:
    # Токен и URL базы данных из переменных окружения
    BOT_TOKEN = os.getenv("BOT_TOKEN")
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


def load_config():
    """Функция для загрузки конфигурации"""
    return Config