using Microsoft.EntityFrameworkCore;

namespace IOT_backend.DbConfig;

public static class DatabaseInitializer
{
    public static async Task EnsureSchemaCreatedAsync(IServiceProvider services)
    {
        using var scope = services.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();

        await db.Database.ExecuteSqlRawAsync("""
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
            """);
    }
}
