from fastapi.testclient import TestClient

try:
    from MAL.app import main
except ModuleNotFoundError:
    from app import main


VALID_PAYLOAD = {
    "currentNoise": 40,
    "maxNoise": 45,
    "minNoise": 35,
    "meanNoise": 40,
}


def test_predict_returns_model_rating(monkeypatch):
    calls = []

    def fake_predict(current_noise, max_noise, min_noise, mean_noise):
        calls.append((current_noise, max_noise, min_noise, mean_noise))
        return 4

    monkeypatch.setattr(main, "predict", fake_predict)

    response = TestClient(main.app).post("/predict", json=VALID_PAYLOAD)

    assert response.status_code == 200
    assert response.json() == {"rating": 4}
    assert calls == [(40, 45, 35, 40)]


def test_predict_rejects_missing_noise_feature():
    payload = VALID_PAYLOAD.copy()
    payload.pop("meanNoise")

    response = TestClient(main.app).post("/predict", json=payload)

    assert response.status_code == 422


def test_predict_rejects_negative_noise():
    payload = VALID_PAYLOAD | {"currentNoise": -1}

    response = TestClient(main.app).post("/predict", json=payload)

    assert response.status_code == 422


def test_predict_rejects_invalid_noise_window():
    payload = VALID_PAYLOAD | {"maxNoise": 30, "minNoise": 35}

    response = TestClient(main.app).post("/predict", json=payload)

    assert response.status_code == 422


def test_predict_rejects_mean_outside_noise_window():
    payload = VALID_PAYLOAD | {"meanNoise": 50}

    response = TestClient(main.app).post("/predict", json=payload)

    assert response.status_code == 422
