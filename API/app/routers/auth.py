from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.database import get_db

router = APIRouter()

class RegisterRequest(BaseModel):
    name: str
    last_name: str
    email: str
    password: str

@router.post("/register")
async def register(data: RegisterRequest, db=Depends(get_db)):
    await db.execute(
        """
        INSERT INTO users (name, last_name, email, password)
        VALUES (%s, %s, %s, %s)
        """,
        (
            data.name,
            data.last_name,
            data.email,
            data.password
        )
    )

    await db.commit()

    return {"message": "User created"}