from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ── Device ────────────────────────────────────────────────────────────────────

class DeviceCreate(BaseModel):
    public_key: str = Field(..., alias="publicKey", max_length=255)

    model_config = {"populate_by_name": True}


class Device(BaseModel):
    public_key: str = Field(..., alias="publicKey")

    model_config = {"populate_by_name": True, "from_attributes": True}

    @classmethod
    def from_row(cls, row: dict) -> "Device":
        return cls(publicKey=row["public_key"])


# ── Session ───────────────────────────────────────────────────────────────────

class SessionCreate(BaseModel):
    device_id: str = Field(..., alias="deviceId")
    study_quality: Optional[int] = Field(None, alias="studyQuality", ge=1, le=10)

    model_config = {"populate_by_name": True}


class Session(BaseModel):
    id: int
    device_id: str = Field(..., alias="deviceId")
    started_at: datetime = Field(..., alias="startedAt")
    ended_at: Optional[datetime] = Field(None, alias="endedAt")
    last_pulse_at: Optional[datetime] = Field(None, alias="lastPulseAt")
    study_quality: Optional[int] = Field(None, alias="studyQuality", ge=1, le=10)

    model_config = {"populate_by_name": True}

    @classmethod
    def from_row(cls, row: dict) -> "Session":
        return cls(
            id=row["id"],
            deviceId=row["device_id"],
            startedAt=row["started_at"],
            endedAt=row.get("ended_at"),
            lastPulseAt=row.get("last_pulse_at"),
            studyQuality=row.get("study_quality"),
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
        )
