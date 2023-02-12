import os
from base64 import urlsafe_b64encode
from datetime import datetime, timedelta
from contextlib import AbstractAsyncContextManager
from typing import Callable

from redis.asyncio import Redis
from jose import jwt, ExpiredSignatureError, JWTError

import app.config as config
from app.exceptions import InvalidTokenError, ExpiredTokenError


class AuthService:
    def __init__(
        self,
        redis_client_factory: Callable[..., AbstractAsyncContextManager[Redis]],
        secret_key: str,
    ):
        self._redis_client_factory = redis_client_factory
        self._secret_key = secret_key

    async def generate_access_token(self, user_id: int) -> str:
        return jwt.encode(
            {
                "exp": datetime.utcnow()
                + timedelta(seconds=config.ACCESS_TOKEN_LIFETIME),
                "aud": str(user_id),
            },
            self._secret_key,
            config.ACCESS_TOKEN_ALGORITHM,
        )

    async def generate_refresh_token(self, user_id: int) -> str:
        redis: Redis
        async with self._redis_client_factory() as redis:
            refresh_token: str = urlsafe_b64encode(
                os.urandom(config.REFRESH_TOKEN_SIZE)
            ).decode("utf-8")

            await redis.set(
                f"refresh_token:{refresh_token}:user_id",
                user_id,
                config.REFRESH_TOKEN_LIFETIME,
            )
            return refresh_token

    async def validate_access_token(self, access_token: str) -> int:
        """
        Validates access token provided by client. Raises exception if
        access_token is invalid.

        Args:
            access_token: Query parameter provided by client

        Returns:
            User id from decoded token

        Raises:
            ExpiredTokenError: Access token is expired
            InvalidTokenError: Access token is not valid
        """
        try:
            claims = jwt.decode(
                access_token,
                self._secret_key,
                config.ACCESS_TOKEN_ALGORITHM,
                {
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_aud": False,
                    "require_exp": True,
                    "require_aud": False,
                },
            )
            return int(claims.get("aud"))
        except ExpiredSignatureError:
            raise ExpiredTokenError()
        except JWTError:
            raise InvalidTokenError(details="Invalid access token")

    async def validate_refresh_token(self, refresh_token: str) -> int:
        """
        Validates refresh token provided by client. Raises exception if
        refresh_token is invalid.

        Args:
            refresh_token: Query parameter provided by client

        Returns:
            User id from decoded token

        Raises:
            InvalidTokenError: Refresh token is invalid
        """
        redis: Redis
        async with self._redis_client_factory() as redis:
            user_id: int = await redis.get(f"refresh_token:{refresh_token}:user_id")

            if user_id is None:
                raise InvalidTokenError(details="Invalid refresh token")

            return user_id

    async def reset_refresh_token(self, refresh_token: str):
        """Makes given refresh token invalid."""
        redis: Redis
        async with self._redis_client_factory() as redis:
            await redis.delete(f"refresh_token:{refresh_token}:user_id")
