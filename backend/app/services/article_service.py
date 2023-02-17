from contextlib import AbstractAsyncContextManager
from typing import Callable

from starlette.datastructures import Address

import app.config as config
from app.exceptions import ContentNotFoundError
from app.models import Article
from app.redis import Redis
from app.repositories import ArticleRepository
from app.schemas import ArticleSchema


class ArticleService:
    def __init__(
        self,
        article_repo: ArticleRepository,
        redis_client_factory: Callable[..., AbstractAsyncContextManager[Redis]],
    ):
        self._article_repo = article_repo
        self._redis_client_factory = redis_client_factory

    async def create(self, title: str, author_id: int) -> ArticleSchema:
        article = Article(title=title.strip(), author_id=author_id)

        return ArticleSchema.from_orm(await self._article_repo.save(article))

    async def get_by_id(self, id: int) -> ArticleSchema | None:
        article = await self._article_repo.get_by_id(id)
        if article is None:
            return None
        return ArticleSchema.from_orm(article)

    async def get_by_author_id(self, author_id: int) -> list[ArticleSchema]:
        db_articles = await self._article_repo.get_by_author_id(author_id)
        return list(map(ArticleSchema.from_orm, db_articles))

    async def update(self, article: ArticleSchema) -> ArticleSchema:
        db_article = await self._article_repo.get_by_id(article.id)
        if db_article is None:
            raise ContentNotFoundError()

        db_article.title = article.title.strip()
        db_article.body = article.body
        db_article.is_published = article.is_published
        db_article = await self._article_repo.save(db_article)

        return ArticleSchema.from_orm(db_article)

    async def count_view(self, article_id: int, client_address: Address):
        db_article = await self._article_repo.get_by_id(article_id)
        if db_article is None:
            raise ContentNotFoundError()

        redis_key = f"client:{client_address.host}:{client_address.port}:viewed_article:{article_id}"  # noqa: E501

        async with self._redis_client_factory() as redis:
            if redis.exists(redis_key):
                return

            redis.set(redis_key, "", config.ARTICLE_VIEW_COUNT_DELAY)
            await self._article_repo.add_view(article_id)
