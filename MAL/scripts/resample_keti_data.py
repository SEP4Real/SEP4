from pathlib import Path

import pandas as pd

script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent

raw_dir = project_root / 'data' / 'raw' / 'data_3' / 'KETI'
output_file = project_root / 'data' / 'interim' / 'keti_1min_resampled.csv'
quality_report_file = project_root / 'data' / 'interim' / 'keti_1min_quality_report.csv'

CONTINUOUS_SENSORS = ['co2', 'humidity', 'light', 'temperature']
SENSORS = CONTINUOUS_SENSORS + ['pir']

# Conservative physical bounds for indoor sensor readings. Values outside these
# ranges are treated as sensor glitches and excluded before minute aggregation.
VALID_RANGES = {
    'co2': (250, 2000),
    'humidity': (0, 100),
    'light': (0, 5000),
    'temperature': (0, 50),
}


def load_sensor(room_path: Path, sensor: str) -> pd.DataFrame:
    df = pd.read_csv(
        room_path / f'{sensor}.csv',
        header=None,
        names=['timestamp', sensor],
        skipinitialspace=True,
    )
    df['timestamp'] = pd.to_datetime(df['timestamp'].astype('int64'), unit='s')
    df[sensor] = pd.to_numeric(df[sensor], errors='coerce')

    if sensor == 'pir':
        df[sensor] = (df[sensor] > 0).astype('Int64')
        return df

    low, high = VALID_RANGES[sensor]
    df.loc[~df[sensor].between(low, high), sensor] = pd.NA
    return df


def resample_sensor(df: pd.DataFrame, sensor: str) -> pd.DataFrame:
    resampler = df.set_index('timestamp')[sensor].resample('1min')

    if sensor == 'pir':
        values = resampler.max()
    else:
        values = resampler.mean()

    counts = resampler.count().rename(f'{sensor}_observations')
    values = values.rename(sensor)
    return pd.concat([values, counts], axis=1)


all_rooms = []
quality_rows = []

print(f'Resampling KETI data from: {raw_dir}')

for room_path in sorted(raw_dir.iterdir(), key=lambda path: path.name):
    if not room_path.is_dir():
        continue

    room = room_path.name
    print(f'Processing room {room}')
    room_parts = []

    for sensor in SENSORS:
        sensor_file = room_path / f'{sensor}.csv'
        if not sensor_file.exists():
            quality_rows.append({
                'room': room,
                'sensor': sensor,
                'raw_rows': 0,
                'valid_rows': 0,
                'invalid_rows': 0,
                'first_timestamp': pd.NaT,
                'last_timestamp': pd.NaT,
            })
            continue

        sensor_df = load_sensor(room_path, sensor)
        valid_rows = int(sensor_df[sensor].notna().sum())
        quality_rows.append({
            'room': room,
            'sensor': sensor,
            'raw_rows': len(sensor_df),
            'valid_rows': valid_rows,
            'invalid_rows': len(sensor_df) - valid_rows,
            'first_timestamp': sensor_df['timestamp'].min(),
            'last_timestamp': sensor_df['timestamp'].max(),
        })
        room_parts.append(resample_sensor(sensor_df, sensor))

    if not room_parts:
        continue

    room_df = pd.concat(room_parts, axis=1, sort=True).reset_index()
    room_df.insert(0, 'room', room)
    all_rooms.append(room_df)

if not all_rooms:
    raise RuntimeError(f'No room data found in {raw_dir}')

final_df = pd.concat(all_rooms, ignore_index=True)
observation_columns = [f'{sensor}_observations' for sensor in SENSORS]
final_df[observation_columns] = final_df[observation_columns].fillna(0).astype('int64')
final_df = final_df[
    ['room', 'timestamp']
    + SENSORS
    + observation_columns
]

output_file.parent.mkdir(parents=True, exist_ok=True)
final_df.to_csv(output_file, index=False)
pd.DataFrame(quality_rows).to_csv(quality_report_file, index=False)

print(f'Saved trustworthy 1-minute data to: {output_file}')
print(f'Saved quality report to: {quality_report_file}')
print(f'Rows: {final_df.shape[0]:,}; rooms: {final_df["room"].nunique()}')
print('Missing values are preserved. Use observation-count columns to filter coverage before modeling.')
