from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from httpx2 import Response

from .test_tabs import sign_in


@pytest.fixture
def owner(client: TestClient) -> dict[str, str]:
    return sign_in(client, "alice")


@pytest.fixture
def tab(client: TestClient, owner: dict[str, str]) -> dict[str, str]:
    data = {"id": str(uuid4()), "title": "Notebook"}
    assert client.post("/tabs", headers=owner, json=data).status_code == 201
    return data


def field(title: str, content: str) -> dict[str, str]:
    return {"id": str(uuid4()), "title": title, "content": content}


def assert_detail(
    response: Response, tab: dict[str, str], content: list[dict[str, str]]
) -> None:
    assert response.status_code == 200
    detail = response.json()
    assert detail["id"] == tab["id"]
    assert detail["title"] == tab["title"]
    assert type(detail["version"]) is int
    assert detail["content"] == content


def test_get_new_tab(
    client: TestClient, owner: dict[str, str], tab: dict[str, str]
) -> None:
    assert_detail(client.get(f"/tabs/{tab['id']}", headers=owner), tab, [])


def test_save_ordered_fields(
    client: TestClient, owner: dict[str, str], tab: dict[str, str]
) -> None:
    path = f"/tabs/{tab['id']}"
    content = [field("Zebra", "Last alphabetically"), field("Apple", "Second")]
    saved = client.put(f"{path}/content", headers=owner, json={"content": content})
    assert_detail(saved, tab, content)
    assert_detail(client.get(path, headers=owner), tab, content)


@pytest.mark.parametrize("clear", [False, True], ids=["replace", "clear"])
def test_replace_content(
    client: TestClient, owner: dict[str, str], tab: dict[str, str], clear: bool
) -> None:
    path = f"/tabs/{tab['id']}"
    original = [field("Name", "First draft"), field("Notes", "Remove this field")]
    assert_detail(
        client.put(f"{path}/content", headers=owner, json={"content": original}),
        tab,
        original,
    )
    updated = [] if clear else [{**original[0], "content": "Edited"}]
    saved = client.put(f"{path}/content", headers=owner, json={"content": updated})
    assert_detail(saved, tab, updated)
    assert_detail(client.get(path, headers=owner), tab, updated)


@pytest.mark.parametrize("method", ["GET", "PUT"])
def test_other_users_cannot_access_tab_content(
    client: TestClient, owner: dict[str, str], tab: dict[str, str], method: str
) -> None:
    other_user = sign_in(client, "bobby")
    path = f"/tabs/{tab['id']}"
    content = [field("Owner's note", "Original text")]
    saved = client.put(f"{path}/content", headers=owner, json={"content": content})
    assert_detail(saved, tab, content)

    if method == "GET":
        response = client.get(path, headers=other_user)
    else:
        response = client.put(
            f"{path}/content", headers=other_user, json={"content": []}
        )
    assert response.status_code == 404
    assert_detail(client.get(path, headers=owner), tab, content)


@pytest.mark.parametrize("method", ["GET", "PUT"])
@pytest.mark.parametrize(
    "headers", [{}, {"Authorization": "Bearer invalid"}], ids=["missing", "invalid"]
)
def test_detail_routes_require_authentication(
    client: TestClient, tab: dict[str, str], method: str, headers: dict[str, str]
) -> None:
    path = f"/tabs/{tab['id']}"
    if method == "GET":
        response = client.get(path, headers=headers)
    else:
        response = client.put(f"{path}/content", headers=headers, json={"content": []})
    assert response.status_code == 401


@pytest.mark.parametrize("method", ["GET", "PUT"])
@pytest.mark.parametrize(
    ("tab_id", "expected"),
    [(str(uuid4()), 404), ("invalid", 422)],
    ids=["missing", "invalid"],
)
def test_unknown_or_invalid_tab_id(
    client: TestClient, owner: dict[str, str], method: str, tab_id: str, expected: int
) -> None:
    path = f"/tabs/{tab_id}"
    if method == "GET":
        response = client.get(path, headers=owner)
    else:
        response = client.put(f"{path}/content", headers=owner, json={"content": []})
    assert response.status_code == expected


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"content": "not a list"},
        {"content": [{"title": "Note", "content": "Text"}]},
        {"content": [{"id": str(uuid4()), "content": "Text"}]},
        {"content": [{"id": str(uuid4()), "title": "Note"}]},
        {"content": [{"id": "invalid", "title": "Note", "content": "Text"}]},
        {"content": [field("a" * 51, "Text")]},
        {"content": [{**field("Note", "Text"), "content": 12}]},
    ],
    ids=[
        "missing-content",
        "wrong-container",
        "missing-id",
        "missing-title",
        "missing-text",
        "invalid-uuid",
        "long-title",
        "wrong-text-type",
    ],
)
def test_invalid_content_payload(
    client: TestClient,
    owner: dict[str, str],
    tab: dict[str, str],
    payload: dict[str, object],
) -> None:
    response = client.put(f"/tabs/{tab['id']}/content", headers=owner, json=payload)
    assert response.status_code == 422


def test_invalid_replacement_preserves_content(
    client: TestClient, owner: dict[str, str], tab: dict[str, str]
) -> None:
    path = f"/tabs/{tab['id']}"
    original = [field("Notes", "Saved text")]
    saved = client.put(f"{path}/content", headers=owner, json={"content": original})
    assert_detail(saved, tab, original)

    replacement = [field("First", "New text"), field("a" * 51, "Invalid title")]
    response = client.put(
        f"{path}/content", headers=owner, json={"content": replacement}
    )
    assert response.status_code == 422
    assert_detail(client.get(path, headers=owner), tab, original)
