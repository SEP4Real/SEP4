"""
API tests for the MAL service.

These tests hit a running MAL instance over real HTTP — they verify the
service starts, the model is loaded, the /predict endpoint returns valid
ratings, and the request validator rejects bad payloads. Run before
deploying to Coolify.

Set MAL_BASE_URL to point at a running instance (defaults to localhost:8000).

Run:
    MAL_BASE_URL=http://localhost:8000 python -m pytest tests/test_prediction_api.py -v
"""
import os

import httpx
import pytest

BASE_URL = os.environ.get("MAL_BASE_URL", "http://localhost:8000")

VALID_PAYLOAD = {
    "currentTemperature": 22.0,
    "maxTemp": 24.0,
    "minTemp": 20.0,
    "meanTemp": 22.0,
    "currentHumidity": 50.0,
    "maxHumidity": 55.0,
    "minHumidity": 45.0,
    "meanHumidity": 50.0,
    "currentCO2": 850.0,
    "maxCO2": 900.0,
    "minCO2": 800.0,
    "meanCO2": 850.0,
    "currentLight": 320.0,
    "maxLight": 350.0,
    "minLight": 300.0,
    "meanLight": 320.0,
    "currentNoise": 5.39,
    "maxNoise": 5.39,
    "minNoise": 5.39,
    "meanNoise": 5.39,
}

INSTANT_VALID_PAYLOAD = {
    "temperature": 22,
    "humidity": 45,
    "co2Level": 650,
    "lightLevel": 300,
    "noise": 29,
}


@pytest.fixture(scope="module")
def client():
    with httpx.Client(base_url=BASE_URL, timeout=10) as c:
        yield c


def test_service_is_reachable(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello world from MAL FastAPI"}


def test_model_is_loaded_and_available(client):
    response = client.get("/model-info")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "available"
    assert body["model"] == "MLPClassifier"


def test_predict_returns_valid_rating(client):
    response = client.post("/predict", json=VALID_PAYLOAD)

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body.get("rating"), int)
    assert 1 <= body["rating"] <= 5


def test_predict_is_deterministic(client):
    first = client.post("/predict", json=VALID_PAYLOAD).json()
    second = client.post("/predict", json=VALID_PAYLOAD).json()

    assert first == second


def test_predict_accepts_negative_temperatures(client):
    payload = VALID_PAYLOAD | {
        "currentTemperature": -2.0,
        "maxTemp": 1.0,
        "minTemp": -5.0,
        "meanTemp": -1.0,
    }

    response = client.post("/predict", json=payload)

    assert response.status_code == 200
    assert 1 <= response.json()["rating"] <= 5


def test_predict_rejects_missing_field(client):
    payload = VALID_PAYLOAD.copy()
    payload.pop("meanTemp")

    response = client.post("/predict", json=payload)

    assert response.status_code == 422


def test_predict_rejects_invalid_temperature_window(client):
    payload = VALID_PAYLOAD | {"maxTemp": 19.0, "minTemp": 20.0}

    response = client.post("/predict", json=payload)

    assert response.status_code == 422


def test_predict_rejects_mean_outside_window(client):
    payload = VALID_PAYLOAD | {"meanTemp": 25.0}

    response = client.post("/predict", json=payload)

    assert response.status_code == 422


def test_predict_rejects_current_outside_window(client):
    payload = VALID_PAYLOAD | {"currentTemperature": 25.0}

    response = client.post("/predict", json=payload)

    assert response.status_code == 422


def test_predict_rejects_invalid_humidity_window(client):
    payload = VALID_PAYLOAD | {"maxHumidity": 40.0, "minHumidity": 45.0}

    response = client.post("/predict", json=payload)

    assert response.status_code == 422


def test_predict_rejects_invalid_co2_window(client):
    payload = VALID_PAYLOAD | {"meanCO2": 1200.0}

    response = client.post("/predict", json=payload)

    assert response.status_code == 422


def test_instant_predict_returns_valid_rating(client):
    response = client.post("/instant-predict", json=INSTANT_VALID_PAYLOAD)

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body.get("rating"), int)
    assert 1 <= body["rating"] <= 5


def test_instant_predict_rejects_missing_field(client):
    payload = INSTANT_VALID_PAYLOAD.copy()
    payload.pop("humidity")

    response = client.post("/instant-predict", json=payload)

    assert response.status_code == 422
