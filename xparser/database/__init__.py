from xparser.database.models import *
from sqlalchemy.ext.asyncio import AsyncEngine,create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text, delete
from os import getenv
from typing import Iterable
from loguru import logger
from functools import lru_cache
from halone.patterns import SpotResultPublisher


class Database:
    engine: AsyncEngine = ...
    session_maker: async_sessionmaker[AsyncSession] = ...
    publisher: SpotResultPublisher = SpotResultPublisher()

    @classmethod
    async def init(cls):
        url = f'postgresql+asyncpg://{getenv("_USERNAME_")}:{getenv("PASSWORD")}'\
                                  f'@{getenv("HOST")}/{getenv("DATABASE")}'
        logger.info(f'Start database with url :: {url}')
        cls.engine = create_async_engine(url, echo=bool(getenv('debug','')))
        async with cls.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        cls.session_maker = async_sessionmaker(bind=cls.engine)

    @classmethod
    @logger.catch
    async def add_to_database(cls, spots: Iterable[Spot]):
        async with cls.session_maker() as session:
            session.add_all(
                spots
            )
            await session.commit()

    @classmethod
    @logger.catch
    async def proceed_database(cls):
        query = text(cls.get_select_query())
        async with cls.session_maker() as session:
            result = await session.execute(query)
            await session.execute(delete(Spot))
            await session.commit()
            res = result.fetchall()
            result = [
                SpotResult(
                        benefit=i[0],
                        price1=i[1],
                        price2=i[2],
                        spot_id1=i[3],
                        spot_id2=i[4],
                        symbol_id=i[5],
                        ask=i[6]
                    ) for i in res]
            if res:
                await cls.publisher.new_best_result(result)
                session.add_all(
                    (
                        result
                    )
                )
                await session.commit()

    @staticmethod
    @lru_cache
    def get_select_query():
        from pathlib import Path
        from os import getcwd
        with open(Path(getcwd()).joinpath('select.sql')) as f:
            return f.read()

    @classmethod
    async def execute(cls, stmt) -> Iterable[Base]:
        async with cls.session_maker() as conn:
            return await conn.execute(stmt)

