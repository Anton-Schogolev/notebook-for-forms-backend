import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def registration_payload() -> dict[str, str | bool]:
    return {
        "username": "alice",
        "password": "test-password",
        "is_encryption_enabled": True,
    }


def test_register_login_and_get_profile(
    client: TestClient, registration_payload: dict[str, str | bool]
) -> None:
    response = client.post("/auth/register", json=registration_payload)
    assert response.status_code == 201, "POST /auth/register should create the account"

    response = client.post(
        "/auth/token",
        data={
            "username": registration_payload["username"],
            "password": registration_payload["password"],
        },
    )
    assert response.status_code == 200, (
        "POST /auth/token should accept valid credentials"
    )
    token = response.json()
    assert token.get("token_type") == "bearer", "POST /auth/token should return bearer"
    access_token = token.get("access_token")
    assert isinstance(access_token, str), (
        "POST /auth/token should return an access token"
    )
    assert access_token, "POST /auth/token returned an empty access token"

    response = client.get(
        "/auth/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200, "GET /auth/me should accept the issued token"
    assert response.json() == {
        "username": registration_payload["username"],
        "is_encryption_enabled": registration_payload["is_encryption_enabled"],
    }, "GET /auth/me should return the registered username and encryption preference"


def test_register_rejects_duplicate_username(
    client: TestClient, registration_payload: dict[str, str | bool]
) -> None:
    response = client.post("/auth/register", json=registration_payload)
    assert response.status_code == 201, "Initial registration should succeed"

    response = client.post(
        "/auth/register", json={**registration_payload, "password": "other-password"}
    )

    assert response.status_code == 409, (
        "Second registration should reject the duplicate"
    )


def test_login_rejects_wrong_password(
    client: TestClient, registration_payload: dict[str, str | bool]
) -> None:
    response = client.post("/auth/register", json=registration_payload)
    assert response.status_code == 201, "Registration should succeed before login"

    response = client.post(
        "/auth/token",
        data={
            "username": registration_payload["username"],
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401, (
        "POST /auth/token should reject the wrong password"
    )


def test_login_rejects_unknown_username(client: TestClient) -> None:
    response = client.post(
        "/auth/token",
        data={"username": "unknown_user", "password": "test-password"},
    )

    assert response.status_code == 401


def test_profile_requires_bearer_token(client: TestClient) -> None:
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_profile_rejects_invalid_bearer_token(client: TestClient) -> None:
    response = client.get("/auth/me", headers={"Authorization": "Bearer invalid-token"})

    assert response.status_code == 401


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("username", "invalid-user"),
        ("password", "abc"),
        ("password", "a" * 17),
    ],
)
def test_register_rejects_invalid_fields(
    client: TestClient,
    registration_payload: dict[str, str | bool],
    field: str,
    value: str,
) -> None:
    response = client.post(
        "/auth/register", json={**registration_payload, field: value}
    )

    assert response.status_code == 422, (
        "POST /auth/register should reject invalid input"
    )
    assert any(
        error["loc"] == ["body", field] for error in response.json()["detail"]
    ), f"Registration validation should identify {field}"


@pytest.mark.parametrize(
    ("data", "missing_field"),
    [
        ({"username": "alice"}, "password"),
        ({"password": "test-password"}, "username"),
    ],
)
def test_login_requires_form_fields(
    client: TestClient, data: dict[str, str], missing_field: str
) -> None:
    response = client.post("/auth/token", data=data)

    assert response.status_code == 422, (
        "POST /auth/token should reject incomplete input"
    )
    assert any(
        error["loc"] == ["body", missing_field] for error in response.json()["detail"]
    ), f"Login validation should identify the missing {missing_field} field"
