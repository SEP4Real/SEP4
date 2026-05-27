from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from ml_pipeline.model import FEATURE_COLUMNS, TARGET_COLUMN


def load_and_preprocess_data(test_size=0.2, random_state=42):
    """
    Loads linearized_session_windows.csv, drops rows with missing ratings,
    extracts the production model features, splits into train and test sets,
    and scales the features using StandardScaler.
    
    Returns:
        X_train_scaled (pd.DataFrame): Scaled training features.
        X_test_scaled (pd.DataFrame): Scaled test features.
        y_train (pd.Series): Training target.
        y_test (pd.Series): Test target.
        scaler (StandardScaler): Fitted StandardScaler.
    """
    # Locate dataset path relative to this script
    script_dir = Path(__file__).resolve().parent
    dataset_path = script_dir.parent / "data" / "processed" / "linearized_session_windows.csv"
    
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found at {dataset_path}")
        
    df = pd.read_csv(dataset_path)

    feature_cols = list(FEATURE_COLUMNS)
    target_col = TARGET_COLUMN

    missing_columns = [
        column
        for column in [*feature_cols, target_col]
        if column not in df.columns
    ]
    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {', '.join(missing_columns)}")

    df = df.dropna(subset=[target_col])
    
    y = df[target_col]
    X = df[feature_cols]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Convert back to DataFrame to preserve column names
    X_train_scaled_df = pd.DataFrame(X_train_scaled, columns=feature_cols, index=X_train.index)
    X_test_scaled_df = pd.DataFrame(X_test_scaled, columns=feature_cols, index=X_test.index)
    
    return X_train_scaled_df, X_test_scaled_df, y_train, y_test, scaler
