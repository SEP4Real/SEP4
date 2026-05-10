from fastapi import APIRouter, Depends, HTTPException
from psycopg import AsyncConnection

from app.database import get_db
from app.models import Device, DeviceCreate

router = APIRouter(prefix="/device", tags=["device"])


@router.get("", response_model=list[Device])
async def get_all(db: AsyncConnection = Depends(get_db)):
    async with db.cursor() as cur:
        await cur.execute("SELECT public_key FROM devices")
        rows = await cur.fetchall()
    return [Device.from_row(r) for r in rows]


@router.get("/{public_key}", response_model=Device)
async def get_by_key(public_key: str, db: AsyncConnection = Depends(get_db)):
    async with db.cursor() as cur:
        await cur.execute("SELECT public_key FROM devices WHERE public_key = %s", (public_key,))
        row = await cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return Device.from_row(row)


@router.post("", response_model=Device, status_code=201)
async def create_device(body: DeviceCreate, db: AsyncConnection = Depends(get_db)):
    key = body.public_key.strip()
    if not key:
        raise HTTPException(status_code=400, detail="Device publicKey is required")

    async with db.cursor() as cur:
        await cur.execute("SELECT 1 FROM devices WHERE public_key = %s", (key,))
        if await cur.fetchone():
            raise HTTPException(status_code=409, detail=f"Device {key} already exists")

        await cur.execute("INSERT INTO devices (public_key) VALUES (%s)", (key,))
    await db.commit()
    return Device(publicKey=key)


@router.delete("/{public_key}", status_code=204)
async def delete_device(public_key: str, db: AsyncConnection = Depends(get_db)):
    async with db.cursor() as cur:
        await cur.execute("SELECT 1 FROM devices WHERE public_key = %s", (public_key,))
        if not await cur.fetchone():
            raise HTTPException(status_code=404, detail="Device not found")

        await cur.execute("SELECT 1 FROM sessions WHERE device_id = %s LIMIT 1", (public_key,))
        if await cur.fetchone():
            raise HTTPException(
                status_code=409,
                detail="Device has sessions and cannot be deleted without losing IoT history",
            )

        await cur.execute("DELETE FROM devices WHERE public_key = %s", (public_key,))
    await db.commit()
