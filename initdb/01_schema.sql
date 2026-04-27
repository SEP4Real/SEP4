CREATE TABLE devices (
    public_key  VARCHAR(255) PRIMARY KEY
);

CREATE TABLE sessions (
    id            BIGSERIAL PRIMARY KEY,
    device_id     VARCHAR(255) NOT NULL REFERENCES devices(public_key) ON DELETE CASCADE,
    started_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    ended_at      TIMESTAMPTZ,
    last_pulse_at TIMESTAMPTZ,
    study_quality INT CHECK (study_quality BETWEEN 1 AND 10)
);

CREATE TABLE data (
    id          BIGSERIAL PRIMARY KEY,
    session_id  BIGINT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    temperature FLOAT,
    humidity    FLOAT,
    co2_level   FLOAT,
    light_level FLOAT,
    sent_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);