import os

from fastapi import FastAPI
import psycopg


app = FastAPI(title="MAL API")


@app.get("/")
def hello_world() -> dict[str, str]:
    return {"message": "Hello world from MAL FastAPI"}


@app.get("/db-check")
def db_check() -> dict[str, str | int]:
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://study:study@postgres:5432/sep4",
    )

    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()

    return {"status": "ok", "result": result[0] if result else 0}