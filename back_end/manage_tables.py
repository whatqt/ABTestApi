from src.orm.postgresql.models import Base
from src.orm.postgresql.settings import engine
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from src.orm.mongodb.settings import client

async def create_tables() -> None:
    '''создаёт таблицы'''
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            print("Таблицы созданы")
    except Exception as e:
        print(f"Возникла ошибка {e}")


async def drop_tables() -> None:
    '''удаляет таблицы'''
    try:
        databases = []
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            print("Таблицы удалены")
    except Exception as e:
        print(f"Возникла ошибка {e}")

if __name__ == "__main__":
    mode = int(input("1 - создание таблиц\n2 - удаление таблиц.\n")) 
    if mode == 1:
        asyncio.run(create_tables())
    elif mode == 2:
        asyncio.run(drop_tables())
    else:
        print("Выберите режим от 1 до 2")