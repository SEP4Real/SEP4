from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from psycopg import AsyncConnection

from app.database import get_db
from app.models import DataCreate, DataPointResponse

import httpx
import os

router = APIRouter(prefix="/predict", tags=["predict"])

def _last_non_null(values: list[float | None]) -> float | None:
    for value in reversed(values):
        if value is not None:
            return value
    return None


def _stats(values: list[float | None]) -> tuple[float | None, float | None, float | None, float | None]:
    clean = [value for value in values if value is not None]
    if not clean:
        return None, None, None, None
    current = _last_non_null(values)
    mean_value = round(sum(clean) / len(clean), 2)
    return current, max(clean), min(clean), mean_value


async def _get_current_session_id(db: AsyncConnection) -> int:
    async with db.cursor() as cur:
        await cur.execute(
            """
            SELECT id
            FROM sessions
            WHERE is_ended = FALSE
            ORDER BY last_pulse_at DESC NULLS LAST, started_at DESC
            LIMIT 1
            """
        )
        row = await cur.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="No active session found")

    return int(row["id"])


async def _get_session_rows(db: AsyncConnection, session_id: int) -> list[dict[str, object]]:
    async with db.cursor() as cur:
        await cur.execute(
            """
            SELECT temperature, humidity, co2_level, light_level, sent_at
            FROM data
            WHERE session_id = %s
            ORDER BY sent_at
            """,
            (session_id,),
        )
        rows = await cur.fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail="No sensor data for current session")

    return rows


def _linearize_session(rows: list[dict[str, object]]) -> dict[str, float | None]:
    temperatures = [row.get("temperature") for row in rows]
    humidities = [row.get("humidity") for row in rows]
    co2_levels = [row.get("co2_level") for row in rows]
    light_levels = [row.get("light_level") for row in rows]

    temp_current, temp_max, temp_min, temp_mean = _stats(temperatures)
    hum_current, hum_max, hum_min, hum_mean = _stats(humidities)
    co2_current, co2_max, co2_min, co2_mean = _stats(co2_levels)
    light_current, light_max, light_min, light_mean = _stats(light_levels)

    return {
        "currentTemperature": temp_current,
        "maxTemp": temp_max,
        "minTemp": temp_min,
        "meanTemp": temp_mean,
        "currentHumidity": hum_current,
        "maxHumidity": hum_max,
        "minHumidity": hum_min,
        "meanHumidity": hum_mean,
        "currentCO2": co2_current,
        "maxCO2": co2_max,
        "minCO2": co2_min,
        "meanCO2": co2_mean,
        "currentLight": light_current,
        "maxLight": light_max,
        "minLight": light_min,
        "meanLight": light_mean,
    }


@router.post("", response_model=DataPointResponse, status_code=201)
async def predict_study_quality(body: DataCreate, db: AsyncConnection = Depends(get_db)):
    _ = body

    session_id = await _get_current_session_id(db)
    rows = await _get_session_rows(db, session_id)
    payload = _linearize_session(rows)

    required = [
        "currentTemperature", "maxTemp", "minTemp", "meanTemp",
        "currentHumidity", "maxHumidity", "minHumidity", "meanHumidity",
        "currentCO2", "maxCO2", "minCO2", "meanCO2",
        "currentLight", "maxLight", "minLight", "meanLight"
    ]
    missing = [name for name in required if payload.get(name) is None]
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"Missing required sensor data: {', '.join(missing)}",
        )

    mal_base = os.getenv("MAL_API_HOST_PORT")
    if not mal_base:
        raise HTTPException(status_code=500, detail="MAL_API_HOST_PORT is not configured")

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(f"{mal_base}/predict", json=payload)

    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="MAL prediction failed")

    rating = response.json().get("rating")
    if not isinstance(rating, int):
        raise HTTPException(status_code=502, detail="MAL prediction returned invalid rating")

    return DataPointResponse(study_quality=rating)
