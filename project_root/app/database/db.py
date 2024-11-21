from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text as sql_text  # Используем псевдоним
from config import Config
from app.database.models import Base
import logging

# Создание асинхронного движка и сессии
engine = create_async_engine(Config.DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, 
                             class_=AsyncSession)

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,  # Максимальный уровень логирования
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]  # Логи выводятся в консоль
)

# Логирование для SQLAlchemy
logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)
logging.getLogger("sqlalchemy.pool").setLevel(logging.DEBUG)
logging.getLogger("asyncpg").setLevel(logging.DEBUG)


# Функция создания базы данных и таблиц
async def create_db_and_tables():
    """Создание базы данных и таблиц, если они еще не существуют."""
    try:
        async with engine.begin() as conn:
            logging.info("Проверяем и создаём таблицы, если их нет...")
            await conn.run_sync(Base.metadata.create_all)
            logging.info("Таблицы успешно созданы или уже существуют.")
    except Exception as e:
        logging.error(f"Ошибка при создании таблиц: {e}")
        raise


# Тестовое подключение
async def test_connection():
    """Проверяет подключение к базе данных."""
    try:
        async with engine.connect() as conn:
            logging.info("Проверка подключения к базе данных...")
            result = await conn.execute(sql_text("SELECT 1"))
            logging.info(f"Результат тестового запроса: {result.scalar()}")
    except Exception as e:
        logging.error(f"Ошибка подключения к базе данных: {e}")
        logging.exception("Детали ошибки:")  # Вывод полного стека ошибки
    finally:
        await engine.dispose()
        logging.info("Соединение с базой данных закрыто.")


# Проверка сессии при запросах
async def check_session():
    """Проверяет, можно ли открыть сессию."""
    try:
        async with async_session() as session:
            async with session.begin():
                logging.info("Сессия базы данных успешно открыта и работает.")
    except Exception as e:
        logging.error(f"Ошибка при проверке сессии: {e}")