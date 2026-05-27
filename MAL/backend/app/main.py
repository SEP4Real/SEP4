import csv
import io
import zipfile
import os
from datetime import datetime

import psycopg
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, model_validator

from ml_pipeline.instant_model import predict_instant
from ml_pipeline.model import FEATURE_COLUMNS, MODEL_PATH, REAL_SENSOR_HISTORY_PATH, predict
from ml_pipeline.transform_real_data import transform_real_data

app = FastAPI(title="MAL API")

DEFAULT_NOISE_DB = 29.0
DEFAULT_NOISE_FEATURE_VALUE = round(DEFAULT_NOISE_DB**0.5, 2)

def _require_export_token(x_export_token: str | None = Header(default=None)) -> None:
    expected_token = os.environ.get("MAL_API_EXPORT_TOKEN")
    if expected_token and x_export_token != expected_token:
        raise HTTPException(status_code=401, detail="Invalid export token")

class PredictionRequest(BaseModel):
    currentTemperature: float = Field(allow_inf_nan=False)
    maxTemp: float = Field(allow_inf_nan=False)
    minTemp: float = Field(allow_inf_nan=False)
    meanTemp: float = Field(allow_inf_nan=False)
    currentHumidity: float = Field(allow_inf_nan=False)
    maxHumidity: float = Field(allow_inf_nan=False)
    minHumidity: float = Field(allow_inf_nan=False)
    meanHumidity: float = Field(allow_inf_nan=False)
    currentCO2: float = Field(allow_inf_nan=False)
    maxCO2: float = Field(allow_inf_nan=False)
    minCO2: float = Field(allow_inf_nan=False)
    meanCO2: float = Field(allow_inf_nan=False)
    currentLight: float = Field(allow_inf_nan=False)
    maxLight: float = Field(allow_inf_nan=False)
    minLight: float = Field(allow_inf_nan=False)
    meanLight: float = Field(allow_inf_nan=False)
    currentNoise: float = Field(default=DEFAULT_NOISE_FEATURE_VALUE, allow_inf_nan=False)
    maxNoise: float = Field(default=DEFAULT_NOISE_FEATURE_VALUE, allow_inf_nan=False)
    minNoise: float = Field(default=DEFAULT_NOISE_FEATURE_VALUE, allow_inf_nan=False)
    meanNoise: float = Field(default=DEFAULT_NOISE_FEATURE_VALUE, allow_inf_nan=False)

    @model_validator(mode="after")
    def validate_prediction_window(self) -> "PredictionRequest":
        # Validate temperature window
        if self.maxTemp < self.minTemp:
            raise ValueError("maxTemp must be greater than or equal to minTemp")
        if not self.minTemp <= self.meanTemp <= self.maxTemp:
            raise ValueError("meanTemp must be between minTemp and maxTemp")
        if not self.minTemp <= self.currentTemperature <= self.maxTemp:
            raise ValueError("currentTemperature must be between minTemp and maxTemp")

        # Validate humidity window
        if self.maxHumidity < self.minHumidity:
            raise ValueError("maxHumidity must be greater than or equal to minHumidity")
        if not self.minHumidity <= self.meanHumidity <= self.maxHumidity:
            raise ValueError("meanHumidity must be between minHumidity and maxHumidity")
        if not self.minHumidity <= self.currentHumidity <= self.maxHumidity:
            raise ValueError("currentHumidity must be between minHumidity and maxHumidity")

        # Validate CO2 window
        if self.maxCO2 < self.minCO2:
            raise ValueError("maxCO2 must be greater than or equal to minCO2")
        if not self.minCO2 <= self.meanCO2 <= self.maxCO2:
            raise ValueError("meanCO2 must be between minCO2 and maxCO2")
        if not self.minCO2 <= self.currentCO2 <= self.maxCO2:
            raise ValueError("currentCO2 must be between minCO2 and maxCO2")

        # Validate light window
        if self.maxLight < self.minLight:
            raise ValueError("maxLight must be greater than or equal to minLight")
        if not self.minLight <= self.meanLight <= self.maxLight:
            raise ValueError("meanLight must be between minLight and maxLight")
        if not self.minLight <= self.currentLight <= self.maxLight:
            raise ValueError("currentLight must be between minLight and maxLight")

        # Validate noise window
        if self.maxNoise < self.minNoise:
            raise ValueError("maxNoise must be greater than or equal to minNoise")
        if not self.minNoise <= self.meanNoise <= self.maxNoise:
            raise ValueError("meanNoise must be between minNoise and maxNoise")
        if not self.minNoise <= self.currentNoise <= self.maxNoise:
            raise ValueError("currentNoise must be between minNoise and maxNoise")

        return self


class PredictionResponse(BaseModel):
    rating: int = Field(ge=1, le=5)


class InstantPredictionRequest(BaseModel):
    temperature: float = Field(allow_inf_nan=False)
    humidity: float = Field(allow_inf_nan=False)
    co2_level: float = Field(alias="co2Level", allow_inf_nan=False)
    light_level: float = Field(alias="lightLevel", allow_inf_nan=False)
    noise: float = Field(default=29.0, allow_inf_nan=False)

    model_config = {"populate_by_name": True}


class InstantPredictionResponse(BaseModel):
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


@app.get("/collect-data")
def collect_data() -> dict[str, object]:
    db_host = os.environ["DB_HOST"]
    db_port = os.environ["DB_PORT"]
    db_name = os.environ["DB_NAME"]
    db_user = os.environ["DB_USER"]
    db_password = os.environ["DB_PASSWORD"]

    try:
        with psycopg.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_password,
        ) as conn:
            with conn.cursor() as cur:
                query = """
                    SELECT *
                    FROM data
                    ORDER BY sent_at DESC
                    LIMIT 2000
                """
                cur.execute(query)
                rows = cur.fetchall()
                colnames = [desc[0] for desc in cur.description]

                if not rows:
                    return {"message": "No data found in database"}

                REAL_SENSOR_HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
                with REAL_SENSOR_HISTORY_PATH.open(mode="w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(colnames)
                    writer.writerows(rows)

        # Run the transformation script to create session aggregates
        transform_real_data(input_file=REAL_SENSOR_HISTORY_PATH)

        return {
            "message": "Data collection complete and transformed to focus dataset",
            "count": len(rows),
            "columns": colnames,
            "saved_to": str(REAL_SENSOR_HISTORY_PATH),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/export-data")
def export_data(
    limit: int = Query(default=2000, ge=1, le=10000),
    _: None = Depends(_require_export_token),
) -> StreamingResponse:
    db_host = os.environ["DB_HOST"]
    db_port = os.environ["DB_PORT"]
    db_name = os.environ["DB_NAME"]
    db_user = os.environ["DB_USER"]
    db_password = os.environ["DB_PASSWORD"]

    try:
        with psycopg.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_password,
        ) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT *
                    FROM data
                    ORDER BY sent_at DESC
                    LIMIT %s
                """, (limit,))
                data_rows = cur.fetchall()
                data_cols = [desc[0] for desc in cur.description]

                cur.execute("""
                    SELECT *
                    FROM sessions
                    ORDER BY started_at DESC
                """)
                session_rows = cur.fetchall()
                session_cols = [desc[0] for desc in cur.description]

        if not data_rows and not session_rows:
            raise HTTPException(status_code=404, detail="No data found in database")

        def _to_csv(cols, rows) -> bytes:
            buf = io.StringIO()
            writer = csv.writer(buf)
            writer.writerow(cols)
            writer.writerows(rows)
            return buf.getvalue().encode()

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("sensor_history.csv", _to_csv(data_cols, data_rows))
            zf.writestr("sessions.csv", _to_csv(session_cols, session_rows))
        zip_buffer.seek(0)

        headers = {"Content-Disposition": "attachment; filename=export.zip"}
        return StreamingResponse(zip_buffer, media_type="application/zip", headers=headers)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/model-info")
def get_model_info() -> dict[str, object]:
    if MODEL_PATH.exists():
        last_modified = datetime.fromtimestamp(MODEL_PATH.stat().st_mtime).isoformat()
        return {
            "status": "available",
            "last_modified": last_modified,
            "model": "MLPClassifier",
            "features": FEATURE_COLUMNS,
        }
    return {"status": "not_found", "model": "MLPClassifier", "features": FEATURE_COLUMNS}


@app.post("/predict", response_model=PredictionResponse)
async def get_prediction(data: PredictionRequest) -> PredictionResponse:
    rating = predict(
        data.currentTemperature,
        data.maxTemp,
        data.minTemp,
        data.meanTemp,
        data.currentHumidity,
        data.maxHumidity,
        data.minHumidity,
        data.meanHumidity,
        data.currentCO2,
        data.maxCO2,
        data.minCO2,
        data.meanCO2,
        data.currentLight,
        data.maxLight,
        data.minLight,
        data.meanLight,
        data.currentNoise,
        data.maxNoise,
        data.minNoise,
        data.meanNoise,
    )
    return PredictionResponse(rating=rating)


@app.post("/instant-predict", response_model=InstantPredictionResponse)
async def get_instant_prediction(data: InstantPredictionRequest) -> InstantPredictionResponse:
    rating = predict_instant(
        humidity=data.humidity,
        light=data.light_level,
        temperature=data.temperature,
        noise=data.noise,
        co2=data.co2_level,
    )
    return InstantPredictionResponse(rating=rating)
