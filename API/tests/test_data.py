from unittest.mock import AsyncMock, patch, MagicMock
from tests.conftest import make_cursor, make_db
from datetime import datetime, timezone

NOW = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

DATA_ROW = {
    "id": 1,
    "session_id": 1,
    "temperature": 21.5,
    "humidity": 45.0,
    "co2_level": 800.0,
    "light_level": 300.0,
    "sent_at": NOW,
    "predicted_study_quality": 3,
}

TEMP_STATS = {
    "min_temp": 20.0,
    "max_temp": 23.0,
    "avg_temp": 21.5,
}

DATA_PAYLOAD = {
    "sessionId": 1,
    "temperature": 21.5,
    "humidity": 45.0,
    "co2Level": 800.0,
    "lightLevel": 300.0,
}


def _override(app, db):
    from app.database import get_db
    app.dependency_overrides[get_db] = lambda: db


# GET /data

def test_get_all_data_empty(client, app):
    _override(app, make_db(make_cursor(rows=[])))
    r = client.get("/data")
    assert r.status_code == 200
    assert r.json() == []


def test_get_all_data(client, app):
    _override(app, make_db(make_cursor(rows=[DATA_ROW])))
    r = client.get("/data")
    assert r.status_code == 200
    assert r.json()[0]["id"] == 1


# GET /data/{id}

def test_get_data_by_id_found(client, app):
    _override(app, make_db(make_cursor(one=DATA_ROW)))
    r = client.get("/data/1")
    assert r.status_code == 200
    assert r.json()["id"] == 1


def test_get_data_by_id_not_found(client, app):
    _override(app, make_db(make_cursor(one=None)))
    r = client.get("/data/999")
    assert r.status_code == 404


# GET /data/session/{session_id}

def test_get_data_by_session(client, app):
    _override(app, make_db(make_cursor(rows=[DATA_ROW])))
    r = client.get("/data/session/1")
    assert r.status_code == 200
    assert r.json()[0]["sessionId"] == 1
    assert r.json()[0]["id"] == 1


def test_get_data_by_session_empty(client, app):
    _override(app, make_db(make_cursor(rows=[])))
    r = client.get("/data/session/999")
    assert r.status_code == 200
    assert r.json() == []


# POST /data

def _mock_httpx(rating=3):
    mock_response = MagicMock()
    mock_response.json = MagicMock(return_value={"rating": rating})
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    return mock_client


def test_create_data_success(client, app):
    cur = make_cursor()
    cur.fetchone = AsyncMock(side_effect=[
        {"is_ended": False},
        DATA_ROW,
        TEMP_STATS,
        None,
    ])
    _override(app, make_db(cur))

    with patch("app.routers.data.httpx.AsyncClient", return_value=_mock_httpx(3)):
        r = client.post("/data", json=DATA_PAYLOAD)

    assert r.status_code == 201
    assert r.json()["study_quality"] == 3


def test_create_data_invalid_session_id(client, app):
    _override(app, make_db(make_cursor()))
    r = client.post("/data", json={**DATA_PAYLOAD, "sessionId": 0})
    assert r.status_code == 400


def test_create_data_session_not_found(client, app):
    cur = make_cursor(one=None)
    _override(app, make_db(cur))
    r = client.post("/data", json=DATA_PAYLOAD)
    assert r.status_code == 404


def test_create_data_session_ended(client, app):
    cur = make_cursor(one={"is_ended": True})
    _override(app, make_db(cur))
    r = client.post("/data", json=DATA_PAYLOAD)
    assert r.status_code == 409
