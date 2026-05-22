from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
from app.database import get_db
from app.security import get_current_user

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UpdateProfileRequest(BaseModel):
    university: str | None = None
    study_program: str | None = None
    study_year: str | None = None
    study_goal: str | None = None

    preferred_temp: int | None = None
    preferred_co2: int | None = None

    profile_picture: str | None = None

class UpdatePasswordRequest(BaseModel):
    current_password: str
    new_password: str

@router.get("/profile")
async def get_profile(
    current_user=Depends(get_current_user),
    db=Depends(get_db)):

    async with db.cursor() as cur:
        await cur.execute(
            """
            SELECT *
            FROM user_profiles
            WHERE user_id = %s
            """,
            (current_user["id"],)
        )
        profile = await cur.fetchone()

    return {
        "user": {
            "id": str(current_user["id"]),
            "name": current_user["name"],
            "last_name": current_user["last_name"],
            "email": current_user["email"]
        },
        "profile": profile
    }

@router.put("/profile")
async def update_profile(
    data: UpdateProfileRequest,
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    async with db.cursor() as cur:
        await cur.execute(
            """
            INSERT INTO user_profiles (
                user_id,
                university,
                study_program,
                study_year,
                study_goal,
                preferred_temp,
                preferred_co2,
                profile_picture
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)

            ON CONFLICT (user_id)
            DO UPDATE SET
                university = EXCLUDED.university,
                study_program = EXCLUDED.study_program,
                study_year = EXCLUDED.study_year,
                study_goal = EXCLUDED.study_goal,
                preferred_temp = EXCLUDED.preferred_temp,
                preferred_co2 = EXCLUDED.preferred_co2,
                profile_picture = EXCLUDED.profile_picture
            """,
            (
                current_user["id"],
                data.university,
                data.study_program,
                data.study_year,
                data.study_goal,
                data.preferred_temp,
                data.preferred_co2,
                data.profile_picture
            )
        )

    await db.commit()

    return {
        "message": "Profile updated successfully"
    }

@router.put("/profile/password")
async def update_password(
    data: UpdatePasswordRequest,
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    if len(data.new_password) < 8:
        raise HTTPException(status_code=400, detail="New password too short")

    if not pwd_context.verify(data.current_password, current_user["password"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    hashed_password = pwd_context.hash(data.new_password)

    async with db.cursor() as cur:
        await cur.execute(
            """
            UPDATE users
            SET password = %s
            WHERE id = %s
            """,
            (hashed_password, current_user["id"])
        )

    await db.commit()

    return {
        "message": "Password changed successfully"
    }
