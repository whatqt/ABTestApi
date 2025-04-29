import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from orm.postgresql.models import APIGateway
from orm.postgresql.settings import engine
from sqlalchemy.ext.asyncio import AsyncSession
from orm.postgresql.models import Users
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError



class ManageAPIGateway:
    def __init__(self, user_id: int):
        self.user_id = user_id

    async def create(self, body: dict):
        async with AsyncSession(autoflush=False, bind=engine) as session:
            async with session.begin():
                obj = APIGateway(
                    user_id=self.user_id,
                    main_api = body["main_api"],
                    first_api = body["first_api"],
                    second_api = body["second_api"]
                )
                session.add(obj)
                await session.commit()
                return obj
    
    async def get(
        self, 
        id_record: int = None
    ):
        async with AsyncSession(
            autoflush=False, 
            bing=engine,
            expire_on_commit=False
        ) as session:
            if id_record:
                result = await session.execute(
                    select(APIGateway).where(
                        APIGateway.id==id
                    )
                )
            else:
                result = await session.execute(
                    select(APIGateway)
                )
            return result
        