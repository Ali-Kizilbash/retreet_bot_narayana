import asyncio
from app.database.db import create_db_and_tables

async def main():
    await create_db_and_tables()
    print("Таблицы успешно созданы!")

if __name__ == "__main__":
    asyncio.run(main())
