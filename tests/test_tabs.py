from uuid import uuid4

import pytest
from fastapi.testclient import TestClient


def sign_in(client: TestClient, username: str) -> dict[str, str]:
    credentials = {"username": username, "password": "test_password"}
    registration = client.post(
        "/auth/register", json={**credentials, "is_encryption_enabled": True}
    )
    assert registration.status_code == 201
    response = client.post("/auth/token", data={**credentials, "grant_type": "password"})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def authenticated_client(client: TestClient) -> TestClient:
    client.headers.update(sign_in(client, "alice"))
    return client


@pytest.mark.parametrize("title", ["A", "a" * 30])
def test_create_tab(authenticated_client: TestClient, title: str) -> None:
    tab = {"id": str(uuid4()), "title": title}
    response = authenticated_client.post("/tabs", json=tab)
    assert response.status_code == 201
    assert response.json() == {**tab, "version": 1}


def test_duplicate_tab_id(authenticated_client: TestClient) -> None:
    tab = {"id": str(uuid4()), "title": "Original"}
    assert authenticated_client.post("/tabs", json=tab).status_code == 201
    response = authenticated_client.post("/tabs", json={**tab, "title": "Duplicate"})
    assert response.status_code == 409


@pytest.mark.parametrize(
    ("field", "value"), [("id", "invalid"), ("title", ""), ("title", "a" * 31)]
)
def test_invalid_tab(authenticated_client: TestClient, field: str, value: str) -> None:
    tab = {"id": str(uuid4()), "title": "Notes"}
    tab[field] = value
    assert authenticated_client.post("/tabs", json=tab).status_code == 422


def test_list_empty_tabs(authenticated_client: TestClient) -> None:
    response = authenticated_client.get("/tabs")
    assert response.status_code == 200
    assert response.json() == []


def test_list_created_tabs(authenticated_client: TestClient) -> None:
    tabs = [{"id": str(uuid4()), "title": title} for title in ("Notes", "Tasks")]
    for tab in tabs:
        assert authenticated_client.post("/tabs", json=tab).status_code == 201

    response = authenticated_client.get("/tabs")
    assert response.status_code == 200
    listed = response.json()
    assert isinstance(listed, list)
    assert len(listed) == len(tabs)
    for tab in tabs:
        assert {**tab, "version": 1} in listed


def test_update_tab_increments_version(authenticated_client: TestClient) -> None:
    tab_id = str(uuid4())
    tab = {"id": tab_id, "title": "Draft"}
    assert authenticated_client.post("/tabs", json=tab).status_code == 201

    for version, title in [(2, "Reviewed"), (3, "Final")]:
        response = authenticated_client.put(f"/tabs/{tab_id}/metadata", json={"title": title})
        assert response.status_code == 200
        assert response.json() == {"id": tab_id, "title": title, "version": version}

    response = authenticated_client.get("/tabs")
    assert response.status_code == 200
    assert response.json() == [{"id": tab_id, "title": "Final", "version": 3}]


@pytest.mark.parametrize("method", ["POST", "GET", "PUT"])
def test_tabs_require_authentication(client: TestClient, method: str) -> None:
    tab_id = str(uuid4())
    path = "/tabs"
    payload = None
    if method == "POST":
        payload = {"id": tab_id, "title": "Notes"}
    elif method == "PUT":
        path = f"/tabs/{tab_id}/metadata"
        payload = {"title": "Renamed"}

    response = client.request(method, path, json=payload)
    assert response.status_code == 401


def test_users_list_only_their_own_tabs(client: TestClient) -> None:
    users = [
        (sign_in(client, username), {"id": str(uuid4()), "title": "Notes"})
        for username in ("alice", "bobby")
    ]
    for headers, tab in users:
        assert client.post("/tabs", headers=headers, json=tab).status_code == 201

    for headers, tab in users:
        response = client.get("/tabs", headers=headers)
        assert response.status_code == 200
        assert response.json() == [{**tab, "version": 1}]


def test_only_owner_can_rename_tab(client: TestClient) -> None:
    alice = sign_in(client, "alice")
    bob = sign_in(client, "bobby")
    tab = {"id": str(uuid4()), "title": "Draft"}
    assert client.post("/tabs", headers=alice, json=tab).status_code == 201

    path = f"/tabs/{tab['id']}/metadata"
    response = client.put(path, headers=bob, json={"title": "Bob's edit"})
    assert response.status_code == 404

    response = client.get("/tabs", headers=alice)
    assert response.status_code == 200
    assert response.json() == [{**tab, "version": 1}]

    response = client.put(path, headers=alice, json={"title": "Reviewed"})
    assert response.status_code == 200
    assert response.json() == {**tab, "title": "Reviewed", "version": 2}
