from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.database import get_db
from passlib.context import CryptContext
from fastapi import HTTPException
from jose import jwt
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
security = HTTPBearer()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM)

    return encoded_jwt

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db=Depends(get_db)):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM])

        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token")

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token")

    result = await db.execute(
        """
        SELECT * FROM users
        WHERE id = %s
        """,
        (user_id,))
    user = await result.fetchone()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found")
    return user

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

    access_token = create_access_token(data={"sub": str(user["id"])})
    
    # success → return user data
    return {
        "message": "Login successful",
        "access_token": access_token,
        "user": {
            "id": str(user["id"]),
            "name": user["name"],
            "email": user["email"]
        }
    }

class UpdateProfileRequest(BaseModel):
    university: str | None = None
    study_program: str | None = None
    study_year: str | None = None
    study_goal: str | None = None

    preferred_temp: int | None = None
    preferred_co2: int | None = None

    profile_picture: str | None = None

@router.get("/profile")
async def get_profile(
    current_user=Depends(get_current_user),
    db=Depends(get_db)):

    result = await db.execute(
        """
        SELECT *
        FROM user_profiles
        WHERE user_id = %s
        """,
        (current_user["id"],)
    )

    profile = await result.fetchone()

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
    await db.execute(
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