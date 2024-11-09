import aiosqlite
from config import Config
from app.database.models import Base  # убедитесь, что у вас есть файл models.py с базовыми моделями


<<<<<<< HEAD
async def create_db_and_tables():
    async with aiosqlite.connect(Config.DATABASE_URL) as db:
        await db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
        await db.commit()
=======
# Создание фабрики сессий
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        yield session

# Функция для создания базы данных и таблиц
async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
>>>>>>> 18e49f14a8c56d4a8de5d9a51cc925c756a18365
