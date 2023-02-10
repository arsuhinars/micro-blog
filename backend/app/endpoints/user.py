from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from app.container import AppContainer
from app.schemas import UserCreateSchema, UserSchema
from app.services import UserService
from app.dependencies import validate_access_token
from app.exceptions import ContentNotFoundError


router = APIRouter(prefix='/user', tags=['User'])


@router.post(
    '',
    response_model=UserSchema,
    summary='Create user profile',
    description='This method should be used for user registration'
)
@inject
async def create_user(
    user_create_data: UserCreateSchema,
    user_service: UserService = Depends(Provide[AppContainer.user_service])
):
    return await user_service.create(
        user_create_data.email,
        user_create_data.password,
        user_create_data.display_name
    )


@router.put(
    '',
    response_model=UserSchema,
    summary='Update current user'
)
@inject
async def update_current_user(
    user_data: UserSchema,
    user_service: UserService = Depends(Provide[AppContainer.user_service]),
    user_id: int = Depends(validate_access_token)
):
    user_data.id = user_id
    return await user_service.update(user_data)


@router.get(
    '',
    response_model=UserSchema,
    summary='Get current user'
)
@inject
async def get_current_user(
    user_service: UserService = Depends(Provide[AppContainer.user_service]),
    user_id: int = Depends(validate_access_token)
):
    return await user_service.get_by_id(user_id)


@router.get(
    '/{id}',
    response_model=UserSchema,
    summary='Get user by id'
)
@inject
async def get_user_by_id(
    id: int,
    user_service: UserService = Depends(Provide[AppContainer.user_service]),
):
    user = await user_service.get_by_id(id)
    if user is None:
        raise ContentNotFoundError()
    return user
