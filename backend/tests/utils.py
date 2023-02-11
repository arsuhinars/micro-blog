from httpx import Response

from app.schemas import ErrorResponse

from app.exceptions import AppException


def assert_app_error(response: Response, exc: AppException):
    assert response.status_code == exc.status_code
    assert ErrorResponse.parse_obj(response.json()).error_code == exc.error_code
