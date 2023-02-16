from app.repositories import ArticleRepository
from app.schemas import ArticleSchema


class ArticleService:
    def __init__(self, article_repo: ArticleRepository):
        self._article_repo = article_repo

    async def create(self, title: str, author_id: int) -> ArticleSchema:
        ...

    async def get_by_id(self, id: int) -> ArticleSchema | None:
        ...

    async def get_by_author_id(self, author_id: int) -> list[ArticleSchema]:
        ...

    async def update(self, article: ArticleSchema) -> ArticleSchema:
        ...
