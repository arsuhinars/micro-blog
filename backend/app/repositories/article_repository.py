from contextlib import AbstractAsyncContextManager
from typing import Callable

from sqlalchemy.sql import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Article


class ArticleRepository:
    
    def __init__(self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]):
        self.session_factory = session_factory

    async def get_by_id(self, id: int) -> Article | None:
        session: AsyncSession
        with self.session_factory() as session:
            return await session.get(Article, id)

    async def get_by_author_id(self, author_id: int) -> list[Article]:
        session: AsyncSession
        with self.session_factory() as session:
            result = await session.execute(
                select(Article).where(Article.author_id == author_id)
            )
            return list(result.scalars().all())

    async def save(self, article: Article):
        session: AsyncSession
        with self.session_factory() as session:
            session.add(article)
            await session.flush()
            await session.commit()
