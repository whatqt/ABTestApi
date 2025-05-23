import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from orm.postgresql.models import WhiteListUrls
from orm.postgresql.settings import engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Union
from sqlalchemy.exc import IntegrityError
from utils.logger import logger



class ManageWhiteListUrls:

    @classmethod
    async def get(cls, url: str) -> Union[WhiteListUrls, None]:
        async with AsyncSession(
            bind=engine, 
            expire_on_commit=False
        ) as session:
            result = await session.execute(
                select(WhiteListUrls).where(
                    WhiteListUrls.url==url
                )
            )
            result = result.scalar_one_or_none()
        return result
    
    @classmethod
    async def create(cls, url: str, user):
        async with AsyncSession(
            bind=engine,
            autoflush=False,
            expire_on_commit=False
        ) as session:
            async with session.begin():
                obj = WhiteListUrls(
                    url=url,
                    user=user
                )
                try:
                    session.add(obj)
                    await session.commit()
                    return obj
                except IntegrityError:
                    return None
                # except Exception as e:
                #     logger.error(f"Возникла ошибка при занесение данных: {e}")