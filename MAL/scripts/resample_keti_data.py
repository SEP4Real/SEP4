import pandas as pd
from pathlib import Path

# Setup Paths dynamically
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent

input_file = project_root / 'data' / 'interim' / 'combined_keti_sensor_data.csv'
output_file = project_root / 'data' / 'interim' / 'keti_1min_resampled.csv'

print(f"Loading raw rows from: {input_file}")
print("Smoke a pipe muchacha/muchacho, this will take a few seconds...")
df = pd.read_csv(input_file)

print("Converting timestamps to datetime objects...")
df['timestamp'] = pd.to_datetime(df['timestamp'])
df.set_index('timestamp', inplace=True)

print("Binarizing PIR data and resampling...")
df['pir'] = (df['pir'] > 0).astype(int)

aggregation_rules = {
    'co2': 'mean',
    'humidity': 'mean',
    'light': 'mean',
    'temperature': 'mean',
    'pir': 'max' 
}

df_resampled = df.groupby('room').resample('1min').agg(aggregation_rules).reset_index()

print("Handling any remaining missing values...")
features = ['co2', 'humidity', 'light', 'temperature', 'pir']

# Forward-fill to carry last known values forward, then back-fill as a safety net 
df_resampled[features] = df_resampled.groupby('room')[features].ffill()
df_resampled[features] = df_resampled.groupby('room')[features].bfill()


output_file.parent.mkdir(parents=True, exist_ok=True)
print(f"Saving clean data to: {output_file}")
df_resampled.to_csv(output_file, index=False)
print(f"Success! Data dramatically reduced to {df_resampled.shape[0]} clean rows.")