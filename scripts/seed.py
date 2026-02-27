import asyncio
import argparse
from database.db import init_db

async def seed():
    print("Seeding database with mock data...")
    # Наша init_db() теперь создаст таблицы, а заполнение товарами мы сейчас вынесем туда или оставим там
    # Если мы отрефакторим init_db(), то seed() можно будет вызывать отдельно.
    # Для MVP оставим вызов init_db(), но в будущем лучше разделить create_tables и seed_data.
    await init_db(seed_data=True)
    print("Database seeded completely.")

if __name__ == "__main__":
    asyncio.run(seed())
