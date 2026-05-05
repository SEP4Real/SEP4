import pandas as pd

from ml_pipeline.model import REAL_FOCUS_DATASET_PATH, REAL_SENSOR_HISTORY_PATH

REAL_HISTORY_FILE = REAL_SENSOR_HISTORY_PATH
OUTPUT_FILE = REAL_FOCUS_DATASET_PATH

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
