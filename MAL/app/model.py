from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

DATASET_PATH = Path(__file__).with_name("focus_dataset.csv")
MODEL_PATH = Path(__file__).with_name("rf_model.pkl")
FEATURE_COLUMNS = ["currentNoise", "maxNoise", "minNoise", "meanNoise"]


@lru_cache(maxsize=1)
def load_model() -> RandomForestClassifier:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model artifact not found at {MODEL_PATH}. "
            "Run `python -m app.train_model` from the MAL directory first."
        )
    return joblib.load(MODEL_PATH)


def train_model() -> RandomForestClassifier:
    df = pd.read_csv(DATASET_PATH)
    model = RandomForestClassifier(random_state=42, n_estimators=100)
    model.fit(df[FEATURE_COLUMNS], df["rating"])
    return model


def save_model(model: RandomForestClassifier, path: Path = MODEL_PATH) -> Path:
    joblib.dump(model, path)
    load_model.cache_clear()
    return path


def predict(current_noise: float, max_noise: float, min_noise: float, mean_noise: float) -> int:
    input_df = pd.DataFrame(
        [[current_noise, max_noise, min_noise, mean_noise]],
        columns=FEATURE_COLUMNS,
    )
    prediction = load_model().predict(input_df)
    return int(prediction[0])
