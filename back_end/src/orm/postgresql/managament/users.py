import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from orm.postgresql.settings import engine
from sqlalchemy.ext.asyncio import AsyncSession
from orm.postgresql.models import Users
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from utils.logger import logger
from sqlalchemy.sql.expression import BinaryExpression
from typing import Union


class ManageUser:
    '''Управление таблицой Users в PostgreSQL.'''

    @classmethod
    async def _get(cls, filter_: BinaryExpression) -> Union[Users, None]:
        '''
        Приватный метод, который не предназначен для использование вне класса.
        Метод ищет пользователя с условием, которое передаётся в аргументе filter.
        
        :param filter: условие для поиска пользователя
        :return  Users | None: Если пользователь найден, 
        то метод вернёт его, иначе вернёт None
        '''
        
        async with AsyncSession(
            bind=engine, 
            expire_on_commit=False
        ) as session:
            result = await session.execute(
                select(Users).where(filter_)
            )
            return result.scalar_one_or_none()
        
    @classmethod
    async def get_by_id(cls, id_user: int) -> Union[Users, None]:
        '''
        Находит пользователя по его id.

        :param id_user: id пользователя
        :return  Users | None: Если пользователь найден, 
        то метод вернёт его, иначе вернёт None 
        '''

        return await cls._get(Users.id == id_user)
        
    @classmethod
    async def get_by_email(cls, email: str) -> Union[Users, None]:
        '''
        Находит пользователя по его почте.

        :param email: почта пользователя
        :return Users | None: Если пользователь найден, 
        то метод вернёт его, иначе вернёт None 
        '''

        return await cls._get(Users.email==email)

    @classmethod
    async def create(
        self, 
        email: str, 
        username: str,
        password: bytes
    ) -> Union[Users, None]:
        """
        Создание пользователя.
        
        Params:
            email: почта пользователя.
            username: имя пользователя.
            passwoord: закэшированный пароль.

        :return Users | None: Возвращает пользователя, 
        но если такой пользователь существует, то вернёт None.
        """
        async with AsyncSession(
            bind=engine,
            expire_on_commit=False
        ) as session:
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
                   logger.error(f"Ошибка при создание пользователя {e}")

    @classmethod
    async def save_refresh_token(cls, user: Users, token: str) -> bool:
        '''
        Сохраняет рефреш токен у определенного пользователя.
        
        Params:
            user: Объект таблицы Users.
            token: refresh токен.

        :return True | False: Если у пользователя уже есть jwt токен, 
        то возвращает False, иначе True.
        '''
        async with AsyncSession(bind=engine) as session:
            async with session.begin():
                check_token = user.jwt_refresh_token
                if check_token:
                    # проверить, истёк ли рефреш токен. Если истёк - записать новый
                    return False
                session.add(user)
                user.jwt_refresh_token = token
                await session.commit()
                session.expunge_all()
                return True

                    
