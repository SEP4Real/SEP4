from unittest.mock import AsyncMock, patch
from tests.conftest import make_cursor, make_db

from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _override(app, db):
    from app.database import get_db
    app.dependency_overrides[get_db] = lambda: db


REGISTER_PAYLOAD = {
    "name": "Ada",
    "last_name": "Lovelace",
    "email": "ada@example.com",
    "password": "secret123",
}

USER_ROW = {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Ada",
    "last_name": "Lovelace",
    "email": "ada@example.com",
    "password": "$2b$12$hashedpassword",
}


# POST /register

def test_register_success(client, app):
    db = AsyncMock()
    result = AsyncMock()
    result.fetchone = AsyncMock(return_value=None)
    db.execute = AsyncMock(return_value=result)
    db.commit = AsyncMock()
    _override(app, db)

    r = client.post("/register", json=REGISTER_PAYLOAD)
    assert r.status_code == 200
    assert r.json()["message"] == "User created"


def test_register_duplicate_email(client, app):
    db = AsyncMock()
    result = AsyncMock()
    result.fetchone = AsyncMock(return_value=USER_ROW)
    db.execute = AsyncMock(return_value=result)
    _override(app, db)

    r = client.post("/register", json=REGISTER_PAYLOAD)
    assert r.status_code == 400
    assert "already registered" in r.json()["detail"]


# POST /login

def test_login_success(client, app):
    db = AsyncMock()
    result = AsyncMock()

    hashed = __import__("passlib.context", fromlist=["CryptContext"]).CryptContext(
        schemes=["bcrypt"], deprecated="auto"
    ).hash("secret123")

    result.fetchone = AsyncMock(return_value={**USER_ROW, "password": hashed})
    db.execute = AsyncMock(return_value=result)
    _override(app, db)

    r = client.post("/login", json={"email": "ada@example.com", "password": "secret123"})
    assert r.status_code == 200
    body = r.json()
    assert body["message"] == "Login successful"
    assert "access_token" in body
    assert body["user"]["email"] == "ada@example.com"


def test_login_user_not_found(client, app):
    db = AsyncMock()
    result = AsyncMock()
    result.fetchone = AsyncMock(return_value=None)
    db.execute = AsyncMock(return_value=result)
    _override(app, db)

    r = client.post("/login", json={"email": "ghost@example.com", "password": "x"})
    assert r.status_code == 200
    assert r.json()["error"] == "Invalid credentials"


def test_login_wrong_password(client, app):
    db = AsyncMock()
    result = AsyncMock()
    real_hash = pwd_context.hash("correctpassword")
    result.fetchone = AsyncMock(return_value={**USER_ROW, "password": real_hash})
    db.execute = AsyncMock(return_value=result)
    _override(app, db)

    r = client.post("/login", json={"email": "ada@example.com", "password": "wrongpassword"})
    assert r.status_code == 200
    assert r.json()["error"] == "Invalid credentials"


# HEALTH

def test_db_health_ok(client, app):
    cur = make_cursor()
    cur.fetchone = AsyncMock(side_effect=[
        {"exists": True},
        {"exists": True},
        {"exists": True},
    ])
    _override(app, make_db(cur))
    r = client.get("/health/db")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_db_health_missing_table(client, app):
    cur = make_cursor()
    cur.fetchone = AsyncMock(side_effect=[
        {"exists": True},
        {"exists": False},   # sessions missing
        {"exists": True},
    ])
    _override(app, make_db(cur))
    r = client.get("/health/db")
    assert r.status_code == 503
    assert "sessions" in r.json()["missingTables"]


def test_db_health_unreachable(client, app):
    db = AsyncMock()
    cur = AsyncMock()
    cur.execute = AsyncMock(side_effect=Exception("connection refused"))
    cur.__aenter__ = AsyncMock(return_value=cur)
    cur.__aexit__ = AsyncMock(return_value=False)
    db.cursor = lambda: cur
    _override(app, db)
    r = client.get("/health/db")
    assert r.status_code == 503
    assert r.json()["status"] == "unhealthy"


# PREDICTION

PREDICT_PAYLOAD = {
    "sessionId": 1,
    "temperature": 21.5,
    "humidity": 45.0,
    "co2Level": 800.0,
    "lightLevel": 300.0,
}


def test_predict_returns_study_quality(client, app):
    _override(app, make_db(make_cursor()))
    r = client.post("/predict", json=PREDICT_PAYLOAD)
    assert r.status_code == 201
    body = r.json()
    assert "study_quality" in body
    assert 1 <= body["study_quality"] <= 5
