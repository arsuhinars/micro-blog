from dependency_injector import containers, providers

from app.db import Database
from app.redis import RedisDatabase
from app.repositories import ArticleRepository, UserRepository
from app.services import ArticleService, AuthService, UserService


class AppContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    db = providers.Singleton(Database, url=config.database_url)
    redis_db = providers.Singleton(RedisDatabase, url=config.redis_url)

    user_repository = providers.Singleton(
        UserRepository, session_factory=db.provided.session
    )
    article_repository = providers.Singleton(
        ArticleRepository, session_factory=db.provided.session
    )

    user_service = providers.Singleton(UserService, user_repo=user_repository)
    article_service = providers.Singleton(ArticleService)
    auth_service = providers.Singleton(
        AuthService,
        redis_client_factory=redis_db.provided.client,
        secret_key=config.secret_key,
    )

    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.endpoints.auth",
            "app.endpoints.user",
            "app.endpoints.article",
            "app.dependencies",
        ]
    )
