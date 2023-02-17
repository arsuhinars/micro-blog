from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.container import AppContainer
from app.dependencies import validate_access_token
from app.schemas import ArticleSchema
from app.services import ArticleService

router = APIRouter()


@router.post(
    "/article",
    response_model=ArticleSchema,
    summary="Creates new user article",
)
@inject
def create_article(
    article: ArticleSchema,
    article_service: ArticleService = Depends(Provide[AppContainer.article_service]),
    user_id: int = Depends(validate_access_token),
):
    ...


@router.put(
    "/article/{article_id}",
    response_model=ArticleSchema,
    summary="Updates article by id",
    description="""This method will raise 403 HTTP status code (Forbidden) if article is
    private and user is not its author""",
)
@inject
def update_article(
    article_id: int,
    article: ArticleSchema,
    article_service: ArticleService = Depends(Provide[AppContainer.article_service]),
    user_id: int = Depends(validate_access_token),
):
    ...


@router.get(
    "/article/{article_id}",
    response_model=ArticleSchema,
    summary="Get article by id",
    description="""Raise 403 status code (Forbidden) if article exists, but is
    private and user is not its author""",
)
def get_article_by_id(
    article_id: int,
    article_service: ArticleService = Depends(Provide[AppContainer.article_service]),
    user_id: int = Depends(validate_access_token),
):
    ...


@router.get(
    "/user/{user_id}/articles_ids",
    response_model=list[int],
    summary="Get ids of user's articles",
    description="""Returns only available articles, e.g if it is requested by other
    users, then only public articles are returned.""",
)
def get_user_articles(
    user_id: int,
    article_service: ArticleService = Depends(Provide[AppContainer.article_service]),
    curr_user_id: int = Depends(validate_access_token),
):
    ...
