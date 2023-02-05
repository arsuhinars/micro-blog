from fastapi import FastAPI

from app.container import AppContainer
from app.endpoints.user import router as user_router
from app.endpoints.article import router as article_router
from app.endpoints.auth import router as auth_router


def create_app() -> FastAPI:
    container = AppContainer()

    app = FastAPI()
    app.container = container
    app.include_router(user_router)
    app.include_router(article_router)
    app.include_router(auth_router)
    return app


app = create_app()
