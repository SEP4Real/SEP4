from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV

MAL_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = MAL_DIR / "data"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = MAL_DIR / "models"

INSTANT_DATASET_PATH = PROCESSED_DATA_DIR / "instant_mock_clean.csv"
INSTANT_MODEL_PATH = MODELS_DIR / "instantrfcmodel.pkl"

INSTANT_FEATURE_COLUMNS = ["humidity", "light", "temperature", "noise", "co2"]
INSTANT_TARGET_COLUMN = "comfortValue"
RANDOM_STATE = 42


def load_instant_dataset(path: Path = INSTANT_DATASET_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing_columns = [
        column
        for column in [*INSTANT_FEATURE_COLUMNS, INSTANT_TARGET_COLUMN]
        if column not in df.columns
    ]
    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {', '.join(missing_columns)}")

    df = df[INSTANT_FEATURE_COLUMNS + [INSTANT_TARGET_COLUMN]].dropna()
    if pd.api.types.is_numeric_dtype(df[INSTANT_TARGET_COLUMN]):
        df[INSTANT_TARGET_COLUMN] = df[INSTANT_TARGET_COLUMN].round().astype(int)
    return df


def train_instant_model(df: pd.DataFrame | None = None) -> RandomForestClassifier:
    training_df = load_instant_dataset() if df is None else df
    x = training_df[INSTANT_FEATURE_COLUMNS]
    y = training_df[INSTANT_TARGET_COLUMN]

    param_grid = {
        "n_estimators": [100, 300],
        "max_depth": [None, 10, 20],
        "min_samples_split": [2, 5],
        "min_samples_leaf": [1, 3],
    }

    rf = RandomForestClassifier(
        random_state=RANDOM_STATE,
        n_jobs=-1,
        class_weight="balanced",
    )

    grid = GridSearchCV(
        rf,
        param_grid=param_grid,
        scoring="accuracy",
        cv=5,
        n_jobs=-1,
    )
    grid.fit(x, y)
    return grid.best_estimator_


def save_instant_model(model: RandomForestClassifier, path: Path = INSTANT_MODEL_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)
    load_instant_model.cache_clear()
    return path


@lru_cache(maxsize=1)
def load_instant_model() -> RandomForestClassifier:
    if not INSTANT_MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Instant model artifact not found at {INSTANT_MODEL_PATH}. "
            "Run `python scripts/train_instant_rfc_model.py` from the MAL directory first."
        )
    return joblib.load(INSTANT_MODEL_PATH)


def predict_instant(
    humidity: float,
    light: float,
    temperature: float,
    noise: float,
    co2: float,
) -> int:
    input_df = pd.DataFrame(
        [[humidity, light, temperature, noise, co2]],
        columns=INSTANT_FEATURE_COLUMNS,
    )
    prediction = load_instant_model().predict(input_df)
    return int(prediction[0])
