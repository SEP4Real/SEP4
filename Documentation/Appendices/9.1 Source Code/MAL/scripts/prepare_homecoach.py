import pandas as pd
from pathlib import Path

# Make the paths bulletproof by anchoring them to where this script lives
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent  # This gets you to the 'MAL' folder

# Define file paths using the project root
data_7_dir = project_root / 'data' / 'raw' / 'DATA_7'
output_file = project_root / 'data' / 'interim' / 'HomeCoach_combined.csv'

# List the raw files
hc_files = [
    'HomeCoach_5min_2023.csv',
    'HomeCoach_5min_2024.csv',
    'HomeCoach_5min_2025.csv',
    'HomeCoach_5min_2026.csv'
]

# Read and glue them together
dfs = [pd.read_csv(data_7_dir / f) for f in hc_files]
data_7_full = pd.concat(dfs, ignore_index=True)

# Parse timestamps and sort so the timeline is clean
data_7_full['timestamp'] = pd.to_datetime(data_7_full['timestamp'])
data_7_full = data_7_full.sort_values('timestamp').reset_index(drop=True)

# Add a standard 'id' column to match your other datasets
data_7_full.insert(0, 'id', 'HomeCoach')

# Save the combined dataset
output_file.parent.mkdir(parents=True, exist_ok=True)
data_7_full.to_csv(output_file, index=False)

print(f"Combined HomeCoach dataset saved to: {output_file}")
print(f"Total Rows: {len(data_7_full):,}")
print(f"Timeline: {data_7_full['timestamp'].min()} to {data_7_full['timestamp'].max()}")