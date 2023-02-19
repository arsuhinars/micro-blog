from fastapi.testclient import TestClient

import tests.defines as defines
from app.exceptions import AuthorizationRequiredError, InvalidTokenError
from app.schemas import UserSchema
from tests.utils import assert_app_error


def test_valid_data(test_client: TestClient, test_user, access_token):
    user: UserSchema = test_user[0]

    response = test_client.get(defines.USER_PATH, params={"access_token": access_token})

    received_user = UserSchema.parse_obj(response.json())

    assert received_user.dict() == user.dict()


def test_invalid_token(test_client: TestClient, test_user, invalid_access_token):
    response = test_client.get(
        defines.USER_PATH, params={"access_token": invalid_access_token}
    )

    assert_app_error(response, InvalidTokenError)

    response = test_client.get(defines.USER_PATH)

    assert_app_error(response, AuthorizationRequiredError)
