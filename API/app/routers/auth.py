from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.database import get_db
from passlib.context import CryptContext
from fastapi import HTTPException

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# request body for registration
class RegisterRequest(BaseModel):
    name: str
    last_name: str
    email: str
    password: str

@router.post("/register")
async def register(data: RegisterRequest, db=Depends(get_db)):

    # check if email already exists
    result = await db.execute(
        """
        SELECT * FROM users
        WHERE email = %s
        """,
        (data.email,)
    )

    existing_user = await result.fetchone()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # hash password
    hashed_password = pwd_context.hash(data.password)

    print("REGISTERED USER:")
    print(data.email)
    print(hashed_password)

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
            hashed_password
        )
    )

    # save changes to db
    await db.commit()

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
    if not pwd_context.verify(data.password, user["password"]):
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