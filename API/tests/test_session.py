from unittest.mock import AsyncMock
from tests.conftest import make_cursor, make_db
from datetime import datetime, timezone

NOW = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

SESSION_ROW = {
    "id": 1,
    "device_id": "dev-001",
    "started_at": NOW,
    "is_ended": False,
    "last_pulse_at": NOW,
    "study_quality": None,
}


def _override(app, db):
    from app.database import get_db
    app.dependency_overrides[get_db] = lambda: db


# GET /session

def test_get_all_sessions_empty(client, app):
    _override(app, make_db(make_cursor(rows=[])))
    r = client.get("/session")
    assert r.status_code == 200
    assert r.json() == []


def test_get_all_sessions(client, app):
    _override(app, make_db(make_cursor(rows=[SESSION_ROW])))
    r = client.get("/session")
    assert r.status_code == 200
    assert r.json()[0]["id"] == 1


# GET /session/device/{id}

def test_get_sessions_by_device(client, app):
    _override(app, make_db(make_cursor(rows=[SESSION_ROW])))
    r = client.get("/session/device/dev-001")
    assert r.status_code == 200
    assert r.json()[0]["deviceId"] == "dev-001"


def test_get_sessions_by_device_empty(client, app):
    _override(app, make_db(make_cursor(rows=[])))
    r = client.get("/session/device/unknown")
    assert r.status_code == 200
    assert r.json() == []


# GET /session/current

def test_get_current_session_success(client, app):
    _override(app, make_db(make_cursor(one=SESSION_ROW)))
    r = client.get("/session/current?deviceId=dev-001")
    assert r.status_code == 200
    assert r.json()["id"] == 1


def test_get_current_session_without_device_id(client, app):
    _override(app, make_db(make_cursor(one=SESSION_ROW)))
    r = client.get("/session/current")
    assert r.status_code == 200
    assert r.json()["id"] == 1


def test_get_current_session_empty_device_id(client, app):
    _override(app, make_db(make_cursor()))
    r = client.get("/session/current?deviceId=   ")
    assert r.status_code == 400


def test_get_current_session_not_found(client, app):
    _override(app, make_db(make_cursor(one=None)))
    r = client.get("/session/current?deviceId=dev-001")
    assert r.status_code == 404


# GET /session/{id}

def test_get_session_found(client, app):
    _override(app, make_db(make_cursor(one=SESSION_ROW)))
    r = client.get("/session/1")
    assert r.status_code == 200
    assert r.json()["id"] == 1


def test_get_session_not_found(client, app):
    _override(app, make_db(make_cursor(one=None)))
    r = client.get("/session/999")
    assert r.status_code == 404


# POST /session

def test_create_session_success(client, app):
    cur = make_cursor()
    cur.fetchone = AsyncMock(side_effect=[{"id": "dev-001"}, SESSION_ROW])
    _override(app, make_db(cur))
    r = client.post("/session", json={"deviceId": "dev-001"})
    assert r.status_code == 201
    assert r.json()["deviceId"] == "dev-001"


def test_create_session_device_not_found(client, app):
    cur = make_cursor(one=None)
    _override(app, make_db(cur))
    r = client.post("/session", json={"deviceId": "ghost"})
    assert r.status_code == 404


def test_create_session_empty_device_id(client, app):
    _override(app, make_db(make_cursor()))
    r = client.post("/session", json={"deviceId": "   "})
    assert r.status_code == 400


# PATCH /session/{id}/pulse

def test_pulse_alive(client, app):
    cur = make_cursor(one={"is_ended": False})
    _override(app, make_db(cur))
    r = client.patch("/session/1/pulse")
    assert r.status_code == 200
    assert r.json()["alive"] is True


def test_pulse_ended_session(client, app):
    cur = make_cursor(one={"is_ended": True})
    _override(app, make_db(cur))
    r = client.patch("/session/1/pulse")
    assert r.status_code == 200
    assert r.json()["alive"] is False


def test_pulse_not_found(client, app):
    cur = make_cursor(one=None)
    _override(app, make_db(cur))
    r = client.patch("/session/999/pulse")
    assert r.status_code == 404


# PATCH /session/{id}

def test_update_session_success(client, app):
    updated = {**SESSION_ROW, "study_quality": 4}
    cur = make_cursor()
    cur.fetchone = AsyncMock(side_effect=[SESSION_ROW, updated])
    _override(app, make_db(cur))
    r = client.patch("/session/1", json={"studyQuality": 4})
    assert r.status_code == 200
    assert r.json()["studyQuality"] == 4


def test_update_session_not_found(client, app):
    cur = make_cursor(one=None)
    _override(app, make_db(cur))
    r = client.patch("/session/999", json={"studyQuality": 3})
    assert r.status_code == 404


# DELETE /session/{id}

def test_delete_session_success(client, app):
    cur = make_cursor()
    cur.fetchone = AsyncMock(side_effect=[{"id": 1}, None])
    _override(app, make_db(cur))
    r = client.delete("/session/1")
    assert r.status_code == 204


def test_delete_session_not_found(client, app):
    cur = make_cursor(one=None)
    _override(app, make_db(cur))
    r = client.delete("/session/999")
    assert r.status_code == 404


def test_delete_session_has_data(client, app):
    cur = make_cursor()
    cur.fetchone = AsyncMock(side_effect=[{"id": 1}, {"session_id": 1}])
    _override(app, make_db(cur))
    r = client.delete("/session/1")
    assert r.status_code == 409
