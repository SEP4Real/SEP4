from unittest.mock import patch
from tests.conftest import make_cursor, make_db
from unittest.mock import AsyncMock


# helpers

DEVICE_ROW = {"id": "dev-001"}


def _override(app, db):
    from app.database import get_db
    app.dependency_overrides[get_db] = lambda: db
    return app


# GET /device

def test_get_all_devices_empty(client, app):
    db = make_db(make_cursor(rows=[]))
    _override(app, db)
    r = client.get("/device")
    assert r.status_code == 200
    assert r.json() == []


def test_get_all_devices(client, app):
    db = make_db(make_cursor(rows=[DEVICE_ROW]))
    _override(app, db)
    r = client.get("/device")
    assert r.status_code == 200
    assert r.json()[0]["id"] == "dev-001"


# GET /device/{id}

def test_get_device_found(client, app):
    db = make_db(make_cursor(one=DEVICE_ROW))
    _override(app, db)
    r = client.get("/device/dev-001")
    assert r.status_code == 200
    assert r.json()["id"] == "dev-001"


def test_get_device_not_found(client, app):
    db = make_db(make_cursor(one=None))
    _override(app, db)
    r = client.get("/device/missing")
    assert r.status_code == 404


# POST /device

def test_create_device_success(client, app):
    cur = make_cursor(one=None)
    db = make_db(cur)
    _override(app, db)
    r = client.post("/device", json={"id": "dev-new"})
    assert r.status_code == 201
    assert r.json()["id"] == "dev-new"


def test_create_device_duplicate(client, app):
    cur = make_cursor(one={"id": "dev-001"})
    db = make_db(cur)
    _override(app, db)
    r = client.post("/device", json={"id": "dev-001"})
    assert r.status_code == 409


def test_create_device_empty_id(client, app):
    db = make_db(make_cursor(one=None))
    _override(app, db)
    r = client.post("/device", json={"id": "   "})
    assert r.status_code == 400


# DELETE /device/{id}

def test_delete_device_success(client, app):
    cur = make_cursor()
    responses = [{"id": "dev-001"}, None]
    cur.fetchone = __import__("unittest.mock", fromlist=["AsyncMock"]).AsyncMock(
        side_effect=responses
    )
    db = make_db(cur)
    _override(app, db)
    r = client.delete("/device/dev-001")
    assert r.status_code == 204


def test_delete_device_not_found(client, app):
    cur = make_cursor(one=None)
    db = make_db(cur)
    _override(app, db)
    r = client.delete("/device/ghost")
    assert r.status_code == 404


def test_delete_device_has_sessions(client, app):
    cur = make_cursor()
    cur.fetchone = AsyncMock(side_effect=[{"id": "dev-001"}, {"session_id": 1}])

    db = make_db(cur)
    _override(app, db)
    r = client.delete("/device/dev-001")
    assert r.status_code == 409
