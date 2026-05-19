CREATE TABLE devices (
    id  VARCHAR(255) PRIMARY KEY
);

CREATE TABLE sessions (
    id            BIGSERIAL PRIMARY KEY,
    device_id     VARCHAR(255) NOT NULL,
    started_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_ended BOOLEAN NOT NULL DEFAULT FALSE,
    last_pulse_at TIMESTAMPTZ,
    study_quality INT CHECK (study_quality BETWEEN 1 AND 5),
    CONSTRAINT fk_sessions_device FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE RESTRICT
);

CREATE TABLE data (
    id          BIGSERIAL PRIMARY KEY,
    session_id  BIGINT NOT NULL,
    temperature FLOAT,
    humidity    FLOAT,
    co2_level   FLOAT,
    light_level FLOAT,
    sent_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    predicted_study_quality INT CHECK (predicted_study_quality BETWEEN 1 AND 5),
    CONSTRAINT fk_data_session FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE RESTRICT
);

CREATE INDEX ix_sessions_device_id ON sessions(device_id);
CREATE INDEX ix_sessions_started_at ON sessions(started_at);
CREATE INDEX ix_data_session_id ON data(session_id);
CREATE INDEX ix_data_sent_at ON data(sent_at);
CREATE INDEX idx_sessions_last_pulse_at ON sessions(last_pulse_at) WHERE is_ended IS FALSE;

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

CREATE TABLE IF NOT EXISTS ratings (
    id BIGSERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    device_id VARCHAR(255) NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    
    CONSTRAINT fk_ratings_user FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE,
    CONSTRAINT fk_ratings_device FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
);