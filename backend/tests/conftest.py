from datetime import date

import pytest
from pytest import MonkeyPatch
from pytest_mock import MockerFixture
from dependency_injector import providers
from fastapi.testclient import TestClient
from faker import Faker

from app.container import AppContainer
from app.models import User, Article
from app.schemas import UserSchema
from app.factory import create_app
from .defines import *


class MockedRedis:
    def __init__(self):
        self.data = {}
    
    async def get(self, name: str):
        return self.data.get(name)
    
    async def set(self, name: str, value: str, *args):
        self.data[name] = value
    
    async def delete(self, *keys: list[str]):
        for key in keys:
            self.data.pop(key, None)


@pytest.fixture(scope='function')
def mock_redis_database(mocker: MockerFixture):
    redis_mock = mocker.patch('app.redis.RedisDatabase')
    redis_mock.client.return_value.__aenter__.return_value = MockedRedis()
    return redis_mock


@pytest.fixture(scope='function')
def mock_database(mocker: MockerFixture):
    return mocker.patch('app.db.Database')


class FakeUserRepository:
    def __init__(self):
        self.id_table: dict[int, User] = {}
        self.email_table: dict[str, User] = {}
        self.counter = 1

    async def get_by_id(self, id: int) -> User | None:
        return self.id_table.get(id)
    
    async def get_by_email(self, email: str) -> User | None:
        return self.email_table.get(email)

    async def save(self, user: User) -> User:
        if user.id is None:
            user.id = self.counter
            user.creation_date = date.today()
            user.is_active = True
            self.counter += 1

        self.id_table[user.id] = user
        self.email_table[user.email] = user
        return user


class FakeArticleRepository:
    def __init__(self):
        self.id_table: dict[int, Article] = {}
        self.author_table: dict[int, set[int]] = {}
        self.counter = 1

    async def get_by_id(self, id: int) -> Article | None:
        return self.id_table.get(id)

    async def get_by_author_id(self, author_id: int) -> list[Article]:
        return list(
            map(
                self.author_table.get(author_id, []),
                lambda id: self.id_table[id]
            )
        )
    
    async def save(self, article: Article) -> Article:
        if article.id is None:
            article.id = self.counter
            self.counter += 1

        self.id_table[article.id] = article
        self.author_table[article.author_id].add(article.id)
        return article


@pytest.fixture(scope='function')
def test_client(
    monkeypatch: MonkeyPatch,
    mocker: MockerFixture,
    mock_redis_database,
    mock_database
):
    monkeypatch.setenv('DATABASE_URL', '')
    monkeypatch.setenv('REDIS_URL', '')
    monkeypatch.setenv('SECRET_KEY', TEST_SECRET_KEY)

    container = AppContainer()
    container.redis_db.override(mock_redis_database)
    container.db.override(mock_database)
    container.user_repository.override(
        providers.Singleton(FakeUserRepository)
    )
    container.article_repository.override(
        providers.Singleton(FakeArticleRepository)
    )

    mocker.patch('app.factory.AppContainer', lambda: container)

    return TestClient(create_app())


@pytest.fixture(scope='function')
async def create_fake_user(test_client: TestClient, faker: Faker):
    email = faker.email()
    password = faker.password()
    
    container: AppContainer = test_client.app.container
    user: UserSchema = await container.user_service().create(
        email, password, faker.first_name()
    )

    return ( user, email, password )
