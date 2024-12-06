from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from config import load_config

# Загрузка конфигурации
config = load_config()

# Настройка базы данных
DATABASE_URL = config.DATABASE_URL

# Создаем движок для работы с базой данных
engine = create_async_engine(DATABASE_URL, echo=True)

# Создаем базу данных с помощью ORM SQLAlchemy
Base = declarative_base()

# Создаем сессию для взаимодействия с базой данных
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Функция для получения сессии
async def get_async_session():
    return async_session()

# Создание таблиц в базе данных
async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Закрытие соединения с базой данных
async def close_db():
    await engine.dispose()
