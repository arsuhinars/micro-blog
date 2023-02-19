from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.container import AppContainer
from app.dependencies import validate_access_token, validate_optional_access_token
from app.exceptions import AccessDeniedError
from app.schemas import ArticleCreateSchema, ArticleSchema
from app.services import ArticleService

router = APIRouter(tags=["Article"])


@router.post(
    "/article",
    response_model=ArticleSchema,
    summary="Creates new user article",
)
@inject
async def create_article(
    article_create_data: ArticleCreateSchema,
    article_service: ArticleService = Depends(Provide[AppContainer.article_service]),
    user_id: int = Depends(validate_access_token),
):
    return await article_service.create(article_create_data.title, user_id)


@router.put(
    "/article/{article_id}",
    response_model=ArticleSchema,
    summary="Updates article by id",
    description="""This method will raise 403 HTTP status code (Forbidden) if article is
    private and user is not its author""",
)
@inject
async def update_article(
    article_id: int,
    article: ArticleSchema,
    article_service: ArticleService = Depends(Provide[AppContainer.article_service]),
    user_id: int = Depends(validate_access_token),
):
    db_article = await article_service.get_by_id(article_id)
    if db_article.author_id != user_id:
        raise AccessDeniedError()

    article.id = article_id
    return await article_service.update(article)


@router.get(
    "/article/{article_id}",
    response_model=ArticleSchema,
    summary="Get article by id",
    description="""Raise 403 status code (Forbidden) if article exists, but is
    private and user is not its author""",
)
async def get_article_by_id(
    article_id: int,
    article_service: ArticleService = Depends(Provide[AppContainer.article_service]),
    user_id: int | None = Depends(validate_optional_access_token),
):
    article = await article_service.get_by_id(article_id)
    if not article.is_published and user_id != article.author_id:
        raise AccessDeniedError()

    return article


@router.get(
    "/user/{user_id}/articles_ids",
    response_model=list[int],
    summary="Get ids of user's articles",
    description="""Returns only available articles, e.g if it is requested by other
    users, then only public articles are returned.""",
)
async def get_user_articles(
    user_id: int,
    article_service: ArticleService = Depends(Provide[AppContainer.article_service]),
    curr_user_id: int | None = Depends(validate_optional_access_token),
):
    articles = await article_service.get_by_author_id(user_id)
    if curr_user_id != user_id:
        articles = [a for a in articles if a.is_published]
    return list(map(lambda a: a.id, articles))
