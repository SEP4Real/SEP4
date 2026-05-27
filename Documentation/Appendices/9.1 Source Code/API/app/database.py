import os
import psycopg
import asyncio
from psycopg.rows import dict_row

DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ["DB_NAME"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]

CONNINFO = (
    f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} "
    f"user={DB_USER} password={DB_PASSWORD}"
)

async def get_db():
    conn = await psycopg.AsyncConnection.connect(CONNINFO, row_factory=dict_row)
    try:
        yield conn
    finally:
        await conn.close()

async def cleanup_sessions(interval: int = 30):
    while True:
        await asyncio.sleep(interval)
        conn = await psycopg.AsyncConnection.connect(CONNINFO, row_factory=dict_row)
        try:
            await conn.execute("""
                UPDATE sessions
                SET is_ended = TRUE
                WHERE NOT is_ended
                  AND last_pulse_at < now() - INTERVAL '30 seconds'
            """)
            await conn.commit()
        finally:
            await conn.close()

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS devices (
    id VARCHAR(255) PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS sessions (
    id BIGSERIAL PRIMARY KEY,
    device_id VARCHAR(255) NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_ended BOOLEAN NOT NULL DEFAULT FALSE,
    last_pulse_at TIMESTAMPTZ,
    CONSTRAINT fk_sessions_device FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS data (
    id BIGSERIAL PRIMARY KEY,
    session_id BIGINT NOT NULL,
    temperature FLOAT,
    humidity FLOAT,
    co2_level FLOAT,
    light_level FLOAT,
    sent_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    predicted_study_quality INT CHECK (predicted_study_quality BETWEEN 1 AND 5),
    CONSTRAINT fk_data_session FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE RESTRICT
);

-- MIGRATION PATCH: Safely add missing columns to existing tables
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS is_ended BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS last_pulse_at TIMESTAMPTZ;

ALTER TABLE sessions DROP CONSTRAINT IF EXISTS sessions_device_id_fkey;
ALTER TABLE data DROP CONSTRAINT IF EXISTS data_session_id_fkey;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_sessions_device'
    ) THEN
        ALTER TABLE sessions
        ADD CONSTRAINT fk_sessions_device
        FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE RESTRICT;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_data_session'
    ) THEN
        ALTER TABLE data
        ADD CONSTRAINT fk_data_session
        FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE RESTRICT;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS ix_sessions_device_id ON sessions(device_id);
CREATE INDEX IF NOT EXISTS ix_sessions_started_at ON sessions(started_at);
CREATE INDEX IF NOT EXISTS ix_data_session_id ON data(session_id);
CREATE INDEX IF NOT EXISTS ix_data_sent_at ON data(sent_at);
CREATE INDEX IF NOT EXISTS idx_sessions_last_pulse_at ON sessions(last_pulse_at) WHERE is_ended IS FALSE;

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS calendar_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    title VARCHAR(255) NOT NULL,
    note TEXT,

    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,

    all_day BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,

    university VARCHAR(255),
    study_program VARCHAR(255),
    study_year VARCHAR(50),
    study_goal TEXT,

    preferred_temp INT DEFAULT 22,
    preferred_co2 INT DEFAULT 800,

    connected_device_id VARCHAR(255),
    profile_picture TEXT
);

ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS connected_device_id VARCHAR(255);

CREATE TABLE IF NOT EXISTS ratings (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    device_id VARCHAR(255) NOT NULL,
    session_id BIGINT NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    
    CONSTRAINT fk_ratings_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_ratings_device FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
    CONSTRAINT fk_ratings_session FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);
"""


async def ensure_schema_created():
    async with await psycopg.AsyncConnection.connect(CONNINFO, row_factory=dict_row) as conn:
        await conn.execute(SCHEMA_SQL)
        await conn.commit()
