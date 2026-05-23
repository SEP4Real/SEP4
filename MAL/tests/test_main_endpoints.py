"""
Endpoint tests for backend/app/main.py using FastAPI's TestClient.

TestClient wraps the ASGI app in-process — no running server required.
Because the app code executes inside this process, pytest-cov can measure
which lines in main.py are reached.

Tests follow the AAA pattern and use the naming convention:
  <what_is_tested>_<scenario>_<expected_outcome>
"""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


_VALID_PAYLOAD = {
    "currentTemperature": 22.0,
    "maxTemp": 25.0,
    "minTemp": 20.0,
    "meanTemp": 22.5,
}


def test_root_endpoint_with_get_returns_hello_world(client):
    # Arrange - client fixture provides the in-process test client
    # Act
    response = client.get("/")
    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": "Hello world from MAL FastAPI"}


def test_model_info_endpoint_returns_200_with_classifier_name(client):
    # Arrange - rf_model.pkl is committed to the repo and available
    # Act
    response = client.get("/model-info")
    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["model"] == "RandomForestClassifier"
    assert "features" in body


def test_model_info_endpoint_reports_available_when_model_exists(client):
    # Arrange
    # Act
    response = client.get("/model-info")
    # Assert
    assert response.json()["status"] == "available"


def test_predict_with_valid_payload_returns_rating_in_range(client):
    # Arrange
    payload = _VALID_PAYLOAD
    # Act
    response = client.post("/predict", json=payload)
    # Assert
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["rating"], int)
    assert 1 <= body["rating"] <= 5


def test_predict_is_deterministic_for_same_input(client):
    # Arrange
    payload = _VALID_PAYLOAD
    # Act
    first = client.post("/predict", json=payload).json()
    second = client.post("/predict", json=payload).json()
    # Assert
    assert first == second


def test_predict_with_missing_field_returns_422(client):
    # Arrange - remove a required field
    payload = {k: v for k, v in _VALID_PAYLOAD.items() if k != "meanTemp"}
    # Act
    response = client.post("/predict", json=payload)
    # Assert
    assert response.status_code == 422


def test_predict_with_inverted_temperature_window_returns_422(client):
    # Arrange - maxTemp < minTemp violates the model_validator
    payload = _VALID_PAYLOAD | {"maxTemp": 19.0, "minTemp": 20.0}
    # Act
    response = client.post("/predict", json=payload)
    # Assert
    assert response.status_code == 422


def test_predict_with_mean_outside_window_returns_422(client):
    # Arrange - meanTemp > maxTemp violates the model_validator
    payload = _VALID_PAYLOAD | {"meanTemp": 30.0}
    # Act
    response = client.post("/predict", json=payload)
    # Assert
    assert response.status_code == 422


def test_predict_with_current_outside_window_returns_422(client):
    # Arrange - currentTemperature > maxTemp violates the model_validator
    payload = _VALID_PAYLOAD | {"currentTemperature": 30.0}
    # Act
    response = client.post("/predict", json=payload)
    # Assert
    assert response.status_code == 422


def test_predict_accepts_negative_temperatures(client):
    # Arrange
    payload = {
        "currentTemperature": -2.0,
        "maxTemp": 1.0,
        "minTemp": -5.0,
        "meanTemp": -1.0,
    }
    # Act
    response = client.post("/predict", json=payload)
    # Assert
    assert response.status_code == 200
    assert 1 <= response.json()["rating"] <= 5


# ---------------------------------------------------------------------------
# Mocking tests — cover branches that require database or missing-file state
# (Python's unittest.mock is the equivalent of Mockito from the exercises)
# ---------------------------------------------------------------------------

_DB_ENV = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "DB_NAME": "testdb",
    "DB_USER": "testuser",
    "DB_PASSWORD": "testpass",
}


def _make_mock_conn(cursor: MagicMock) -> MagicMock:
    """Return a psycopg connection mock that supports the context-manager protocol."""
    mock_conn = MagicMock()
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = cursor
    return mock_conn


def test_model_info_when_model_file_is_missing_returns_not_found(client):
    # Arrange - redirect MODEL_PATH to a path that does not exist
    with patch("backend.app.main.MODEL_PATH", Path("/nonexistent/model.pkl")):
        # Act
        response = client.get("/model-info")
    # Assert
    assert response.status_code == 200
    assert response.json()["status"] == "not_found"


def test_export_data_with_wrong_token_returns_401(client):
    # Arrange - set the expected token in the environment, send a different one
    with patch.dict("os.environ", {"MAL_API_EXPORT_TOKEN": "secret"}):
        # Act
        response = client.get("/export-data", headers={"X-Export-Token": "wrong"})
    # Assert
    assert response.status_code == 401


def test_db_check_with_mocked_database_returns_ok(client):
    # Arrange
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1,)
    mock_conn = _make_mock_conn(mock_cursor)
    # Act
    with patch("backend.app.main.psycopg.connect", return_value=mock_conn):
        with patch.dict("os.environ", _DB_ENV):
            response = client.get("/db-check")
    # Assert
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["result"] == 1


def test_collect_data_when_database_is_empty_returns_no_data_message(client):
    # Arrange - cursor returns no rows, triggering the early-return branch
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = []
    mock_cursor.description = []
    mock_conn = _make_mock_conn(mock_cursor)
    # Act
    with patch("backend.app.main.psycopg.connect", return_value=mock_conn):
        with patch.dict("os.environ", _DB_ENV):
            response = client.get("/collect-data")
    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": "No data found in database"}


def test_collect_data_when_database_raises_returns_500(client):
    # Arrange - connection itself raises before any query runs
    with patch("backend.app.main.psycopg.connect", side_effect=Exception("connection refused")):
        with patch.dict("os.environ", _DB_ENV):
            # Act
            response = client.get("/collect-data")
    # Assert
    assert response.status_code == 500
