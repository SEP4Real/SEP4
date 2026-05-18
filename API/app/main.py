import asyncio
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.database import ensure_schema_created
from app.routers import device, session, data, health, auth, profile, calendar, dashboard
from app.database import cleanup_sessions

@asynccontextmanager
async def lifespan(app: FastAPI):
    await ensure_schema_created()
    task = asyncio.create_task(cleanup_sessions())
    yield
    task.cancel();

app = FastAPI(title="API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(device.router)
app.include_router(session.router)
app.include_router(data.router)
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(calendar.router)
app.include_router(dashboard.router)


