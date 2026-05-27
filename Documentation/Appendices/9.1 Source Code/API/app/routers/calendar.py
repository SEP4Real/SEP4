from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.security import get_current_user

router = APIRouter()

# request model
class CalendarEventRequest(BaseModel):
    title: str
    note: str | None = None

    start_time: datetime
    end_time: datetime

    all_day: bool = False

@router.post("/calendar-events")
async def create_calendar_event(
    data: CalendarEventRequest,
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    result = await db.execute(
        """
        INSERT INTO calendar_events (
            user_id,
            title,
            note,
            start_time,
            end_time,
            all_day
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING *
        """,
        (
            current_user["id"],
            data.title,
            data.note,
            data.start_time,
            data.end_time,
            data.all_day
        )
    )

    event = await result.fetchone()

    await db.commit()

    return event

@router.get("/calendar-events")
async def get_calendar_events(
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    result = await db.execute(
        """
        SELECT *
        FROM calendar_events
        WHERE user_id = %s
        ORDER BY start_time
        """,
        (current_user["id"],)
    )

    events = await result.fetchall()

    return events

@router.delete("/calendar-events/{event_id}")
async def delete_calendar_event(
    event_id: str,
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    result = await db.execute(
        """
        DELETE FROM calendar_events
        WHERE id = %s
        AND user_id = %s
        """,
        (
            event_id,
            current_user["id"]
        )
    )

    await db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Calendar event not found")

    return {
        "message": "Event deleted successfully"
    }

@router.put("/calendar-events/{event_id}")
async def update_calendar_event(
    event_id: str,
    data: CalendarEventRequest,
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    result = await db.execute(
        """
        UPDATE calendar_events
        SET
            title = %s,
            note = %s,
            start_time = %s,
            end_time = %s,
            all_day = %s
        WHERE id = %s
        AND user_id = %s
        RETURNING *
        """,
        (
            data.title,
            data.note,
            data.start_time,
            data.end_time,
            data.all_day,
            event_id,
            current_user["id"]
        )
    )

    event = await result.fetchone()

    await db.commit()

    if event is None:
        raise HTTPException(status_code=404, detail="Calendar event not found")

    return event
