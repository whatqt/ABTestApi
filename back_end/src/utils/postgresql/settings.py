import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine


engine = create_async_engine(
    "postgresql+asyncpg://scott:tiger@localhost/test",
    echo=True,
)