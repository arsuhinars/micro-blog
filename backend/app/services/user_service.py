import os
from hashlib import pbkdf2_hmac

from email_validator import EmailNotValidError, validate_email

import app.config as config
from app.exceptions import (
    ContentNotFoundError,
    InvalidInputFormatError,
    TakenLoginError,
)
from app.models import User
from app.repositories import UserRepository
from app.schemas import UserSchema


class UserService:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    @staticmethod
    def get_password_key(password: str, salt: bytes) -> bytes:
        return pbkdf2_hmac(
            config.PASSWORD_HASH_ALGORITHM,
            password.encode("utf-8"),
            salt,
            config.PASSWORD_HASH_ITERATIONS,
            config.PASSWORD_KEY_LENGTH,
        )

    async def create(self, email: str, password: str, display_name: str) -> UserSchema:
        try:
            normalized_email: str = validate_email(
                email, check_deliverability=False
            ).email
        except EmailNotValidError:
            raise InvalidInputFormatError()

        if (await self._user_repo.get_by_email(email)) is not None:
            raise TakenLoginError(details="This email is already taken")

        password_salt = os.urandom(config.PASSWORD_SALT_LENGTH)
        password_key = self.get_password_key(password, password_salt)

        user = User(
            email=normalized_email,
            password_salt=password_salt,
            password_key=password_key,
            display_name=display_name.strip(),
        )

        return UserSchema.from_orm(await self._user_repo.save(user))

    async def get_by_id(self, id: int) -> UserSchema | None:
        user = await self._user_repo.get_by_id(id)
        if user is None or not user.is_active:
            return None
        return UserSchema.from_orm(user)

    async def get_by_email(self, email: str) -> UserSchema | None:
        user = await self._user_repo.get_by_email(email)
        if user is None or not user.is_active:
            return None
        return UserSchema.from_orm(user)

    async def update(self, user: UserSchema) -> UserSchema:
        db_user = await self._user_repo.get_by_id(user.id)
        if db_user is None or not db_user.is_active:
            raise ContentNotFoundError()

        db_user.display_name = user.display_name.strip()
        db_user = await self._user_repo.save(db_user)

        return UserSchema.from_orm(db_user)

    async def check_credentials(self, email: str, password: str) -> bool:
        user = await self._user_repo.get_by_email(email)
        if user is None or not user.is_active:
            return False

        password_key = self.get_password_key(password, user.password_salt)
        return user.password_key == password_key
