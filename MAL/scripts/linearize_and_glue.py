import pandas as pd
from pathlib import Path

def linearize_and_glue(sensor_df, sessions_df):
    valid_sessions = sessions_df.dropna(subset=['study_quality']).copy()

    sensor_df = sensor_df[sensor_df['session_id'].isin(valid_sessions['id'])].copy()
    sensor_df = sensor_df.sort_values(by=['session_id', 'sent_at'])
    
    features = ['temperature', 'humidity', 'co2_level', 'light_level']
    agg_funcs = ['mean', 'min', 'max', 'std', 'count', 'last']
    agg_dict = {f: agg_funcs for f in features}
    
    linearized_df = sensor_df.groupby('session_id').agg(agg_dict)
    
    linearized_df.columns = [f"{col[0]}_{col[1]}" for col in linearized_df.columns]
    linearized_df = linearized_df.reset_index()

    for f in features:
        if f"{f}_std" in linearized_df.columns:
            linearized_df[f"{f}_std"] = linearized_df[f"{f}_std"].fillna(0)

    final_df = linearized_df.merge(
        valid_sessions, 
        left_on='session_id', 
        right_on='id', 
        how='inner'
    )
    
    cols_to_drop = ['id', 'device_id', 'started_at', 'is_ended', 'last_pulse_at']
    final_df = final_df.drop(columns=[col for col in cols_to_drop if col in final_df.columns])
    
    return final_df

def run_linearization_and_glue():
    MAL_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = MAL_DIR / "data" / "real"
    
    sensor_path = DATA_DIR / "sensor_history.csv"
    sessions_path = DATA_DIR / "sessions.csv"
    output_path = DATA_DIR / "linearized_sessions_with_target.csv"

    sensor_df = pd.read_csv(sensor_path, parse_dates=['sent_at'])
    sessions_df = pd.read_csv(sessions_path)

    final_df = linearize_and_glue(sensor_df, sessions_df)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    final_df.to_csv(output_path, index=False)

if __name__ == "__main__":
    run_linearization_and_glue()
