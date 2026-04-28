CREATE TABLE devices (
    public_key  VARCHAR(255) PRIMARY KEY
);

CREATE TABLE sessions (
    id            BIGSERIAL PRIMARY KEY,
    device_id     VARCHAR(255) NOT NULL,
    started_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    ended_at      TIMESTAMPTZ,
    last_pulse_at TIMESTAMPTZ,
    study_quality INT CHECK (study_quality BETWEEN 1 AND 10),
    CONSTRAINT fk_sessions_device FOREIGN KEY (device_id) REFERENCES devices(public_key) ON DELETE RESTRICT
);

CREATE TABLE data (
    id          BIGSERIAL PRIMARY KEY,
    session_id  BIGINT NOT NULL,
    temperature FLOAT,
    humidity    FLOAT,
    co2_level   FLOAT,
    light_level FLOAT,
    sent_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_data_session FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE RESTRICT
);

CREATE INDEX ix_sessions_device_id ON sessions(device_id);
CREATE INDEX ix_sessions_started_at ON sessions(started_at);
CREATE INDEX ix_data_session_id ON data(session_id);
CREATE INDEX ix_data_sent_at ON data(sent_at);
