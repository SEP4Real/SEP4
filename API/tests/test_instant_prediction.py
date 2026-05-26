from tests.conftest import make_cursor, make_db

import app.routers.instant_measurement as instant_measurement



GOOD_PAYLOAD = {
    "temperature": 22.5,
    "humidity": 45.0,
    "co2Level": 650.0,
    "lightLevel": 400.0,
}


BAD_PAYLOAD = {
    "temperature": 29.5,
    "humidity": 82.0,
    "co2Level": 1800.0,
    "lightLevel": 90.0,
}


LATEST_GOOD_ROW = {
    "temperature": 22.5,
    "humidity": 45.0,
    "co2_level": 650.0,
    "light_level": 400.0,
}


LATEST_BAD_ROW = {
    "temperature": 29.5,
    "humidity": 82.0,
    "co2_level": 1800.0,
    "light_level": 90.0,
}


def _override(app, db):
    from app.database import get_db

    app.dependency_overrides[get_db] = lambda: db


def _mock_mal_instant_prediction(monkeypatch, rating):
    class DummyResponse:
        status_code = 200

        def json(self):
            return {"rating": rating}

    class DummyClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, *_args, **_kwargs):
            return DummyResponse()

    monkeypatch.setattr(
        instant_measurement.httpx,
        "AsyncClient",
        lambda *args, **kwargs: DummyClient(),
    )


def test_instant_measurement_returns_stay_for_good_conditions(client, monkeypatch):
    _mock_mal_instant_prediction(monkeypatch, rating=4)
    response = client.post("/instant-measurement", json=GOOD_PAYLOAD)

    assert response.status_code == 201
    assert response.json() == {"study_quality": 4}


def test_instant_measurement_returns_leave_for_bad_conditions(client, monkeypatch):
    _mock_mal_instant_prediction(monkeypatch, rating=1)
    response = client.post("/instant-measurement", json=BAD_PAYLOAD)

    assert response.status_code == 201
    assert response.json() == {"study_quality": 1}


def test_latest_instant_measurement_reads_database_snapshot(client, app, monkeypatch):
    _mock_mal_instant_prediction(monkeypatch, rating=4)
    _override(app, make_db(make_cursor(one=LATEST_GOOD_ROW)))

    response = client.get("/instant-measurement/latest")

    assert response.status_code == 200
    assert response.json() == {"study_quality": 4}


def test_latest_instant_measurement_can_filter_by_session(client, app, monkeypatch):
    _mock_mal_instant_prediction(monkeypatch, rating=1)
    _override(app, make_db(make_cursor(one=LATEST_BAD_ROW)))

    response = client.get("/instant-measurement/latest?sessionId=1")

    assert response.status_code == 200
    assert response.json() == {"study_quality": 1}


def test_latest_instant_measurement_returns_404_without_sensor_data(client, app):
    _override(app, make_db(make_cursor(one=None)))

    response = client.get("/instant-measurement/latest")

    assert response.status_code == 404
