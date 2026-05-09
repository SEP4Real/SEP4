from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from psycopg import AsyncConnection

from app.database import get_db
from app.models import Session, SessionCreate

router = APIRouter(prefix="/session", tags=["session"])

PULSE_TIMEOUT_SECONDS = 15


def _now() -> datetime:
    return datetime.now(tz=timezone.utc)


@router.get("", response_model=list[Session])
async def get_all(db: AsyncConnection = Depends(get_db)):
    async with db.cursor() as cur:
        await cur.execute("SELECT * FROM sessions")
        rows = await cur.fetchall()
    return [Session.from_row(r) for r in rows]


@router.get("/device/{public_key}", response_model=list[Session])
async def get_by_device(public_key: str, db: AsyncConnection = Depends(get_db)):
    async with db.cursor() as cur:
        await cur.execute("SELECT * FROM sessions WHERE device_id = %s", (public_key,))
        rows = await cur.fetchall()
    return [Session.from_row(r) for r in rows]


@router.get("/{id}", response_model=Session)
async def get_by_id(id: int, db: AsyncConnection = Depends(get_db)):
    async with db.cursor() as cur:
        await cur.execute("SELECT * FROM sessions WHERE id = %s", (id,))
        row = await cur.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Session not found")

    # Auto-end session if pulse timed out
    if row["ended_at"] is None and row["last_pulse_at"] is not None:
        elapsed = _now() - row["last_pulse_at"]
        if elapsed.total_seconds() > PULSE_TIMEOUT_SECONDS:
            ended_at = row["last_pulse_at"]
            async with db.cursor() as cur:
                await cur.execute(
                    "UPDATE sessions SET ended_at = %s WHERE id = %s",
                    (ended_at, id),
                )
            await db.commit()
            row = dict(row)
            row["ended_at"] = ended_at

    return Session.from_row(row)


@router.post("", response_model=Session, status_code=201)
async def create_session(body: SessionCreate, db: AsyncConnection = Depends(get_db)):
    device_id = body.device_id.strip()
    if not device_id:
        raise HTTPException(status_code=400, detail="deviceId is required")

    now = _now()
    async with db.cursor() as cur:
        await cur.execute("SELECT 1 FROM devices WHERE public_key = %s", (device_id,))
        if not await cur.fetchone():
            raise HTTPException(status_code=404, detail=f"Device {device_id} does not exist")

        await cur.execute(
            """
            INSERT INTO sessions (device_id, started_at, last_pulse_at, study_quality)
            VALUES (%s, %s, %s, %s)
            RETURNING *
            """,
            (device_id, now, now, body.study_quality),
        )
        row = await cur.fetchone()
    await db.commit()
    return Session.from_row(row)


@router.patch("/{id}/end", response_model=Session)
async def end_session(id: int, study_quality: Optional[int] = None, db: AsyncConnection = Depends(get_db)):
    async with db.cursor() as cur:
        await cur.execute("SELECT * FROM sessions WHERE id = %s", (id,))
        row = await cur.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Session not found")
    if row["ended_at"] is not None:
        raise HTTPException(status_code=409, detail="Session already ended")

    now = _now()
    async with db.cursor() as cur:
        await cur.execute(
            "UPDATE sessions SET ended_at = %s, study_quality = %s WHERE id = %s RETURNING *",
            (now, study_quality, id),
        )
        row = await cur.fetchone()
    await db.commit()
    return Session.from_row(row)


@router.patch("/{id}/pulse")
async def pulse(id: int, db: AsyncConnection = Depends(get_db)):
    async with db.cursor() as cur:
        await cur.execute("SELECT ended_at FROM sessions WHERE id = %s", (id,))
        row = await cur.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Session not found")
    if row["ended_at"] is not None:
        return {"alive": False}

    async with db.cursor() as cur:
        await cur.execute(
            "UPDATE sessions SET last_pulse_at = %s WHERE id = %s",
            (_now(), id),
        )
    await db.commit()
    return {"alive": True}


@router.delete("/{id}", status_code=204)
async def delete_session(id: int, db: AsyncConnection = Depends(get_db)):
    async with db.cursor() as cur:
        await cur.execute("SELECT 1 FROM sessions WHERE id = %s", (id,))
        if not await cur.fetchone():
            raise HTTPException(status_code=404, detail="Session not found")

        await cur.execute("SELECT 1 FROM data WHERE session_id = %s LIMIT 1", (id,))
        if await cur.fetchone():
            raise HTTPException(
                status_code=409,
                detail="Session has data points and cannot be deleted without losing IoT history",
            )

        await cur.execute("DELETE FROM sessions WHERE id = %s", (id,))
    await db.commit()
