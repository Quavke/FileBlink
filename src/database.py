from typing import AsyncGenerator

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
# from sqlalchemy.orm import DeclarativeBase
from src.config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


# my_metadata = MetaData()


# Base: DeclarativeMeta = declarative_base(metadata=my_metadata)


# class Base(DeclarativeBase):
#     pass


#
#
# Base_1 = Base
# Base_1.metadata = my_metadata

engine = create_async_engine(DATABASE_URL, poolclass=NullPool)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
