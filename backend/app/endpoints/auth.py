from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide
from email_validator import validate_email, EmailNotValidError

from app.container import AppContainer
from app.services import AuthService, UserService
from app.schemas import AuthTokens
from app.exceptions import InvalidInputFormatError, InvalidCredentialsError


router = APIRouter(tags=['Auth'])


@router.get(
    '/tokens',
    response_model=AuthTokens,
    summary='Authorize user and get auth tokens',
    description="""
        This method returns two tokens. First is `access_token`. It's used in
        other methods for getting access. `access_token` lifetime is short.
        Second token is `refresh_token`. It is used for getting new pair of
        tokens when old ones are expired. `refresh_token` is long living.
    """
)
@inject
async def get_tokens(
    email: str | None = None,
    password: str | None = None,
    refresh_token: str | None = None,
    user_service: UserService = Depends(Provide[AppContainer.user_service]),
    auth_service: AuthService = Depends(Provide[AppContainer.auth_service])
):
    if ((email is None) or (password is None)) and (refresh_token is None):
        raise InvalidInputFormatError(
            details='User credentials or refresh token should be provided'
        )
    if email is not None:
        try:
            email = validate_email(email, check_deliverability=False).email
        except EmailNotValidError:
            raise InvalidInputFormatError()

        if not await user_service.check_credentials(
            email,
            password
        ):
            raise InvalidCredentialsError()

        user_id = (await user_service.get_by_email(email)).id
    else:
        user_id = await auth_service.validate_refresh_token(refresh_token)
        await auth_service.reset_refresh_token(refresh_token)

    return AuthTokens(
        access_token=await auth_service.generate_access_token(user_id),
        refresh_token=await auth_service.generate_refresh_token(user_id)
    )
