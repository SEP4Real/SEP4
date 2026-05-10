import os
import psycopg
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

import auth 

app = FastAPI(title="Frontend API Gateway")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DATA MODELS (Pydantic) 
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class UserRating(BaseModel):
    rating: int # Scale 1-5

# CONEX DB 
def get_db_connection():
    return psycopg.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )

# ENDPOINT

@app.get("/")
def root():
    return {"message": "Frontend Backend is active"}

# Endpoint for connection check
@app.get("/db-check")
def db_check():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# AUT.logic (JWT)

@app.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    # search for the user in the real database
    # test user
    if request.username == "student@test.com" and request.password == "123":
        # generate the token using the function in auth.py
        token = auth.create_access_token(data={"sub": request.username})
        return {"access_token": token, "token_type": "bearer"}
    
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post("/register")
async def register(user_data: dict):
    # ("INSERT INTO users...")
    print(f"Register the user: {user_data}")
    return {"message": "User created successfully", "ok": True}

# data logic (Rating & History) 

@app.post("/rate-session")
async def save_rating(rating_data: UserRating):
    # Here we save the rating (1-5) for the current session in PostgreSQL
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO ratings (value, created_at) VALUES (%s, NOW())",
                    (rating_data.rating,)
                )
                conn.commit()
        return {"message": "Rating saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))