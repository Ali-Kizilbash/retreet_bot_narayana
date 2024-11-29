from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from config import Config
from app.database.models import Base  # убедитесь, что у вас есть файл models.py с базовыми моделями

# Инициализация только если DATABASE_URL задан
if Config.DATABASE_URL:
    engine = create_async_engine(Config.DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
else:
    engine = None
    async_session = None

async def get_async_session():
    """Получение асинхронной сессии. Если DATABASE_URL отсутствует, вызывает исключение."""
    if async_session is None:
        raise RuntimeError("Сессия базы данных не инициализирована, так как DATABASE_URL отсутствует.")
    async with async_session() as session:
        yield session

async def create_db_and_tables():
    """Создание базы данных и таблиц, если DATABASE_URL указан."""
    if engine is None:
        print("Движок базы данных не инициализирован, так как DATABASE_URL отсутствует.")
        return
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    pass
