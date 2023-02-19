from datetime import date, datetime, timedelta

import pytest
from dependency_injector import providers
from faker import Faker
from fastapi.testclient import TestClient
from jose import jwt
from pytest import FixtureRequest, MonkeyPatch
from pytest_mock import MockerFixture

import app.config as config
import tests.defines as defines
from app.container import AppContainer
from app.factory import create_app
from app.models import Article, User
from app.schemas import UserSchema


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


@pytest.fixture
def mock_redis_database(mocker: MockerFixture):
    redis_mock = mocker.patch("app.redis.RedisDatabase")
    redis_mock.client.return_value.__aenter__.return_value = MockedRedis()
    return redis_mock


@pytest.fixture
def mock_database(mocker: MockerFixture):
    return mocker.patch("app.db.Database")


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
            map(self.author_table.get(author_id, []), lambda id: self.id_table[id])
        )

    async def save(self, article: Article) -> Article:
        if article.id is None:
            article.id = self.counter
            self.counter += 1

        self.id_table[article.id] = article
        self.author_table[article.author_id].add(article.id)
        return article


@pytest.fixture
def test_client(
    monkeypatch: MonkeyPatch, mocker: MockerFixture, mock_redis_database, mock_database
):
    monkeypatch.setenv("DATABASE_URL", "")
    monkeypatch.setenv("REDIS_URL", "")
    monkeypatch.setenv("SECRET_KEY", defines.TEST_SECRET_KEY)

    container = AppContainer()
    container.redis_db.override(mock_redis_database)
    container.db.override(mock_database)
    container.user_repository.override(providers.Singleton(FakeUserRepository))
    container.article_repository.override(providers.Singleton(FakeArticleRepository))

    mocker.patch("app.factory.AppContainer", lambda: container)

    return TestClient(create_app())


@pytest.fixture
async def test_user(test_client: TestClient, faker: Faker):
    email = faker.email()
    password = faker.password()

    container: AppContainer = test_client.app.container
    user: UserSchema = await container.user_service().create(
        email, password, faker.first_name()
    )

    return (user, email, password)


@pytest.fixture
async def test_users(
    request: FixtureRequest, test_client: TestClient, faker: Faker
) -> list[UserSchema]:
    user_count: int = request.param

    container: AppContainer = test_client.app.container
    user_service = container.user_service()

    users = []
    for i in range(user_count):
        users.append(
            await user_service.create(
                faker.email(), faker.password(), faker.first_name()
            )
        )

    return users


@pytest.fixture
async def access_token(test_client: TestClient, test_user):
    user: UserSchema = test_user[0]
    container: AppContainer = test_client.app.container
    return await container.auth_service().generate_access_token(user.id)


@pytest.fixture
def fake_access_token(test_user):
    return jwt.encode(
        {
            "exp": datetime.utcnow() + timedelta(seconds=config.ACCESS_TOKEN_LIFETIME),
            "aud": str(test_user[0].id),
        },
        defines.FAKE_SECRET_KEY,
        config.ACCESS_TOKEN_ALGORITHM,
    )
