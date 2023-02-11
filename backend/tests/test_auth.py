import os
from base64 import urlsafe_b64encode
from datetime import datetime, timedelta
from http import HTTPStatus

from faker import Faker
from fastapi.testclient import TestClient
from jose import jwt

import app.config as config
from app.schemas import UserSchema, AuthTokens
from app.exceptions import *
from tests.utils import assert_app_error
from tests.defines import *


def test_authorize(test_client: TestClient, create_fake_user):
    user: UserSchema = create_fake_user[0]
    email: str = create_fake_user[1]
    password: str = create_fake_user[2]
    
    # Test user credentials
    response = test_client.get(
        TOKENS_PATH,
        params={
            'email': email,
            'password': password
        }
    )
    
    assert response.status_code == HTTPStatus.OK
    
    auth_tokens = AuthTokens.parse_obj(response.json())

    # Test access token
    response = test_client.get(
        USER_PATH,
        params={
            'access_token': auth_tokens.access_token
        }
    )

    assert response.status_code == HTTPStatus.OK

    # Test refresh token
    response = test_client.get(
        TOKENS_PATH,
        params={
            'refresh_token': auth_tokens.refresh_token
        }
    )

    assert response.status_code == HTTPStatus.OK

    new_auth_tokens = AuthTokens.parse_obj(response.json())
    assert new_auth_tokens.refresh_token != auth_tokens.refresh_token

    # Test expired refresh token
    response = test_client.get(
        TOKENS_PATH,
        params={
            'refresh_token': auth_tokens.refresh_token
        }
    )

    assert_app_error(response, InvalidTokenError)


def test_invalid_user(
    test_client: TestClient,
    faker: Faker
):
    email: str = faker.email()
    password: str = faker.password()

    response = test_client.get(
        TOKENS_PATH,
        params={
            'email': email,
            'password': password
        }
    )

    assert_app_error(response, InvalidCredentialsError)


def test_invalid_tokens(test_client: TestClient, create_fake_user):
    # Test invalid access token
    user: UserSchema = create_fake_user[0]
    access_token = jwt.encode(
        {
            'exp': datetime.utcnow() + timedelta(seconds=config.ACCESS_TOKEN_LIFETIME),
            'aud': str(user.id)
        },
        FAKE_SECRET_KEY,
        config.ACCESS_TOKEN_ALGORITHM
    )

    response = test_client.get(
        USER_PATH,
        params={
            'access_token': access_token
        }
    )

    assert_app_error(response, InvalidTokenError)

    # Test invalid refresh token
    refresh_token: str = urlsafe_b64encode(
        os.urandom(config.REFRESH_TOKEN_SIZE)
    )

    response = test_client.get(
        TOKENS_PATH,
        params={
            'refresh_token': refresh_token
        }
    )

    assert_app_error(response, InvalidTokenError)


def test_invalid_request_body(test_client: TestClient, create_fake_user):
    email: str = create_fake_user[1]
    password: str = create_fake_user[2]

    response = test_client.get(
        TOKENS_PATH,
        params={}
    )

    assert_app_error(response, InvalidInputFormatError)

    response = test_client.get(
        TOKENS_PATH,
        params={
            'email': email
        }
    )

    assert_app_error(response, InvalidInputFormatError)

    response = test_client.get(
        TOKENS_PATH,
        params={
            'password': password
        }
    )

    assert_app_error(response, InvalidInputFormatError)