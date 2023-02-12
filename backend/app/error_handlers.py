from http import HTTPStatus

from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse

from app.exceptions import (
    AccessDeniedError,
    AppException,
    AuthorizationRequiredError,
    ContentNotFoundError,
    InvalidInputFormatError,
    UnexpectedError,
)
from app.schemas import ErrorResponse


def handle_app_exception(req, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error_code=exc.error_code, details=exc.details).dict(),
    )


def handle_validation_error(req, exc: RequestValidationError):
    return handle_app_exception(req, InvalidInputFormatError())


def handle_http_exception(req, exc: HTTPException):
    match exc.status_code:
        case HTTPStatus.UNAUTHORIZED:
            handle_app_exception(req, AuthorizationRequiredError(details=exc.detail))
        case HTTPStatus.FORBIDDEN:
            handle_app_exception(req, AccessDeniedError(details=exc.detail))
        case HTTPStatus.NOT_FOUND:
            handle_app_exception(req, ContentNotFoundError(details=exc.detail))
        case HTTPStatus.UNPROCESSABLE_ENTITY:
            handle_app_exception(req, InvalidInputFormatError(details=exc.detail))
        case HTTPStatus.INTERNAL_SERVER_ERROR:
            handle_app_exception(req, UnexpectedError(details=exc.detail))
        case _:
            handle_app_exception(
                req,
                AppException(
                    status_code=exc.status_code, error_code=0, details=exc.detail
                ),
            )
