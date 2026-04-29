import os

from fastapi import FastAPI
import psycopg
from .model import predict
from pydantic import BaseModel, Field, model_validator

#comment
app = FastAPI(title="MAL API")


class PredictionRequest(BaseModel):
    currentNoise: float = Field(ge=0, allow_inf_nan=False)
    maxNoise: float = Field(ge=0, allow_inf_nan=False)
    minNoise: float = Field(ge=0, allow_inf_nan=False)
    meanNoise: float = Field(ge=0, allow_inf_nan=False)

    @model_validator(mode="after")
    def validate_noise_window(self) -> "PredictionRequest":
        if self.maxNoise < self.minNoise:
            raise ValueError("maxNoise must be greater than or equal to minNoise")
        if not self.minNoise <= self.meanNoise <= self.maxNoise:
            raise ValueError("meanNoise must be between minNoise and maxNoise")
        if not self.minNoise <= self.currentNoise <= self.maxNoise:
            raise ValueError("currentNoise must be between minNoise and maxNoise")
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
    return PredictionResponse(rating=rating)
