from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split

APP_DIR = Path(__file__).resolve().parent
DATASET_PATH = APP_DIR / "focus_dataset.csv"
# DATASET_PATH = APP_DIR / "focus_dataset_realdata.csv"
REAL_DATASET_PATH = APP_DIR / "environment_history_realdata.csv"
MODEL_PATH = APP_DIR / "rf_model.pkl"

FEATURE_COLUMNS = ["currentTemperature", "maxTemp", "minTemp", "meanTemp"]
TARGET_COLUMN = "rating"
RANDOM_STATE = 42


def load_dataset(path: Path = DATASET_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing_columns = [column for column in [*FEATURE_COLUMNS, TARGET_COLUMN] if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {', '.join(missing_columns)}")
    return df


def load_real_sensor_dataset(path: Path = REAL_DATASET_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    # The real data pulled from the database won't have feature aggregates or ratings yet
    return df


def split_features_target(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    return df[FEATURE_COLUMNS], df[TARGET_COLUMN]


def build_model() -> RandomForestClassifier:
    return RandomForestClassifier(random_state=RANDOM_STATE, n_estimators=100)


def train_model(df: pd.DataFrame | None = None) -> RandomForestClassifier:
    training_df = load_dataset() if df is None else df
    x, y = split_features_target(training_df)
    model = build_model()
    model.fit(x, y)
    return model


def train_validation_test_split(
    df: pd.DataFrame,
    test_size: float = 0.2,
    validation_size: float = 0.2,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.Series]:
    x, y = split_features_target(df)
    x_train_val, x_test, y_train_val, y_test = train_test_split(
        x,
        y,
        test_size=test_size,
        random_state=RANDOM_STATE,
        stratify=y,
    )
    x_train, x_validation, y_train, y_validation = train_test_split(
        x_train_val,
        y_train_val,
        test_size=validation_size,
        random_state=RANDOM_STATE,
        stratify=y_train_val,
    )
    return x_train, x_validation, x_test, y_train, y_validation, y_test


def evaluate_model(model, x: pd.DataFrame, y: pd.Series) -> dict[str, float]:
    predictions = model.predict(x)
    return {
        "accuracy": accuracy_score(y, predictions),
        "macro_f1": f1_score(y, predictions, average="macro"),
    }


def save_model(model: RandomForestClassifier, path: Path = MODEL_PATH) -> Path:
    joblib.dump(model, path)
    load_model.cache_clear()
    return path


@lru_cache(maxsize=1)
def load_model() -> RandomForestClassifier:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model artifact not found at {MODEL_PATH}. "
            "Run `python -m app.train_model` from the MAL directory first."
        )
    return joblib.load(MODEL_PATH)


def predict(
    current_temperature: float,
    max_temperature: float,
    min_temperature: float,
    mean_temperature: float,
) -> int:
    input_df = pd.DataFrame(
        [[current_temperature, max_temperature, min_temperature, mean_temperature]],
        columns=FEATURE_COLUMNS,
    )
    prediction = load_model().predict(input_df)
    return int(prediction[0])
