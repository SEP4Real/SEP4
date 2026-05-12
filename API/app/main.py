import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import ensure_schema_created
from app.routers import device, session, data, health
from app.database import cleanup_sessions

@asynccontextmanager
async def lifespan(app: FastAPI):
    await ensure_schema_created()
    task = asyncio.create_task(cleanup_sessions())
    yield
    task.cancel();


app = FastAPI(title="IoT API", lifespan=lifespan)

app.include_router(device.router)
app.include_router(session.router)
app.include_router(data.router)
app.include_router(health.router)
