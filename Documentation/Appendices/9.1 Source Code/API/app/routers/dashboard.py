from fastapi import APIRouter, Depends
from psycopg import AsyncConnection
from app.security import get_current_user

from app.database import get_db

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_data(
    current_user = Depends(get_current_user),
    db: AsyncConnection = Depends(get_db)
):
    async with db.cursor() as cur:
        await cur.execute(
            """
            SELECT
                d.id,
                d.temperature,
                d.humidity,
                d.co2_level,
                d.light_level,
                d.predicted_study_quality,
                d.sent_at,

                s.device_id,
                s.study_quality

            FROM data d
            JOIN sessions s
                ON d.session_id = s.id

            ORDER BY d.sent_at ASC
            """
        )

        rows = await cur.fetchall()

    return rows