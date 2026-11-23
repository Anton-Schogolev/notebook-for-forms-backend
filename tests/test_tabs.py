from uuid import uuid4

import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize("title", ["A", "a" * 30])
def test_create_tab(client: TestClient, title: str) -> None:
    tab = {"id": str(uuid4()), "title": title}
    response = client.post("/tabs", json=tab)
    assert response.status_code == 201
    assert response.json() == {**tab, "version": 1}


def test_duplicate_tab_id(client: TestClient) -> None:
    tab = {"id": str(uuid4()), "title": "Original"}
    assert client.post("/tabs", json=tab).status_code == 201
    response = client.post("/tabs", json={**tab, "title": "Duplicate"})
    assert response.status_code == 409


@pytest.mark.parametrize(
    ("field", "value"), [("id", "invalid"), ("title", ""), ("title", "a" * 31)]
)
def test_invalid_tab(client: TestClient, field: str, value: str) -> None:
    tab = {"id": str(uuid4()), "title": "Notes"}
    tab[field] = value
    assert client.post("/tabs", json=tab).status_code == 422


def test_list_empty_tabs(client: TestClient) -> None:
    response = client.get("/tabs")
    assert response.status_code == 200
    assert response.json() == []


def test_list_created_tabs(client: TestClient) -> None:
    tabs = [{"id": str(uuid4()), "title": title} for title in ("Notes", "Tasks")]
    for tab in tabs:
        assert client.post("/tabs", json=tab).status_code == 201

    response = client.get("/tabs")
    assert response.status_code == 200
    listed = response.json()
    assert isinstance(listed, list)
    assert len(listed) == len(tabs)
    for tab in tabs:
        assert {**tab, "version": 1} in listed


def test_update_tab_increments_version(client: TestClient) -> None:
    tab_id = str(uuid4())
    tab = {"id": tab_id, "title": "Draft"}
    assert client.post("/tabs", json=tab).status_code == 201

    for version, title in [(2, "Reviewed"), (3, "Final")]:
        response = client.put(f"/tabs/{tab_id}/metadata", json={"title": title})
        assert response.status_code == 200
        assert response.json() == {"id": tab_id, "title": title, "version": version}

    response = client.get("/tabs")
    assert response.status_code == 200
    assert response.json() == [{"id": tab_id, "title": "Final", "version": 3}]
