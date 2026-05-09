import os
import psycopg
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


def get_conn() -> psycopg.Connection:
    return psycopg.connect(CONNINFO, row_factory=dict_row)


async def get_aconn() -> psycopg.AsyncConnection:
    return await psycopg.AsyncConnection.connect(CONNINFO, row_factory=dict_row)


async def get_db():
    conn = await psycopg.AsyncConnection.connect(CONNINFO, row_factory=dict_row)
    try:
        yield conn
    finally:
        await conn.close()


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS devices (
    public_key VARCHAR(255) PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS sessions (
    id BIGSERIAL PRIMARY KEY,
    device_id VARCHAR(255) NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    ended_at TIMESTAMPTZ,
    last_pulse_at TIMESTAMPTZ,
    study_quality INT CHECK (study_quality BETWEEN 1 AND 10),
    CONSTRAINT fk_sessions_device FOREIGN KEY (device_id) REFERENCES devices(public_key) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS data (
    id BIGSERIAL PRIMARY KEY,
    session_id BIGINT NOT NULL,
    temperature FLOAT,
    humidity FLOAT,
    co2_level FLOAT,
    light_level FLOAT,
    sent_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_data_session FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE RESTRICT
);

ALTER TABLE sessions DROP CONSTRAINT IF EXISTS sessions_device_id_fkey;
ALTER TABLE data DROP CONSTRAINT IF EXISTS data_session_id_fkey;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_sessions_device'
    ) THEN
        ALTER TABLE sessions
        ADD CONSTRAINT fk_sessions_device
        FOREIGN KEY (device_id) REFERENCES devices(public_key) ON DELETE RESTRICT;
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
"""


async def ensure_schema_created():
    conn = await get_aconn()
    async with conn:
        await conn.execute(SCHEMA_SQL)
        await conn.commit()
