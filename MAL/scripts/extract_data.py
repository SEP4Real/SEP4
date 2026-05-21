import csv
import io
import os
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

import psycopg

REAL_SENSOR_HISTORY_PATH = Path("data/sensor_history.csv")
SESSIONS_PATH = Path("data/sessions.csv")


def _collect_from_api(api_base_url: str) -> None:
    export_token = os.environ.get("MAL_API_EXPORT_TOKEN")
    export_limit = os.environ.get("MAL_API_EXPORT_LIMIT")

    if export_limit:
        try:
            limit_value = int(export_limit)
        except ValueError as exc:
            raise ValueError("MAL_API_EXPORT_LIMIT must be an integer") from exc
        url = f"{api_base_url.rstrip('/')}/export-data?limit={limit_value}"
    else:
        url = f"{api_base_url.rstrip('/')}/export-data"

    print("Fetching data from MAL API...")
    request = urllib.request.Request(url)
    if export_token:
        request.add_header("X-Export-Token", export_token)

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = response.read()
            if response.status != 200:
                body = payload.decode("utf-8", errors="replace")
                raise RuntimeError(f"API request failed with status {response.status}: {body}")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"API request failed with status {exc.code}: {body}") from exc

    REAL_SENSOR_HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(payload)) as zf:
        with zf.open("sensor_history.csv") as f:
            REAL_SENSOR_HISTORY_PATH.write_bytes(f.read())
        with zf.open("sessions.csv") as f:
            SESSIONS_PATH.write_bytes(f.read())
    print(f"Success: Extracted sensor_history.csv and sessions.csv from zip")


def _collect_from_db() -> None:
    import psycopg

    print("Connecting to database...")
    db_host = os.environ["DB_HOST"]
    db_port = os.environ["DB_PORT"]
    db_name = os.environ["DB_NAME"]
    db_user = os.environ["DB_USER"]
    db_password = os.environ["DB_PASSWORD"]

    try:
        with psycopg.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_password,
        ) as conn:
            with conn.cursor() as cur:
                # --- sensor history (data table) ---
                print("Querying data table...")
                cur.execute("""
                    SELECT *
                    FROM data
                    ORDER BY sent_at DESC
                    LIMIT 2000
                """)
                data_rows = cur.fetchall()
                data_cols = [desc[0] for desc in cur.description]

                # --- sessions table ---
                print("Querying sessions table...")
                cur.execute("""
                    SELECT *
                    FROM sessions
                    ORDER BY started_at DESC
                """)
                session_rows = cur.fetchall()
                session_cols = [desc[0] for desc in cur.description]

        REAL_SENSOR_HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)

        if not data_rows:
            print("No rows found in data table.")
        else:
            print("Saving sensor history to CSV...")
            with REAL_SENSOR_HISTORY_PATH.open(mode="w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(data_cols)
                writer.writerows(data_rows)
            print(f"Success: Saved {len(data_rows)} rows to {REAL_SENSOR_HISTORY_PATH}")

        if not session_rows:
            print("No rows found in sessions table.")
        else:
            print("Saving sessions to CSV...")
            with SESSIONS_PATH.open(mode="w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(session_cols)
                writer.writerows(session_rows)
            print(f"Success: Saved {len(session_rows)} rows to {SESSIONS_PATH}")

    except Exception as exc:
        print(f"Error during extraction: {exc}")
        raise


def collect_data():
    api_base_url = os.environ.get("MAL_API_BASE_URL")
    if api_base_url:
        _collect_from_api(api_base_url)
        return

    _collect_from_db()

if __name__ == "__main__":
    collect_data()