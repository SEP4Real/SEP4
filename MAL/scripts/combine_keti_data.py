import pandas as pd
from pathlib import Path
import os 

script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent

base_dir = project_root / 'data' / 'raw' / 'KETI'

interim_dir = project_root / 'data' / 'interim'
output_file = interim_dir / 'combined_keti_sensor_data.csv'

sensors = ['co2', 'humidity', 'light', 'pir', 'temperature']
all_rooms_data = []

print(f"Looking for data in: {base_dir}")
print("Starting data processing...")

for room_name in os.listdir(str(base_dir)):
    room_path = base_dir / room_name
    
    if room_path.is_dir():
        print(f"Processing data for room: {room_name}")
        room_df = pd.DataFrame()
        
        for sensor in sensors:
            file_path = room_path / f"{sensor}.csv"
            
            if file_path.exists():
                df = pd.read_csv(file_path, header=None, names=['timestamp', sensor])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
                df.set_index('timestamp', inplace=True)
                
                if room_df.empty:
                    room_df = df
                else:
                    room_df = room_df.join(df, how='outer')
        
        if not room_df.empty:
            room_df['room'] = room_name
            all_rooms_data.append(room_df)

print("All rooms processed. Stitching everything together into one dataset...")

final_df = pd.concat(all_rooms_data)
final_df.reset_index(inplace=True)
final_df = final_df[['timestamp', 'room', 'co2', 'humidity', 'light', 'pir', 'temperature']]

interim_dir.mkdir(parents=True, exist_ok=True)
final_df.to_csv(output_file, index=False)

print(f"Success! Data combined and saved to '{output_file}'.")