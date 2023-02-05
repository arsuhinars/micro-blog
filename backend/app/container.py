from dependency_injector import containers, providers

from app.settings import AppSettings
from app.db import Database
from app.redis import RedisDatabase
from app.repositories import UserRepository, ArticleRepository
from app.services import UserService, ArticleService, AuthService


class AppContainer(containers.DeclarativeContainer):
    config = providers.Configuration(pydantic_settings=[AppSettings()])

    db = providers.Singleton(Database, url=config.database_url)
    redis_db = providers.Singleton(RedisDatabase, url=config.redis_url)

    user_repository = providers.Singleton(
        UserRepository,
        session_factory=db.provided.session
    )
    article_repository = providers.Singleton(
        ArticleRepository,
        session_factory=db.provided.session
    )

    user_service = providers.Singleton(UserService)
    article_service = providers.Singleton(ArticleService)
    auth_service = providers.Singleton(AuthService)

    wiring_config = containers.WiringConfiguration(
        modules=[
            'app.endpoints.auth',
            'app.endpoints.user',
            'app.endpoints.article'
        ]
    )
