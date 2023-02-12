from httpx import Response

from app.exceptions import AppException
from app.schemas import ErrorResponse


def assert_app_error(response: Response, exc: type[AppException]):
    error_response = ErrorResponse.parse_obj(response.json())

    assert response.status_code == exc.status_code
    assert error_response.error_code == exc.error_code
