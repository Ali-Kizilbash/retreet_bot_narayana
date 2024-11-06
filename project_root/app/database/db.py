from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from config import Config

# Создание движка базы данных
engine = create_async_engine(Config.DATABASE_URL, echo=True)

# Создание фабрики сессий
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        yield session
