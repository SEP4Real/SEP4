from jose import jwt
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from fastapi import Cookie, Depends, HTTPException
from app.database import get_db

SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
AUTH_COOKIE_NAME = "access_token"
security = HTTPBearer(auto_error=False)

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
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    cookie_token: str | None = Cookie(default=None, alias=AUTH_COOKIE_NAME),
    db=Depends(get_db)):
    token = cookie_token or (credentials.credentials if credentials else None)

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated")

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
