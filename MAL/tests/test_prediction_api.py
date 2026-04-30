from fastapi.testclient import TestClient

from backend.app import main


VALID_PAYLOAD = {
    "currentTemperature": 22,
    "maxTemp": 24,
    "minTemp": 20,
    "meanTemp": 22,
}


def test_predict_returns_model_rating(monkeypatch):
    calls = []

    def fake_predict(current_temperature, max_temperature, min_temperature, mean_temperature):
        calls.append((current_temperature, max_temperature, min_temperature, mean_temperature))
        return 4

    monkeypatch.setattr(main, "predict", fake_predict)

    response = TestClient(main.app).post("/predict", json=VALID_PAYLOAD)

    assert response.status_code == 200
    assert response.json() == {"rating": 4}
    assert calls == [(22, 24, 20, 22)]


def test_predict_rejects_missing_temperature_feature():
    payload = VALID_PAYLOAD.copy()
    payload.pop("meanTemp")

    response = TestClient(main.app).post("/predict", json=payload)

    assert response.status_code == 422


def test_predict_accepts_negative_temperature(monkeypatch):
    monkeypatch.setattr(main, "predict", lambda *args: 3)
    payload = {"currentTemperature": -2, "maxTemp": 1, "minTemp": -5, "meanTemp": -1}

    response = TestClient(main.app).post("/predict", json=payload)

    assert response.status_code == 200
    assert response.json() == {"rating": 3}


def test_predict_rejects_invalid_temperature_window():
    payload = VALID_PAYLOAD | {"maxTemp": 19, "minTemp": 20}

    response = TestClient(main.app).post("/predict", json=payload)

    assert response.status_code == 422


def test_predict_rejects_mean_outside_temperature_window():
    payload = VALID_PAYLOAD | {"meanTemp": 25}

    response = TestClient(main.app).post("/predict", json=payload)

    assert response.status_code == 422


def test_predict_rejects_current_temperature_outside_window():
    payload = VALID_PAYLOAD | {"currentTemperature": 25}

    response = TestClient(main.app).post("/predict", json=payload)

    assert response.status_code == 422
