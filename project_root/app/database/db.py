from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from config import Config
from app.database.models import Base  # убедитесь, что у вас есть файл models.py с базовыми моделями
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)

async def test_connection():
    """Проверка подключения к базе данных."""
    if engine is None:
        raise RuntimeError("Движок базы данных не инициализирован. Проверьте DATABASE_URL.")
    try:
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")  # Проверяем подключение
            print("Подключение успешно!")
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
        raise


# Инициализация только если DATABASE_URL задан
if Config.DATABASE_URL:
    engine = create_async_engine(Config.DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
else:
    engine = None
    async_session = None


async def create_db_and_tables():
    if engine is None:
        raise RuntimeError("Движок базы данных не инициализирован. Проверьте DATABASE_URL.")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Таблицы успешно созданы.")
    except Exception as e:
        logger.error(f"Ошибка при создании таблиц: {e}")
        raise


async def init_db():
    """Создает таблицы, если их нет."""
    if engine is None:
        raise RuntimeError("Движок базы данных не инициализирован. Проверьте DATABASE_URL.")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Таблицы успешно созданы.")


@asynccontextmanager
async def get_async_session():
    """Контекстный менеджер для безопасной работы с сессией."""
    if async_session is None:
        raise RuntimeError("Сессия базы данных не инициализирована. Проверьте DATABASE_URL.")
    async with async_session() as session:
        yield session