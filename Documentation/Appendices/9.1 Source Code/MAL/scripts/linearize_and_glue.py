import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler

def linearize_and_glue(sensor_df, sessions_df):
    # 1. Filter sessions with valid study_quality
    valid_sessions = sessions_df.dropna(subset=['study_quality']).copy()
    if valid_sessions.empty:
        return pd.DataFrame()

    # 2. Filter sensor data to only match valid sessions
    sensor_df = sensor_df[sensor_df['session_id'].isin(valid_sessions['id'])].copy()
    if sensor_df.empty:
        return pd.DataFrame()

    # Sort chronologically per session
    sensor_df = sensor_df.sort_values(by=['session_id', 'sent_at'])
    
    # A. Missing Values Handling: Forward fill then backward fill per session
    cols_to_fill = ['temperature', 'humidity', 'co2_level', 'light_level']
    for col in cols_to_fill:
        if col in sensor_df.columns:
            sensor_df[col] = sensor_df.groupby('session_id')[col].ffill().bfill()
            
    # B. Outliers Handling (Clipping to physical limits)
    if 'temperature' in sensor_df.columns:
        sensor_df['temperature'] = sensor_df['temperature'].clip(lower=10, upper=40)
    if 'humidity' in sensor_df.columns:
        sensor_df['humidity'] = sensor_df['humidity'].clip(lower=0, upper=100)
    if 'co2_level' in sensor_df.columns:
        sensor_df['co2_level'] = sensor_df['co2_level'].clip(lower=400, upper=5000)
    if 'light_level' in sensor_df.columns:
        sensor_df['light_level'] = sensor_df['light_level'].clip(lower=0, upper=2000)
        
    # C. Feature Scaling using StandardScaler
    cols_to_scale = [col for col in cols_to_fill if col in sensor_df.columns]
    scaler = StandardScaler()
    sensor_df[cols_to_scale] = scaler.fit_transform(sensor_df[cols_to_scale])

    # D. Simulate and One-Hot Encode student_type (if not already done)
    # Check if student_type columns are already present to make it idempotent
    student_cols_exist = any(col.startswith('student_type_') for col in valid_sessions.columns)
    if 'student_type' not in valid_sessions.columns and not student_cols_exist:
        student_types_list = ['visual', 'auditory', 'kinesthetic', 'reading_writing']
        np.random.seed(42)
        simulated_student_types = pd.DataFrame({
            'id': valid_sessions['id'],
            'student_type': np.random.choice(student_types_list, size=len(valid_sessions))
        })
        valid_sessions = valid_sessions.merge(simulated_student_types, on='id', how='left')
        valid_sessions = pd.get_dummies(valid_sessions, columns=['student_type'], prefix='student_type', drop_first=False)
    
    # 3. Core aggregation grouping by session_id
    features = ['temperature', 'humidity', 'co2_level', 'light_level']
    agg_funcs = ['mean', 'min', 'max', 'std', 'count', 'last']
    agg_dict = {f: agg_funcs for f in features if f in sensor_df.columns}
    
    linearized_df = sensor_df.groupby('session_id').agg(agg_dict)
    
    # Flatten multi-index columns
    linearized_df.columns = [f"{col[0]}_{col[1]}" for col in linearized_df.columns]
    linearized_df = linearized_df.reset_index()

    # Fill NaNs in standard deviations (sessions with 1 reading)
    for f in features:
        std_col = f"{f}_std"
        if std_col in linearized_df.columns:
            linearized_df[std_col] = linearized_df[std_col].fillna(0)

    # 4. Merge sensor aggregates with session records
    final_df = linearized_df.merge(
        valid_sessions, 
        left_on='session_id', 
        right_on='id', 
        how='inner'
    )
    
    # Drop raw IDs/timestamps not needed for model training
    cols_to_drop = ['id', 'device_id', 'started_at', 'is_ended', 'last_pulse_at']
    final_df = final_df.drop(columns=[col for col in cols_to_drop if col in final_df.columns])
    
    return final_df

def run_linearization_and_glue():
    MAL_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = MAL_DIR / "data" / "real"
    
    sensor_path = DATA_DIR / "sensor_history.csv"
    sessions_path = DATA_DIR / "sessions.csv"
    output_path = DATA_DIR / "linearized_sessions_with_target.csv"

    if not sensor_path.exists() or not sessions_path.exists():
        print(f"Skipping execution: inputs not found at {sensor_path} / {sessions_path}")
        return

    print("Running production linearization & preprocessing...")
    sensor_df = pd.read_csv(sensor_path, parse_dates=['sent_at'])
    sessions_df = pd.read_csv(sessions_path)

    final_df = linearize_and_glue(sensor_df, sessions_df)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    final_df.to_csv(output_path, index=False)
    print(f"Successfully saved final dataset ({len(final_df)} rows) to: {output_path}")

if __name__ == "__main__":
    run_linearization_and_glue()
