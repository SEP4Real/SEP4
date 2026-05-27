from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def load_and_preprocess_data(test_size=0.2, random_state=42):
    """
    Loads linearized_session_windows.csv, drops rows with missing ratings,
    extracts all numeric features, splits into train and test sets,
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
    df = df.dropna(subset=["rating"])
    
    target_col = "rating"
    y = df[target_col]
    
    exclude_cols = [
        "rating", "focus_score", "segment_id", "session_id", "source", 
        "location_id", "segment_start", "segment_end"
    ]
    
    feature_cols = [
        col for col in df.columns 
        if col not in exclude_cols and pd.api.types.is_numeric_dtype(df[col])
    ]
    
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
