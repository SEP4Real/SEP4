import os

from fastapi import FastAPI
import psycopg
from .model import MODEL_PATHS, predict
from pydantic import BaseModel

#comment
app = FastAPI(title="MAL API")


class PredictionRequest(BaseModel):
    currentTemperature: float
    maxTemp: float
    minTemp: float
    meanTemp: float


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
def get_model_info() -> dict[str, list[dict]]:
    from datetime import datetime
    info = []
    for model_path in MODEL_PATHS.values():
        if model_path.exists():
            mtime = model_path.stat().st_mtime
            info.append({
                "name": model_path.name,
                "status": "available",
                "last_modified": datetime.fromtimestamp(mtime).isoformat()
            })
        else:
            info.append({"name": model_path.name, "status": "not_found"})
    return {"models": info}

@app.post("/predict")
async def get_prediction(data: PredictionRequest):
    rating = predict(
        data.currentTemperature,
        data.maxTemp,
        data.minTemp,
        data.meanTemp
    )
    return {"rating": rating}
