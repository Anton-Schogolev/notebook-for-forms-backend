import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def registration_payload() -> dict[str, str | bool]:
    return {
        "username": "alice",
        "password": "test_password",
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
            "grant_type": "password",
            "username": registration_payload["username"],
            "password": registration_payload["password"],
        },
    )
    assert response.status_code == 200, (
        "POST /auth/token should accept valid credentials"
    )
    assert response.headers["Cache-Control"] == "no-store"
    assert response.headers["Pragma"] == "no-cache"
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
            "grant_type": "password",
            "username": registration_payload["username"],
            "password": "wrong_password",
        },
    )

    assert response.json()["error"] == "invalid_grant"
    assert response.status_code == 400, (
        "POST /auth/token should reject the wrong password"
    )


def test_login_rejects_unknown_username(client: TestClient) -> None:
    response = client.post(
        "/auth/token",
        data={
            "grant_type": "password",
            "username": "unknown_user",
            "password": "test-password",
        },
    )

    assert response.status_code == 400
    assert response.json()["error"] == "invalid_grant"


def test_profile_requires_bearer_token(client: TestClient) -> None:
    response = client.get("/auth/me")

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_profile_rejects_invalid_bearer_token(client: TestClient) -> None:
    response = client.get("/auth/me", headers={"Authorization": "Bearer invalid-token"})

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


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
    ("form", "error"),
    [
        ("username=alice&password=test", "invalid_request"),
        ("grant_type=password&password=test", "invalid_request"),
        ("grant_type=password&username=alice", "invalid_request"),
        ("grant_type=password&username=alice&password=", "invalid_request"),
        (
            "grant_type=password&username=alice&username=bob&password=test",
            "invalid_request",
        ),
        ("grant_type=client_credentials", "unsupported_grant_type"),
    ],
)
def test_login_rejects_invalid_form(client: TestClient, form: str, error: str) -> None:
    response = client.post(
        "/auth/token",
        content=form,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 400
    assert response.json()["error"] == error


def test_token_openapi_contract(client: TestClient) -> None:
    document = client.get("/openapi.json").json()
    operation = document["paths"]["/auth/token"]["post"]
    assert set(operation["responses"]) == {"200", "400"}
    schema = operation["requestBody"]["content"]["application/x-www-form-urlencoded"][
        "schema"
    ]
    schema = document["components"]["schemas"][schema["$ref"].split("/")[-1]]
    assert set(schema["required"]) == {"grant_type", "username", "password"}
