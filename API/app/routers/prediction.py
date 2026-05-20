from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from psycopg import AsyncConnection

from app.database import get_db
from app.models import DataCreate, DataPointResponse

from datetime import timedelta
import httpx

import os

router = APIRouter(prefix="/predict", tags=["predict"])

@router.post("", response_model=DataPointResponse, status_code=201)
async def predict_study_quality(body: DataCreate, db: AsyncConnection = Depends(get_db)):
    return DataPointResponse(study_quality = 1);
