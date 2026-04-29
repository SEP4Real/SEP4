import os
from datetime import datetime

import psycopg
from fastapi import FastAPI
from pydantic import BaseModel, Field, model_validator

from .model import FEATURE_COLUMNS, MODEL_PATH, predict

app = FastAPI(title="MAL API")


class PredictionRequest(BaseModel):
    currentTemperature: float = Field(allow_inf_nan=False)
    maxTemp: float = Field(allow_inf_nan=False)
    minTemp: float = Field(allow_inf_nan=False)
    meanTemp: float = Field(allow_inf_nan=False)

    @model_validator(mode="after")
    def validate_temperature_window(self) -> "PredictionRequest":
        if self.maxTemp < self.minTemp:
            raise ValueError("maxTemp must be greater than or equal to minTemp")
        if not self.minTemp <= self.meanTemp <= self.maxTemp:
            raise ValueError("meanTemp must be between minTemp and maxTemp")
        if not self.minTemp <= self.currentTemperature <= self.maxTemp:
            raise ValueError("currentTemperature must be between minTemp and maxTemp")
        return self


class PredictionResponse(BaseModel):
    rating: int = Field(ge=1, le=5)


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


@app.get("/model-info")
def get_model_info() -> dict[str, object]:
    if MODEL_PATH.exists():
        last_modified = datetime.fromtimestamp(MODEL_PATH.stat().st_mtime).isoformat()
        return {
            "status": "available",
            "last_modified": last_modified,
            "model": "RandomForestClassifier",
            "features": FEATURE_COLUMNS,
        }
    return {"status": "not_found", "model": "RandomForestClassifier", "features": FEATURE_COLUMNS}


@app.post("/predict", response_model=PredictionResponse)
async def get_prediction(data: PredictionRequest) -> PredictionResponse:
    rating = predict(
        data.currentTemperature,
        data.maxTemp,
        data.minTemp,
        data.meanTemp,
    )
    return PredictionResponse(rating=rating)
