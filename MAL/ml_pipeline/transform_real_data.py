import pandas as pd

from ml_pipeline.model import REAL_FOCUS_DATASET_PATH, REAL_SENSOR_HISTORY_PATH

REAL_HISTORY_FILE = REAL_SENSOR_HISTORY_PATH
OUTPUT_FILE = REAL_FOCUS_DATASET_PATH
DEFAULT_NOISE_DB = 29.0


def _noise_feature_values(session_data: pd.DataFrame) -> pd.Series:
    if "noise" in session_data.columns:
        raw_noise = pd.to_numeric(session_data["noise"], errors="coerce")
        raw_noise = raw_noise.fillna(DEFAULT_NOISE_DB).clip(lower=0)
    else:
        raw_noise = pd.Series(DEFAULT_NOISE_DB, index=session_data.index, dtype="float64")

    return raw_noise.pow(0.5).round(2)

def transform_real_data(input_file=REAL_HISTORY_FILE, output_file=OUTPUT_FILE):
    if not input_file.exists():
        print(f"Error: {input_file} not found. Hit the /collect-data endpoint first to generate it.")
        return

    # Load csv file
    df = pd.read_csv(input_file)

    # Convert timestamps to datetime
    df["sent_at"] = pd.to_datetime(df["sent_at"])

    # Sort by session and then by time so we can reliably get chronological sequences
    df = df.sort_values(["session_id", "sent_at"]).reset_index(drop=True)

    rows = []

    # Group by session_id to extract features mapped to individual study sessions
    for session_id, session_data in df.groupby("session_id"):
        if session_data.empty:
            continue

        noise_values = _noise_feature_values(session_data)

        # Extract features for the session
        row = {
            "session_id": session_id,

            # Required model features
            "currentTemperature": session_data["temperature"].iloc[-1], # Using the final recorded temperature in the session
            "maxTemp": session_data["temperature"].max(),
            "minTemp": session_data["temperature"].min(),
            "meanTemp": round(session_data["temperature"].mean(), 2),

            # Available auxiliary features (can be added to model later)
            "currentHumidity": session_data["humidity"].iloc[-1],
            "maxHumidity": session_data["humidity"].max(),
            "minHumidity": session_data["humidity"].min(),
            "meanHumidity": round(session_data["humidity"].mean(), 2),

            "currentCO2": session_data["co2_level"].iloc[-1],
            "maxCO2": session_data["co2_level"].max(),
            "minCO2": session_data["co2_level"].min(),
            "meanCO2": round(session_data["co2_level"].mean(), 2),

            "currentLight": session_data["light_level"].iloc[-1],
            "maxLight": session_data["light_level"].max(),
            "minLight": session_data["light_level"].min(),
            "meanLight": round(session_data["light_level"].mean(), 2),

            "humidity_latest": session_data["humidity"].iloc[-1],
            "humidity_mean": round(session_data["humidity"].mean(), 2),
            "humidity_min": session_data["humidity"].min(),
            "humidity_max": session_data["humidity"].max(),

            "co2_latest": session_data["co2_level"].iloc[-1],
            "co2_mean": round(session_data["co2_level"].mean(), 2),
            "co2_min": session_data["co2_level"].min(),
            "co2_max": session_data["co2_level"].max(),

            "light_latest": session_data["light_level"].iloc[-1],
            "light_mean": round(session_data["light_level"].mean(), 2),
            "light_min": session_data["light_level"].min(),
            "light_max": session_data["light_level"].max(),

            "noise_latest": noise_values.iloc[-1],
            "noise_mean": round(noise_values.mean(), 2),
            "noise_min": noise_values.min(),
            "noise_max": noise_values.max(),

            "currentNoise": noise_values.iloc[-1],
            "maxNoise": noise_values.max(),
            "minNoise": noise_values.min(),
            "meanNoise": round(noise_values.mean(), 2),

            # Placeholder until imported rating data is merged with sensor aggregates.
            "rating": None
        }

        rows.append(row)

    dataset = pd.DataFrame(rows)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(output_file, index=False)

    print(f"Created {len(dataset)} session rows in '{output_file}'.")
    print("Preview of the data:")
    print(dataset[["session_id", "currentTemperature", "maxTemp", "minTemp", "meanTemp", "rating"]].head())


if __name__ == "__main__":
    transform_real_data()
