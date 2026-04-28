from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_predict_returns_focus_level_and_suggestion():
    response = client.post(
        "/predict",
        json={
            "temperature": 22,
            "humidity": 45,
            "co2Level": 650,
            "lightLevel": 550,
            "noiseLevel": 42,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert 1 <= body["predictedFocusLevel"] <= 5
    assert body["suggestion"]


def test_predict_rejects_invalid_humidity():
    response = client.post(
        "/predict",
        json={
            "temperature": 22,
            "humidity": 130,
            "co2Level": 650,
            "lightLevel": 550,
            "noiseLevel": 42,
        },
    )

    assert response.status_code == 422
