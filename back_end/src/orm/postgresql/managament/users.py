import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from orm.postgresql.settings import engine
from sqlalchemy.ext.asyncio import AsyncSession
from orm.postgresql.models import Users
from sqlalchemy import select
from auth.utils import JWToken
from sqlalchemy.exc import IntegrityError


class UserIsNone(Exception):
    def __init__(self, email: str):
        self.email = email

    def __str__(self):
        return f"Пользователя с почтой {self.email!r} не существует"
    
class ManageUser:
    @classmethod
    async def get(cls, email: str):
        async with AsyncSession(autoflush=False, bind=engine, expire_on_commit=False) as session:
            result = await session.execute(
                select(Users).where(
                    Users.email==email,
                )
            )
            return result.scalar_one_or_none()
        
    @classmethod
    async def create(
        self, 
        email: str, 
        username: str,
        password: str
    ):
        async with AsyncSession(autoflush=False, bind=engine) as session:
            async with session.begin(): # Для транзакций
                user = Users(
                    email=email,
                    username=username,
                    password=password,
                    jwt_refresh_token=None
                )
                try:
                    session.add(user)
                    await session.commit()
                    return user
                except IntegrityError:
                    return None
                except Exception as e:
                   # добавить нормальное логирование
                   print(f"Ошибка при создание пользователя {e}")

    @classmethod
    async def save_refresh_token(cls, user: Users, token: str):
        async with AsyncSession(autoflush=False, bind=engine) as session:
            async with session.begin():
                check_token = user.jwt_refresh_token
                if check_token:
                    return False
                session.add(user)
                user.jwt_refresh_token = token
                await session.commit()
                return True

                    
