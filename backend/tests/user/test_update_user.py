from datetime import date
from http import HTTPStatus

from faker import Faker
from fastapi.testclient import TestClient

import tests.defines as defines
from app.exceptions import (
    AuthorizationRequiredError,
    InvalidInputFormatError,
    InvalidTokenError,
)
from app.schemas import UserSchema
from tests.utils import assert_app_error


def test_valid_data(test_client: TestClient, faker: Faker, test_user, access_token):
    user: UserSchema = test_user[0]
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


def test_changing_wrong_data(
    test_client: TestClient, faker: Faker, test_user, access_token
):
    user: UserSchema = test_user[0]
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


def test_invalid_data(test_client: TestClient, access_token):
    access_token: str

    response = test_client.put(
        defines.USER_PATH, params={"access_token": access_token}, json={}
    )

    assert_app_error(response, InvalidInputFormatError)


def test_invalid_token(test_client: TestClient, faker: Faker, invalid_access_token):
    response = test_client.put(
        defines.USER_PATH,
        params={"access_token": invalid_access_token},
        json={"display_name": faker.first_name()},
    )

    assert_app_error(response, InvalidTokenError)

    response = test_client.put(
        defines.USER_PATH,
        json={"display_name": faker.first_name()},
    )

    assert_app_error(response, AuthorizationRequiredError)
