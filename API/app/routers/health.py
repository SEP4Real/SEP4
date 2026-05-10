from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from psycopg import AsyncConnection

from app.database import get_db

router = APIRouter(prefix="/health", tags=["health"])

REQUIRED_TABLES = ("devices", "sessions", "data")


@router.get("/db")
async def db_health(db: AsyncConnection = Depends(get_db)):
    try:
        async with db.cursor() as cur:
            await cur.execute("SELECT 1")
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": "unreachable"},
        )

    missing = []
    async with db.cursor() as cur:
        for table in REQUIRED_TABLES:
            await cur.execute(
                "SELECT to_regclass(%s) IS NOT NULL AS exists",
                (f"public.{table}",),
            )
            row = await cur.fetchone()
            if not row or not row["exists"]:
                missing.append(table)

    if missing:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "missingTables": missing},
        )

    return {"status": "ok", "tables": list(REQUIRED_TABLES)}
