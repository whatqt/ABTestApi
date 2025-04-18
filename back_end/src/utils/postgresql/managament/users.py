import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from utils.postgresql.settings import engine
from sqlalchemy.ext.asyncio import AsyncSession
from utils.postgresql.models import Users
from sqlalchemy import select
from sqlalchemy import Select, and_




class ManageUser:
    def __init__(
            self, email: str, username: str, 
            password: bytes
        ):
        self.email = email
        self.username = username
        self.password = password

    async def create(self):
        async with AsyncSession(autoflush=False, bind=engine) as session:
            async with session.begin(): # Для транзакций
                user = Users(
                    email=self.email,
                    username=self.username,
                    password=self.password
                )
                try:
                    session.add(user)
                    await session.commit()
                    return user
                except Exception as e:
                   # добавить нормальное логирование
                   print(f"Ошибка при создание пользователя {e}")

    async def get(self):
        async with AsyncSession(autoflush=False, bind=engine, expire_on_commit=False) as session:
            result = await session.execute(
                select(Users).where(
                    Users.email==self.email,
                )
            )
            return result.scalar_one_or_none()
        
    async def get_hash(self):
        async with AsyncSession(autoflush=False, bind=engine, expire_on_commit=False) as session:
            result = await session.execute(
                select(Users).where(
                    Users.email==self.email,
                )
            )
            return result.scalar_one_or_none().password