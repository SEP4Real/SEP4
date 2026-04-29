import os

from fastapi import FastAPI
import psycopg
from .model import predict
from pydantic import BaseModel

#comment
app = FastAPI(title="MAL API")


class PredictionRequest(BaseModel):
    currentNoise: float
    maxNoise: float
    minNoise: float
    meanNoise: float


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
def get_model_info() -> dict[str, str | float]:
    import os
    from datetime import datetime
    model_path = "rf_model.pkl"
    if os.path.exists(model_path):
        mtime = os.path.getmtime(model_path)
        last_modified = datetime.fromtimestamp(mtime).isoformat()
        return {"status": "available", "last_modified": last_modified, "model": "RandomForest"}
    return {"status": "not_found"}

@app.post("/predict")
async def get_prediction(data: PredictionRequest):
    rating = predict(
        data.currentNoise,
        data.maxNoise,
        data.minNoise,
        data.meanNoise
    )
    return {"rating": rating}
