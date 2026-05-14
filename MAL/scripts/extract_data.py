import os
import csv
import psycopg
from pathlib import Path

REAL_SENSOR_HISTORY_PATH = Path("data/sensor_history.csv")

def collect_data():
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
        # Ensure the directory exists
        REAL_SENSOR_HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        with REAL_SENSOR_HISTORY_PATH.open(mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(colnames)
            writer.writerows(rows)

        print(f"Success: Saved {len(rows)} rows to {REAL_SENSOR_HISTORY_PATH}")

    except Exception as exc:
        print(f"Error during extraction: {exc}")
        raise

if __name__ == "__main__":
    collect_data()