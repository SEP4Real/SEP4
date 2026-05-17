from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from psycopg import AsyncConnection

from app.database import get_db
from app.models import Session, SessionCreate, SessionUpdate

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


@router.get("/device/{id}", response_model=list[Session])
async def get_by_device(id: str, db: AsyncConnection = Depends(get_db)):
    async with db.cursor() as cur:
        await cur.execute("SELECT * FROM sessions WHERE device_id = %s", (id,))
        rows = await cur.fetchall()
    return [Session.from_row(r) for r in rows]


@router.get("/{id}", response_model=Session)
async def get_by_id(id: int, db: AsyncConnection = Depends(get_db)):
    async with db.cursor() as cur:
        await cur.execute("SELECT * FROM sessions WHERE id = %s", (id,))
        row = await cur.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Session not found")

    return Session.from_row(row)


@router.post("", response_model=Session, status_code=201)
async def create_session(body: SessionCreate, db: AsyncConnection = Depends(get_db)):
    device_id = body.device_id.strip()
    if not device_id:
        raise HTTPException(status_code=400, detail="deviceId is required")

    now = _now()
    async with db.cursor() as cur:
        await cur.execute("SELECT 1 FROM devices WHERE id = %s", (device_id,))
        if not await cur.fetchone():
            raise HTTPException(status_code=404, detail=f"Device {device_id} does not exist")

        await cur.execute(
            """
            INSERT INTO sessions (device_id, started_at, last_pulse_at)
            VALUES (%s, %s, %s)
            RETURNING *
            """,
            (device_id, now, now),
        )
        row = await cur.fetchone()
    await db.commit()
    return Session.from_row(row)


@router.patch("/{id}/pulse")
async def pulse(id: int, db: AsyncConnection = Depends(get_db)):
    async with db.cursor() as cur:
        await cur.execute("SELECT is_ended FROM sessions WHERE id = %s", (id,))
        row = await cur.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Session not found")
    if row["is_ended"]:
        return {"alive": False}

    async with db.cursor() as cur:
        await cur.execute(
            "UPDATE sessions SET last_pulse_at = %s WHERE id = %s",
            (_now(), id),
        )
    await db.commit()
    return {"alive": True}


@router.patch("/{id}")
async def update_session(id: int, body: SessionUpdate, db: AsyncConnection = Depends(get_db)):
    async with db.cursor() as cur:
        await cur.execute("SELECT * FROM sessions WHERE id = %s", (id,))
        row = await cur.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Session not found")

    updates = {
        field: getattr(body, field)
        for field in body.model_fields_set
    }

    if updates:
        columns = ", ".join(f"{col} = %s" for col in updates)
        values = list(updates.values()) + [id]
        async with db.cursor() as cur:
            await cur.execute(f"UPDATE sessions SET {columns} WHERE id = %s RETURNING *", values)
            row = await cur.fetchone()
        await db.commit()

    return Session.from_row(row)


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
