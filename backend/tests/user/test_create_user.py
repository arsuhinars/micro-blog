from http import HTTPStatus

from faker import Faker
from fastapi.testclient import TestClient

import tests.defines as defines
from app.exceptions import InvalidInputFormatError, TakenLoginError
from app.schemas import UserCreateSchema, UserSchema
from tests.utils import assert_app_error


def test_valid_data(test_client: TestClient, faker: Faker):
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


def test_existing_credentials(test_client: TestClient, faker: Faker, test_user):
    user: UserSchema = test_user[0]

    response = test_client.post(
        defines.USER_PATH,
        json={
            "email": user.email,
            "password": faker.password(),
            "display_name": faker.first_name(),
        },
    )

    assert_app_error(response, TakenLoginError)


def test_invalid_email(test_client: TestClient, faker: Faker):
    response = test_client.post(
        defines.USER_PATH,
        json={
            "email": "invalid-email",
            "password": faker.password(),
            "display_name": faker.first_name(),
        },
    )

    assert_app_error(response, InvalidInputFormatError)


def test_missing_fields(test_client: TestClient, faker: Faker):
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


def test_blank_fields(test_client: TestClient, faker: Faker):
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
