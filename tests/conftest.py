from collections.abc import AsyncIterator, Iterator
from contextlib import AsyncExitStack
from secrets import token_hex

import pytest
from fastapi.testclient import TestClient
from pydantic import Field
from sqlalchemy.engine import make_url
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from src.dependencies.config import Settings, get_settings
from src.dependencies.database import get_session
from src.main import create_app


class TestSettings(Settings):
    database_url: str = Field(
        validation_alias="TEST_DATABASE_URL", exclude=True, repr=False
    )


@pytest.fixture
def client() -> Iterator[TestClient]:
    settings = TestSettings(
        admin_username="test-admin",
        admin_password="test-password",
        origins=[],
        secret=token_hex(32),
        access_token_expire_minutes=5,
    )
    url = make_url(settings.database_url)
    if (
        url.drivername != "postgresql+psycopg"
        or url.database != "notebook_auth_test"
        or url.username != "notebook_auth_test"
    ):
        pytest.fail("Use the dedicated notebook_auth_test database and user.")

    app = create_app(settings)
    app.dependency_overrides[get_settings] = lambda: settings
    resources = AsyncExitStack()

    async def configure_test_session() -> None:
        connection = await resources.enter_async_context(app.state.engine.connect())
        transaction = await connection.begin()
        resources.push_async_callback(transaction.rollback)
        await connection.run_sync(SQLModel.metadata.create_all)

        async def test_session() -> AsyncIterator[AsyncSession]:
            # Service commits release savepoints inside the test's outer transaction.
            async with AsyncSession(
                connection,
                expire_on_commit=False,
                join_transaction_mode="create_savepoint",
            ) as session:
                yield session

        app.dependency_overrides[get_session] = test_session

    with TestClient(app, raise_server_exceptions=False) as test_client:
        assert test_client.portal is not None
        try:
            test_client.portal.call(configure_test_session)
            yield test_client
        finally:
            # Closing the connection rolls back the test's schema and data.
            test_client.portal.call(resources.aclose)
