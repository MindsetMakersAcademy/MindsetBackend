from __future__ import annotations

import pytest
from flask.testing import FlaskClient

BASE = "/api/v1/courses"


def test_list_courses_empty(client: FlaskClient) -> None:
    """When no courses are seeded, list returns an empty array wrapper."""
    res = client.get(BASE)
    assert res.status_code == 200
    body = res.get_json()
    assert isinstance(body, dict)
    assert body["courses"] == []


@pytest.mark.usefixtures("seed_two_courses")
def test_list_courses_with_data(client: FlaskClient) -> None:
    """When courses are seeded, list returns them with expected keys and types."""
    res = client.get(BASE)
    assert res.status_code == 200
    body = res.get_json()
    assert isinstance(body["courses"], list)
    assert {it["title"] for it in body["courses"]} == {"A", "B"}


def test_get_course_by_id_ok(client: FlaskClient, course_repo, scoped_test_session, seed_delivery_modes) -> None:
    """GET /courses/<id> returns 200 and a JSON object matching DTO shape."""
    created = course_repo.create_course(
        title="X",
        description=None,
        delivery_mode_id=seed_delivery_modes["online"].id,
        venue_id=None,
        instructor_ids=[],
    )
    scoped_test_session.flush()

    res = client.get(f"{BASE}/{created.id}")
    assert res.status_code == 200
    body = res.get_json()
    assert isinstance(body, dict)
    assert body["id"] == created.id
    assert body["title"] == "X"


def test_get_course_404(client: FlaskClient) -> None:
    """GET unknown id returns 404 and an error key in JSON body."""
    res = client.get(f"{BASE}/999999")
    assert res.status_code == 404
    body = res.get_json(silent=True)
    assert body and "error" in body


def test_search_returns_empty_when_no_q(client: FlaskClient) -> None:
    """Calling search without q param returns empty list."""
    res = client.get(f"{BASE}/search")
    assert res.status_code == 200
    assert res.get_json()["courses"] == []

def test_create_course_success(client, seed_delivery_modes):
    """POST with valid payload creates a course."""
    dm_id = seed_delivery_modes["online"].id  # ensure the FK exists
    payload = {
        "title": "New API Course",
        "description": "desc",
        "delivery_mode_id": dm_id,
        "venue_id": None,
        "instructor_ids": [],
        "start_date": "2024-01-01",
        "end_date": "2024-01-02",
    }
    res = client.post("/api/v1/courses", json=payload)
    assert res.status_code == 201, res.get_json()  # helpful when debugging
    body = res.get_json()
    assert body["title"] == "New API Course"
    assert body["delivery_mode_id"] == dm_id



def test_create_course_bad_payload(client, seed_delivery_modes):
    """POST with invalid payload returns 400."""
    dm_id = seed_delivery_modes["online"].id
    payload = {
        "title": "New API Course",
        "description": "desc",
        "delivery_mode_id": dm_id,
        "venue_id": None,
        "instructor_ids": [],
        "start_date": "2024-02-02",
        "end_date": "2024-01-01",  # invalid range
    }
    res = client.post("/api/v1/courses", json=payload)
    assert res.status_code == 400, res.get_json()  # surface server error body on failure
    err = res.get_json()
    assert "error" in err or "message" in err
