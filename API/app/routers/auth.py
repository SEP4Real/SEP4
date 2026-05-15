from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.database import get_db

router = APIRouter()

# request body for registration
class RegisterRequest(BaseModel):
    name: str
    last_name: str
    email: str
    password: str

@router.post("/register")
async def register(data: RegisterRequest, db=Depends(get_db)):

    # insert new user to db
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

    # save changes to db
    await db.commit()

    # success
    return {"message": "User created"}


# request body for user login
class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
async def login(data: LoginRequest, db=Depends(get_db)):

    # find user with matching email
    result = await db.execute(
        """
        SELECT * FROM users
        WHERE email = %s
        """,
        (data.email,)
    )

    user = await result.fetchone()

    # failed: user does not exist
    if not user:
        return {"error": "Invalid credentials"}

    # failed: incorrect password
    if user["password"] != data.password:
        return {"error": "Invalid credentials"}

    # success → return user data
    return {
        "message": "Login successful",
        "user": {
            "id": str(user["id"]),
            "name": user["name"],
            "email": user["email"]
        }
    }