from functools import lru_cache
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier

DATASET_PATH = Path(__file__).with_name("focus_dataset.csv")
FEATURE_COLUMNS = ["currentNoise", "maxNoise", "minNoise", "meanNoise"]


@lru_cache(maxsize=1)
def get_model() -> RandomForestClassifier:
    df = pd.read_csv(DATASET_PATH)
    model = RandomForestClassifier(random_state=42, n_estimators=100)
    model.fit(df[FEATURE_COLUMNS], df["rating"])
    return model


def predict(current_noise: float, max_noise: float, min_noise: float, mean_noise: float) -> int:
    input_df = pd.DataFrame(
        [[current_noise, max_noise, min_noise, mean_noise]],
        columns=FEATURE_COLUMNS,
    )
    prediction = get_model().predict(input_df)
    return int(prediction[0])
