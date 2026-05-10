from fastapi import APIRouter, Depends, HTTPException
from psycopg import AsyncConnection

from app.database import get_db
from app.models import Device, DeviceCreate

router = APIRouter(prefix="/device", tags=["device"])


@router.get("", response_model=list[Device])
async def get_all(db: AsyncConnection = Depends(get_db)):
    async with db.cursor() as cur:
        await cur.execute("SELECT id FROM devices")
        rows = await cur.fetchall()
    return [Device.from_row(r) for r in rows]


@router.get("/{id}", response_model=Device)
async def get_by_key(id: str, db: AsyncConnection = Depends(get_db)):
    async with db.cursor() as cur:
        await cur.execute("SELECT id FROM devices WHERE id = %s", (id,))
        row = await cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return Device.from_row(row)


@router.post("", response_model=Device, status_code=201)
async def create_device(body: DeviceCreate, db: AsyncConnection = Depends(get_db)):
    key = body.id.strip()
    if not key:
        raise HTTPException(status_code=400, detail="Device id is required")

    async with db.cursor() as cur:
        await cur.execute("SELECT 1 FROM devices WHERE id = %s", (key,))
        if await cur.fetchone():
            raise HTTPException(status_code=409, detail=f"Device {key} already exists")

        await cur.execute("INSERT INTO devices (id) VALUES (%s)", (key,))
    await db.commit()
    return Device(id=key)


@router.delete("/{id}", status_code=204)
async def delete_device(id: str, db: AsyncConnection = Depends(get_db)):
    async with db.cursor() as cur:
        await cur.execute("SELECT 1 FROM devices WHERE id = %s", (id,))
        if not await cur.fetchone():
            raise HTTPException(status_code=404, detail="Device not found")

        await cur.execute("SELECT 1 FROM sessions WHERE device_id = %s LIMIT 1", (id,))
        if await cur.fetchone():
            raise HTTPException(
                status_code=409,
                detail="Device has sessions and cannot be deleted without losing IoT history",
            )

        await cur.execute("DELETE FROM devices WHERE id = %s", (id,))
    await db.commit()
