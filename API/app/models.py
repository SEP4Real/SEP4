from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ── Device ────────────────────────────────────────────────────────────────────

class DeviceCreate(BaseModel):
    id: str = Field(..., alias="id", max_length=255)

    model_config = {"populate_by_name": True}


class Device(BaseModel):
    id: str = Field(..., alias="id")

    model_config = {"populate_by_name": True, "from_attributes": True}

    @classmethod
    def from_row(cls, row: dict) -> "Device":
        return cls(id=row["id"])


# ── Session ───────────────────────────────────────────────────────────────────

class SessionCreate(BaseModel):
    device_id: str = Field(..., alias="deviceId")

    model_config = {"populate_by_name": True}


class SessionUpdate(BaseModel):
    device_id: Optional[str] = Field(None, alias="deviceId")
    started_at: Optional[datetime] = Field(None, alias="startedAt")
    is_ended: Optional[bool] = Field(None, alias="isEnded")
    last_pulse_at: Optional[datetime] = Field(None, alias="lastPulseAt")

    model_config = {"populate_by_name": True}


class Session(BaseModel):
    id: int
    device_id: str = Field(..., alias="deviceId")
    started_at: datetime = Field(..., alias="startedAt")
    is_ended: bool = Field(None, alias="isEnded")
    last_pulse_at: Optional[datetime] = Field(None, alias="lastPulseAt")

    model_config = {"populate_by_name": True}

    @classmethod
    def from_row(cls, row: dict) -> "Session":
        return cls(
            id=row["id"],
            deviceId=row["device_id"],
            startedAt=row["started_at"],
            isEnded=row.get("is_ended"),
            lastPulseAt=row.get("last_pulse_at"),
        )


# ── Data ──────────────────────────────────────────────────────────────────────

class DataCreate(BaseModel):
    session_id: int = Field(..., alias="sessionId")
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    co2_level: Optional[float] = Field(None, alias="co2Level")
    light_level: Optional[float] = Field(None, alias="lightLevel")

    model_config = {"populate_by_name": True}


class DataPoint(BaseModel):
    id: int
    session_id: int = Field(..., alias="sessionId")
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    co2_level: Optional[float] = Field(None, alias="co2Level")
    light_level: Optional[float] = Field(None, alias="lightLevel")
    sent_at: datetime = Field(..., alias="sentAt")
    predicted_study_quality: Optional[int] = Field(None, alias="predictedStudyQuality", ge=1, le=5)

    model_config = {"populate_by_name": True}

    @classmethod
    def from_row(cls, row: dict) -> "DataPoint":
        return cls(
            id=row["id"],
            sessionId=row["session_id"],
            temperature=row.get("temperature"),
            humidity=row.get("humidity"),
            co2Level=row.get("co2_level"),
            lightLevel=row.get("light_level"),
            sentAt=row["sent_at"],
            predicted_study_quality=row["predicted_study_quality"],
        )

class DataPointResponse(BaseModel):
    study_quality: int = Field(ge=-1, le=5)

