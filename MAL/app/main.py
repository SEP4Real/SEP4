import os

from fastapi import FastAPI
from pydantic import BaseModel, Field
import psycopg

#from app.model import predict_focus_level, suggestion_for_focus_level
from app.model2 import predict_focus_level, suggestion_for_focus_level


app = FastAPI(title="MAL API")


class EnvironmentReading(BaseModel):
    temperature: float = Field(..., ge=-20, le=60)
    humidity: float = Field(..., ge=0, le=100)
    co2Level: float = Field(..., ge=0)
    lightLevel: float = Field(..., ge=0)
    noiseLevel: float = Field(..., ge=0)


@app.get("/")
def hello_world() -> dict[str, str]:
    return {"message": "Hello world from MAL FastAPI"}


@app.get("/db-check")
def db_check() -> dict[str, str | int]:
    db_host = os.environ["DB_HOST"]
    db_port = os.environ["DB_PORT"]
    db_name = os.environ["DB_NAME"]
    db_user = os.environ["DB_USER"]
    db_password = os.environ["DB_PASSWORD"]

    with psycopg.connect(
        host=db_host,
        port=db_port,
        dbname=db_name,
        user=db_user,
        password=db_password,
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()

    return {"status": "ok", "result": result[0] if result else 0}


@app.post("/predict")
def predict(reading: EnvironmentReading) -> dict[str, int | str]:
    focus_level = predict_focus_level(
        temperature=reading.temperature,
        humidity=reading.humidity,
        co2_level=reading.co2Level,
        light_level=reading.lightLevel,
        noise_level=reading.noiseLevel,
    )

    return {
        "predictedFocusLevel": focus_level,
        "suggestion": suggestion_for_focus_level(focus_level),
    }
