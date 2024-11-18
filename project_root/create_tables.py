from app.database.db import create_db_and_tables
import asyncio

if __name__ == "__main__":
    asyncio.run(create_db_and_tables())
