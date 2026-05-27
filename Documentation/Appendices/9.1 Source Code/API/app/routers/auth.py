import os
from time import monotonic
from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel
from app.database import get_db
from passlib.context import CryptContext
from fastapi import HTTPException
from app.security import AUTH_COOKIE_NAME, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token


router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

LOGIN_RATE_LIMIT_ATTEMPTS = 5
LOGIN_RATE_LIMIT_WINDOW_SECONDS = 15 * 60
AUTH_COOKIE_SECURE = os.getenv("AUTH_COOKIE_SECURE", "false").lower() == "true"
AUTH_COOKIE_SAMESITE = os.getenv("AUTH_COOKIE_SAMESITE", "lax")
login_attempts = {}


def _login_rate_key(request: Request, email: str) -> str:
    client_host = request.client.host if request.client else "unknown"
    return f"{client_host}:{email.lower()}"


def _is_login_rate_limited(key: str) -> bool:
    now = monotonic()
    attempts = [
        timestamp
        for timestamp in login_attempts.get(key, [])
        if now - timestamp < LOGIN_RATE_LIMIT_WINDOW_SECONDS
    ]
    login_attempts[key] = attempts
    return len(attempts) >= LOGIN_RATE_LIMIT_ATTEMPTS


def _record_failed_login(key: str) -> None:
    now = monotonic()
    attempts = [
        timestamp
        for timestamp in login_attempts.get(key, [])
        if now - timestamp < LOGIN_RATE_LIMIT_WINDOW_SECONDS
    ]
    attempts.append(now)
    login_attempts[key] = attempts


def _clear_failed_logins(key: str) -> None:
    login_attempts.pop(key, None)



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
async def login(
    data: LoginRequest,
    request: Request,
    response: Response,
    db=Depends(get_db)
):
    rate_key = _login_rate_key(request, data.email)

    if _is_login_rate_limited(rate_key):
        raise HTTPException(
            status_code=429,
            detail="Too many login attempts. Please try again later."
        )

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
        _record_failed_login(rate_key)
        return {"error": "Invalid credentials"}

    # failed: incorrect password
    if not pwd_context.verify(data.password, user["password"]):
        _record_failed_login(rate_key)
        return {"error": "Invalid credentials"}

    _clear_failed_logins(rate_key)
    access_token = create_access_token(data={"sub": str(user["id"])})
    response.set_cookie(
        key=AUTH_COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=AUTH_COOKIE_SECURE,
        samesite=AUTH_COOKIE_SAMESITE,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    
    # success → return user data
    return {
        "message": "Login successful",
        "user": {
            "id": str(user["id"]),
            "name": user["name"],
            "email": user["email"]
        }
    }


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key=AUTH_COOKIE_NAME,
        httponly=True,
        secure=AUTH_COOKIE_SECURE,
        samesite=AUTH_COOKIE_SAMESITE,
    )
    return {"message": "Logged out"}
