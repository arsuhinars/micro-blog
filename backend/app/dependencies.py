from dependency_injector.wiring import Provide, inject
from fastapi import Depends

from app.container import AppContainer
from app.exceptions import AuthorizationRequiredError
from app.services import AuthService


@inject
async def validate_access_token(
    access_token: str | None = None,
    auth_service: AuthService = Depends(Provide[AppContainer.auth_service]),
) -> int:
    """
    Validate `access_token` provided by client in query parameters. Can be
    used as the FastAPI dependency.

    Returns:
        User id from decoded token

    Raises:
        AuthorizationRequiredError: if provided `access_token` is `None`
    """
    if access_token is None:
        raise AuthorizationRequiredError()
    return await auth_service.validate_access_token(access_token)


@inject
async def validate_optional_access_token(
    access_token: str | None = None,
    auth_service: AuthService = Depends(Provide[AppContainer.auth_service]),
) -> int | None:
    """
    Validate `access_token` provided by client in query parameters. Can be used
    as the FastAPI dependency.

    Returns:
        User id from decoded token or `None` if `access_token` is not given
    """
    if access_token is None:
        return None
    return await auth_service.validate_access_token(access_token)
