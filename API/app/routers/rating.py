from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.database import get_db
from app.security import get_current_user

router = APIRouter()


class RatingRequest(BaseModel):
    device_id: str
    session_id: int
    rating: int
    comment: str | None = None


@router.post("/ratings")
async def create_rating(
    data: RatingRequest,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):

    if data.rating < 1 or data.rating > 5:
        raise HTTPException(
            status_code=400,
            detail="Rating must be between 1 and 5"
        )

    await db.execute(
        """
        INSERT INTO ratings (
            user_id,
            device_id,
            session_id,
            rating,
            comment
        )
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            current_user["id"],
            data.device_id,
            data.session_id,
            data.rating,
            data.comment
        )
    )

    await db.commit()

    return {
        "message": "Rating saved"
    }