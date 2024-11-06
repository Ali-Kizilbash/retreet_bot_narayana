from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from config import Config
from app.database.models import Base  # убедитесь, что у вас есть файл models.py с базовыми моделями

# Создание движка базы данных
engine = create_async_engine(Config.DATABASE_URL, echo=True)

# Создание фабрики сессий
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        yield session

# Функция для создания базы данных и таблиц
async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
