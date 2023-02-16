from datetime import date
from http import HTTPStatus

import pytest
from faker import Faker
from fastapi.testclient import TestClient

import tests.defines as defines
from app.container import AppContainer
from app.exceptions import (
    ContentNotFoundError,
    InvalidInputFormatError,
    TakenLoginError,
)
from app.schemas import UserCreateSchema, UserSchema
from tests.utils import assert_app_error


def test_user_creation(test_client: TestClient, faker: Faker):
    email = faker.email()
    password = faker.password()
    display_name = faker.first_name()

    response = test_client.post(
        defines.USER_PATH,
        json=UserCreateSchema(
            email=email, password=password, display_name=display_name
        ).dict(),
    )

    assert response.status_code == HTTPStatus.OK

    user = UserSchema.parse_obj(response.json())

    assert user.email == email
    assert user.display_name == display_name


def test_creation_existing_user(test_client: TestClient, faker: Faker, fake_user):
    user: UserSchema = fake_user[0]

    response = test_client.post(
        defines.USER_PATH,
        json={
            "email": user.email,
            "password": faker.password(),
            "display_name": faker.first_name(),
        },
    )

    assert_app_error(response, TakenLoginError)


def test_creation_with_invalid_email(test_client: TestClient, faker: Faker):
    response = test_client.post(
        defines.USER_PATH,
        json={
            "email": "invalid-email",
            "password": faker.password(),
            "display_name": faker.first_name(),
        },
    )

    assert_app_error(response, InvalidInputFormatError)


def test_creation_with_missing_fields(test_client: TestClient, faker: Faker):
    response = test_client.post(defines.USER_PATH, json={})

    assert_app_error(response, InvalidInputFormatError)

    response = test_client.post(
        defines.USER_PATH,
        json={"password": faker.password(), "display_name": faker.first_name()},
    )

    assert_app_error(response, InvalidInputFormatError)

    response = test_client.post(
        defines.USER_PATH,
        json={"email": faker.email(), "display_name": faker.first_name()},
    )

    assert_app_error(response, InvalidInputFormatError)

    response = test_client.post(
        defines.USER_PATH, json={"email": faker.email(), "password": faker.password()}
    )

    assert_app_error(response, InvalidInputFormatError)


def test_creation_with_empty_strings(test_client: TestClient, faker: Faker):
    response = test_client.post(
        defines.USER_PATH,
        json={
            "email": "",
            "password": faker.password(),
            "display_name": faker.first_name(),
        },
    )

    assert_app_error(response, InvalidInputFormatError)

    response = test_client.post(
        defines.USER_PATH,
        json={
            "email": faker.email(),
            "password": "",
            "display_name": faker.first_name(),
        },
    )

    assert_app_error(response, InvalidInputFormatError)

    response = test_client.post(
        defines.USER_PATH,
        json={"email": faker.email(), "password": faker.password(), "display_name": ""},
    )

    assert_app_error(response, InvalidInputFormatError)


def test_user_update(test_client: TestClient, faker: Faker, fake_user, access_token):
    user: UserSchema = fake_user[0]
    access_token: str

    new_display_name = faker.first_name()

    response = test_client.put(
        defines.USER_PATH,
        params={"access_token": access_token},
        json={"display_name": new_display_name},
    )

    assert response.status_code == HTTPStatus.OK

    updated_user = UserSchema.parse_obj(response.json())

    assert updated_user.id == user.id
    assert updated_user.email == user.email
    assert updated_user.creation_date == user.creation_date
    assert updated_user.display_name == new_display_name
    assert updated_user.display_name != user.display_name


def test_update_wrong_data(
    test_client: TestClient, faker: Faker, fake_user, access_token
):
    user: UserSchema = fake_user[0]
    access_token: str

    response = test_client.put(
        defines.USER_PATH,
        params={"access_token": access_token},
        json={"id": user.id + 1, "display_name": user.display_name},
    )

    assert user.id == response.json()["id"]

    response = test_client.put(
        defines.USER_PATH,
        params={"access_token": access_token},
        json={"email": faker.email(), "display_name": user.display_name},
    )

    assert user.email == response.json()["email"]

    response = test_client.put(
        defines.USER_PATH,
        params={"access_token": access_token},
        json={
            "creation_date": date(2000, 1, 1).isoformat(),
            "display_name": user.display_name,
        },
    )

    assert user.creation_date == date.fromisoformat(response.json()["creation_date"])


def test_update_with_invalid_data(test_client: TestClient, access_token):
    access_token: str

    response = test_client.put(
        defines.USER_PATH, params={"access_token": access_token}, json={}
    )

    assert_app_error(response, InvalidInputFormatError)


def test_current_user_get(test_client: TestClient, fake_user, access_token):
    user: UserSchema = fake_user[0]
    access_token: str

    response = test_client.get(defines.USER_PATH, params={"access_token": access_token})

    received_user = UserSchema.parse_obj(response.json())

    assert received_user.dict() == user.dict()


@pytest.mark.parametrize("fake_users", [10], indirect=True)
def test_users_getting(test_client: TestClient, fake_users: list[UserSchema]):
    for user in fake_users:
        response = test_client.get(defines.USER_PATH + f"/{user.id}")

        received_user = UserSchema.parse_obj(response.json())
        assert received_user.dict() == user.dict()


async def test_inactive_user(test_client: TestClient, fake_user):
    user_schema: UserSchema = fake_user[0]
    container: AppContainer = test_client.app.container
    user_repo = container.user_repository()

    user = await user_repo.get_by_id(user_schema.id)
    user.is_active = False
    await user_repo.save(user)

    response = test_client.get(defines.USER_PATH + f"/{user.id}")
    assert_app_error(response, ContentNotFoundError)
