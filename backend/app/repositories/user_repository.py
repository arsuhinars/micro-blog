from contextlib import AbstractAsyncContextManager
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from app.models import User


class UserRepository:
    def __init__(
        self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]
    ):
        self.session_factory = session_factory

    async def get_by_id(self, id: int) -> User | None:
        session: AsyncSession
        async with self.session_factory() as session:
            return await session.get(User, id)

    async def get_by_email(self, email: str) -> User | None:
        session: AsyncSession
        async with self.session_factory() as session:
            result = await session.execute(
                select(User).where(User.email == email).limit(1)
            )
            return result.scalar_one_or_none()

    async def save(self, user: User) -> User:
        session: AsyncSession
        async with self.session_factory() as session:
            session.add(user)
            await session.flush()
            await session.commit()
            return user
