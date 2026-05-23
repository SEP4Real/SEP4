"""
Endpoint tests for backend/app/main.py using FastAPI's TestClient.

TestClient wraps the ASGI app in-process — no running server required.
Because the app code executes inside this process, pytest-cov can measure
which lines in main.py are reached.

Tests follow the AAA pattern and use the naming convention:
  <what_is_tested>_<scenario>_<expected_outcome>
"""
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
