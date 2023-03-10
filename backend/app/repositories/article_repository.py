from contextlib import AbstractAsyncContextManager
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from app.models import Article


class ArticleRepository:
    def __init__(
        self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]
    ):
        self.session_factory = session_factory

    async def get_by_id(self, id: int) -> Article | None:
        session: AsyncSession
        async with self.session_factory() as session:
            return await session.get(Article, id)

    async def get_by_author_id(self, author_id: int) -> list[Article]:
        session: AsyncSession
        async with self.session_factory() as session:
            result = await session.execute(
                select(Article).where(Article.author_id == author_id)
            )
            return list(result.scalars().all())

    async def save(self, article: Article):
        session: AsyncSession
        async with self.session_factory() as session:
            session.add(article)
            await session.flush()
            await session.commit()

    async def add_view(self, id: int):
        async with self.session_factory() as session:
            article = await session.get(Article, id)
            if article is None:
                return

            article.views_count = Article.views_count + 1
            await session.flush()
            await session.commit()
