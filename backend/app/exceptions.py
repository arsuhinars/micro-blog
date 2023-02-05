from typing import ClassVar


class AppException(Exception):
    """ Common class for all API exceptions """
    status_code: ClassVar[int] = 500
    error_code: ClassVar[int] = 0
    details: ClassVar[str] = 'App exception'

    def __init__(
        self,
        status_code: int | None,
        error_code: int | None,
        details: str | None
    ):
        if status_code is None:
            status_code = self.__class__.status_code
        
        if error_code is None:
            error_code = self.__class__.error_code
        
        if details is None:
            details = self.__class__.details

        self.status_code = status_code
        self.error_code = error_code
        self.details = details


class UnexpectedError(AppException):
    status_code = 500
    error_code = 1
    details = 'Unexpected error'


class InvalidInputFormatError(AppException):
    status_code = 400
    error_code = 2
    details = 'Invalid input format'
    

class AuthorizationRequiredError(AppException):
    status_code = 401
    error_code = 3
    details = 'Authorization required'


class AccessDeniedError(AppException):
    status_code = 403
    error_code = 4
    details = 'Access is denied'


class ContentNotFoundError(AppException):
    status_code = 404
    error_code = 5
    details = 'Content was not found'


class InvalidTokenError(AppException):
    status_code = 400
    error_code = 6
    details = 'Invalid token'


class ExpiredTokenError(AppException):
    status_code = 400
    error_code = 7
    details = 'The token is expired'


class TakenLoginError(AppException):
    status_code = 400
    error_code = 8
    details = 'This login is already taken'
