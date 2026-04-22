from pathlib import Path
import pandas as pd

# How many minutes of sensor history to use for each rating
WINDOW_MINUTES = 30

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "generated_files"
DATA_DIR.mkdir(exist_ok=True)

# Input files from mockdata.py
HISTORY_FILE = DATA_DIR / "environment_history.csv"
RATINGS_FILE = DATA_DIR / "ratings.csv"

# Output file
OUTPUT_FILE = DATA_DIR / "focus_dataset.csv"


def build_focus_dataset(history_file=HISTORY_FILE, ratings_file=RATINGS_FILE, output_file=OUTPUT_FILE, window_minutes=WINDOW_MINUTES):
    # Load csv files
    history = pd.read_csv(history_file)
    ratings = pd.read_csv(ratings_file)

    # Convert timestamps to datetime
    history["timestamp"] = pd.to_datetime(history["timestamp"])
    ratings["timestamp"] = pd.to_datetime(ratings["timestamp"])

    # Sort just to be safe
    history = history.sort_values("timestamp").reset_index(drop=True)
    ratings = ratings.sort_values("timestamp").reset_index(drop=True)

    rows = []

    for _, rating_row in ratings.iterrows():
        rating_time = rating_row["timestamp"]
        start_time = rating_time - pd.Timedelta(minutes=window_minutes)

        # Take only sensor rows from the last X minutes before the rating
        window = history[
            (history["timestamp"] >= start_time) &
            (history["timestamp"] <= rating_time)
        ]

        # Skip if no sensor data exists in that window
        if window.empty:
            continue

        row = {
            "timePeriod": f"{start_time.strftime('%Y-%m-%d %H:%M:%S')} to {rating_time.strftime('%Y-%m-%d %H:%M:%S')}",

            "currentTemperature": window["temperature"].iloc[-1],
            "currentHumidity": window["humidity"].iloc[-1],
            "currentCO2": window["co2Level"].iloc[-1],
            "currentLight": window["lightLevel"].iloc[-1],
            "currentNoise": window["noiseLevel"].iloc[-1],

            "maxTemp": window["temperature"].max(),
            "minTemp": window["temperature"].min(),
            "meanTemp": round(window["temperature"].mean(), 2),

            "maxHumidity": window["humidity"].max(),
            "minHumidity": window["humidity"].min(),
            "meanHumidity": round(window["humidity"].mean(), 2),

            "maxCO2": window["co2Level"].max(),
            "minCO2": window["co2Level"].min(),
            "meanCO2": round(window["co2Level"].mean(), 2),

            "maxLight": window["lightLevel"].max(),
            "minLight": window["lightLevel"].min(),
            "meanLight": round(window["lightLevel"].mean(), 2),

            "maxNoise": window["noiseLevel"].max(),
            "minNoise": window["noiseLevel"].min(),
            "meanNoise": round(window["noiseLevel"].mean(), 2),

            "rating": rating_row["rating"]
        }

        rows.append(row)

    dataset = pd.DataFrame(rows)
    dataset.to_csv(output_file, index=False)

    print(f"Created {len(dataset)} rows in '{output_file}'")
    print(dataset.head())


if __name__ == "__main__":
    build_focus_dataset()
