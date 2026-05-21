import os

os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_NAME", "test")
os.environ.setdefault("DB_USER", "test")
os.environ.setdefault("DB_PASSWORD", "test")
os.environ.setdefault("MAL_API_HOST_PORT", "http://ml:8000")
os.environ.setdefault("SECRET_KEY", "test_secret_key")

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

import app.database
import app.main


def make_cursor(rows=None, one=None):
    cur = AsyncMock()
    cur.fetchall = AsyncMock(return_value=rows or [])
    cur.fetchone = AsyncMock(return_value=one)
    cur.__aenter__ = AsyncMock(return_value=cur)
    cur.__aexit__ = AsyncMock(return_value=False)
    return cur


def make_db(cursor=None):
    db = AsyncMock()
    db.cursor = MagicMock(return_value=cursor or make_cursor())
    db.commit = AsyncMock()
    return db


@pytest.fixture()
def app():
    with patch("app.main.ensure_schema_created", new_callable=AsyncMock), \
         patch("app.main.cleanup_sessions", new_callable=AsyncMock):
        from app.main import app as _app
        yield _app


@pytest.fixture()
def client(app):
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
