import csv
import os
import urllib.error
import urllib.request
from pathlib import Path

REAL_SENSOR_HISTORY_PATH = Path("data/sensor_history.csv")


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
    REAL_SENSOR_HISTORY_PATH.write_bytes(payload)
    print(f"Success: Saved data to {REAL_SENSOR_HISTORY_PATH}")


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
                print("Executing query...")
                query = """
                    SELECT *
                    FROM data
                    ORDER BY sent_at DESC
                    LIMIT 2000
                """
                cur.execute(query)
                rows = cur.fetchall()
                colnames = [desc[0] for desc in cur.description]

        if not rows:
            print("No data found in database.")
            return

        print("Saving to CSV...")
        REAL_SENSOR_HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)

        with REAL_SENSOR_HISTORY_PATH.open(mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(colnames)
            writer.writerows(rows)

        print(f"Success: Saved {len(rows)} rows to {REAL_SENSOR_HISTORY_PATH}")

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