from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError

from app.container import AppContainer
from app.endpoints.article import router as article_router
from app.endpoints.auth import router as auth_router
from app.endpoints.user import router as user_router
from app.error_handlers import (
    handle_app_exception,
    handle_http_exception,
    handle_validation_error,
)
from app.exceptions import AppException
from app.settings import AppSettings

APP_DESCRIPTION = """

Source code is available on [GitHub](https://github.com/arsuhinars/micro-blog)

"""


def create_app() -> FastAPI:
    container = AppContainer()
    container.config.from_pydantic(AppSettings())

    app = FastAPI(
        redoc_url=None,
        title="Micro-blog",
        description=APP_DESCRIPTION,
        contact={"name": "Arseny Fedorov", "url": "https://t.me/arsuhinars"},
        license_info={"name": "MIT License"},
    )
    app.container = container

    app.include_router(user_router)
    app.include_router(article_router)
    app.include_router(auth_router)

    app.add_exception_handler(AppException, handle_app_exception)
    app.add_exception_handler(RequestValidationError, handle_validation_error)
    app.add_exception_handler(HTTPException, handle_http_exception)

    db = container.db()

    @app.on_event("startup")
    async def on_startup():
        await db.create_database()

    return app
