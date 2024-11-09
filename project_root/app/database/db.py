import aiosqlite
from config import Config


async def create_db_and_tables():
    async with aiosqlite.connect(Config.DATABASE_URL) as db:
        await db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
        await db.commit()