import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.ensemble import ExtraTreesRegressor

def clean_and_impute_dataset():
    MAL_DIR = Path(__file__).resolve().parent.parent
    data_path = MAL_DIR / "data" / "processed" / "unified_environment_focus_dataset.csv"
    output_path = MAL_DIR / "data" / "processed" / "final_mock_dataset.csv"
    
    if not data_path.exists():
        raise FileNotFoundError(f"Missing input unified dataset at {data_path}")
        
    print("Loading unified dataset...")
    df = pd.read_csv(data_path, parse_dates=["timestamp"], low_memory=False)
    print(f"Total Rows: {len(df):,}")
    print(f"Labeled focus_score count in input: {df['focus_score'].notna().sum():,}")

    # Remove rows where either co2, temperature, or humidity are missing
    print("Filtering rows with missing Temp/Humidity/CO2...")
    df = df.dropna(subset=['co2', 'temperature', 'humidity'])
    print(f"Filtered Rows: {len(df):,}")

    # Clustering setup
    combined_df = df.copy()
    anchors = ['temperature', 'humidity', 'co2']
    scaled_data = StandardScaler().fit_transform(combined_df[anchors])

    # Assign room type clusters (K=4)
    print("Assigning environment clusters...")
    model_kmeans = KMeans(n_clusters=4, random_state=42)
    combined_df['room_type'] = model_kmeans.fit_predict(scaled_data)

    # Imputation setup using ExtraTrees uncertainty forest wrapper
    class SmartForest(ExtraTreesRegressor):
        def predict(self, X, return_std=False):
            if not return_std:
                return super().predict(X)
            all_preds = np.stack([t.predict(X) for t in self.estimators_])
            return np.mean(all_preds, axis=0), np.std(all_preds, axis=0)

    impute_cols = ['co2', 'noise', 'temperature', 'light', 'humidity']
    imputed_chunks = []

    for room_id in sorted(combined_df['room_type'].unique()):
        print(f"Processing Cluster {room_id} MICE Imputation...")
        chunk = combined_df[combined_df['room_type'] == room_id].copy()
        original_backup = chunk.copy()

        mice = IterativeImputer(
            estimator=SmartForest(
                n_estimators=20,
                max_depth=15,
                min_samples_leaf=5,
                random_state=42
            ),
            sample_posterior=True,
            n_nearest_features=5,
            random_state=42
        )

        numbers_only = [col for col in impute_cols if col in chunk.columns]
        active_cols = [col for col in numbers_only if chunk[col].notna().any()]

        filled_data = mice.fit_transform(chunk[active_cols])
        temp_df = pd.DataFrame(filled_data, columns=active_cols, index=chunk.index)

        # Physical boundaries
        if 'light' in temp_df.columns:
            temp_df['light'] = temp_df['light'].clip(lower=0)
        if 'noise' in temp_df.columns:
            temp_df['noise'] = temp_df['noise'].clip(lower=0)

        # Restore original Temp, Humidity, CO2 (only impute Light and Noise)
        for col in active_cols:
            if col in ['temperature', 'humidity', 'co2']:
                temp_df[col] = original_backup[col].values

        # Re-add non-imputed columns
        for col in chunk.columns:
            if col not in temp_df.columns:
                temp_df[col] = original_backup[col].values

        imputed_chunks.append(temp_df)

    print("Concatenating imputed clusters...")
    final_df = pd.concat(imputed_chunks).sort_index()

    # Safety fill with global median
    final_df['light'] = final_df['light'].fillna(combined_df['light'].median())
    final_df['noise'] = final_df['noise'].fillna(combined_df['noise'].median())

    # Applying column transformations
    print("Applying column transformations...")
    final_df['co2'] = 1.0 / final_df['co2']
    final_df['light'] = np.log1p(final_df['light'])
    final_df['noise'] = np.sqrt(final_df['noise'])
    final_df['humidity'] = final_df['humidity']**2

    final_cols = [
        'timestamp',
        'session_id',
        'location_id',
        'record_id',
        'source',
        'humidity',
        'light',
        'temperature',
        'noise',
        'co2',
        'focus_score'
    ]
    final_df = final_df[final_cols]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Exporting cleaned mega-dataset to CSV...")
    print(f"Final Row Count: {len(final_df):,}")
    print(f"Non-null focus_score labels count in output: {final_df['focus_score'].notna().sum():,}")
    
    final_df.to_csv(output_path, index=False)
    print(f"Successfully saved to: {output_path}")

if __name__ == '__main__':
    clean_and_impute_dataset()
