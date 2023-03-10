import asyncio
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import Callable

from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    async_scoped_session,
    create_async_engine,
)
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.models import Article, User  # noqa: F401, E402


class Database:
    def __init__(self, url: str):
        self._engine = create_async_engine(url)
        self._session_factory = async_scoped_session(
            async_sessionmaker(
                bind=self._engine, autoflush=False, expire_on_commit=False
            ),
            lambda: asyncio.current_task,
        )

    async def create_database(self):
        conn: AsyncConnection
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @property
    def engine(self):
        return self._engine

    @asynccontextmanager
    async def session(self) -> Callable[..., AbstractAsyncContextManager[AsyncSession]]:
        session: AsyncSession = self._session_factory()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
