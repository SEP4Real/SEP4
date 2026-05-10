from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from psycopg import AsyncConnection

from app.database import get_db
from app.models import DataCreate, DataPoint

router = APIRouter(prefix="/data", tags=["data"])


@router.get("", response_model=list[DataPoint])
async def get_all(db: AsyncConnection = Depends(get_db)):
    async with db.cursor() as cur:
        await cur.execute("SELECT * FROM data")
        rows = await cur.fetchall()
    return [DataPoint.from_row(r) for r in rows]


@router.get("/{id}", response_model=DataPoint)
async def get_by_id(id: int, db: AsyncConnection = Depends(get_db)):
    async with db.cursor() as cur:
        await cur.execute("SELECT * FROM data WHERE id = %s", (id,))
        row = await cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Data point not found")
    return DataPoint.from_row(row)


@router.get("/session/{session_id}", response_model=list[DataPoint])
async def get_by_session(session_id: int, db: AsyncConnection = Depends(get_db)):
    async with db.cursor() as cur:
        await cur.execute("SELECT * FROM data WHERE session_id = %s", (session_id,))
        rows = await cur.fetchall()
    return [DataPoint.from_row(r) for r in rows]


@router.post("", response_model=DataPoint, status_code=201)
async def create_data(body: DataCreate, db: AsyncConnection = Depends(get_db)):
    if body.session_id <= 0:
        raise HTTPException(status_code=400, detail="sessionId is required")

    async with db.cursor() as cur:
        await cur.execute("SELECT ended_at FROM sessions WHERE id = %s", (body.session_id,))
        session = await cur.fetchone()

    if session is None:
        raise HTTPException(status_code=404, detail=f"Session {body.session_id} does not exist")
    if session["ended_at"] is not None:
        raise HTTPException(status_code=409, detail="Cannot add data to an ended session")

    sent_at = datetime.now(tz=timezone.utc)
    async with db.cursor() as cur:
        await cur.execute(
            """
            INSERT INTO data (session_id, temperature, humidity, co2_level, light_level, sent_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (
                body.session_id,
                body.temperature,
                body.humidity,
                body.co2_level,
                body.light_level,
                sent_at,
            ),
        )
        row = await cur.fetchone()
    await db.commit()
    return DataPoint.from_row(row)
