import pytest
from fastapi.testclient import TestClient

import tests.defines as defines
from app.container import AppContainer
from app.exceptions import ContentNotFoundError
from app.schemas import UserSchema
from tests.utils import assert_app_error


@pytest.mark.parametrize("test_users", [10], indirect=True)
def test_users_getting(test_client: TestClient, test_users: list[UserSchema]):
    for user in test_users:
        response = test_client.get(defines.USER_PATH + f"/{user.id}")

        received_user = UserSchema.parse_obj(response.json())
        assert received_user.dict() == user.dict()


async def test_inactive_user(test_client: TestClient, test_user):
    user_schema: UserSchema = test_user[0]
    container: AppContainer = test_client.app.container
    user_repo = container.user_repository()

    user = await user_repo.get_by_id(user_schema.id)
    user.is_active = False
    await user_repo.save(user)

    response = test_client.get(defines.USER_PATH + f"/{user.id}")
    assert_app_error(response, ContentNotFoundError)
