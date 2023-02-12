from fastapi import Depends
from dependency_injector.wiring import inject, Provide

from app.container import AppContainer
from app.services import AuthService
from app.exceptions import AuthorizationRequiredError


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
    """
    if access_token is None:
        raise AuthorizationRequiredError()
    return await auth_service.validate_access_token(access_token)
