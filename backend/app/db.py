from contextlib import asynccontextmanager, AbstractAsyncContextManager

from sqlalchemy.ext.asyncio import create_async_engine, async_scoped_session
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Database:
    def __init__(self, url: str):
        self._engine = create_async_engine(url)
        self._session_factory = async_scoped_session(
            async_sessionmaker(
                bind=self._engine,
                autoflush=False,
                expire_on_commit=True
            )
        )

    def create_database(self):
        Base.metadata.create_all(self._engine)

    @property
    def engine(self):
        return self._engine
    
    @asynccontextmanager
    async def session(self) -> callable[..., AbstractAsyncContextManager[AsyncSession]]:
        session: AsyncSession = self._session_factory()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
