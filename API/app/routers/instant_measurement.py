from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from psycopg import AsyncConnection
from pydantic import BaseModel, Field

from app.database import get_db

router = APIRouter(prefix="/instant-measurement", tags=["instant-measurement"])


class InstantMeasurementRequest(BaseModel):
    temperature: float = Field(..., ge=-20, le=60)
    humidity: float = Field(..., ge=0, le=100)
    co2_level: float = Field(..., alias="co2Level", ge=0, le=10000)
    light_level: float = Field(..., alias="lightLevel", ge=0, le=100000)

    model_config = {"populate_by_name": True}


class InstantMeasurementResponse(BaseModel):
    decision: Literal["stay", "leave"]


def decide_stay_or_leave(measurement: InstantMeasurementRequest) -> Literal["stay", "leave"]:
    if measurement.temperature < 18 or measurement.temperature > 30:
        return "leave"
    if measurement.humidity < 30 or measurement.humidity > 70:
        return "leave"
    if measurement.co2_level > 1500:
        return "leave"
    if measurement.light_level < 100:
        return "leave"
    return "stay"


@router.post("", response_model=InstantMeasurementResponse, status_code=201)
async def create_instant_measurement(
    body: InstantMeasurementRequest,
) -> InstantMeasurementResponse:
    return InstantMeasurementResponse(decision=decide_stay_or_leave(body))


@router.get("/latest", response_model=InstantMeasurementResponse)
async def get_latest_instant_measurement(
    session_id: int | None = Query(default=None, alias="sessionId"),
    device_id: str | None = Query(default=None, alias="deviceId"),
    db: AsyncConnection = Depends(get_db),
) -> InstantMeasurementResponse:
    conditions: list[str] = []
    params: list[object] = []

    if session_id is not None:
        conditions.append("d.session_id = %s")
        params.append(session_id)
    if device_id is not None:
        conditions.append("s.device_id = %s")
        params.append(device_id)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    async with db.cursor() as cur:
        await cur.execute(
            f"""
            SELECT
                d.temperature,
                d.humidity,
                d.co2_level,
                d.light_level
            FROM data d
            JOIN sessions s ON d.session_id = s.id
            {where_clause}
            ORDER BY d.sent_at DESC
            LIMIT 1
            """,
            params,
        )
        row = await cur.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="No sensor measurements found")

    measurement = InstantMeasurementRequest(
        temperature=row["temperature"],
        humidity=row["humidity"],
        co2Level=row["co2_level"],
        lightLevel=row["light_level"],
    )
    return InstantMeasurementResponse(decision=decide_stay_or_leave(measurement))
