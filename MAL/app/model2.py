from functools import lru_cache
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split


BASE_DIR = Path(__file__).resolve().parent
DATASET_FILE = BASE_DIR / "generated_files" / "focus_dataset.csv"

FEATURE_COLUMNS = [
    "currentTemperature",
    "currentHumidity",
    "currentCO2",
    "currentLight",
    "currentNoise",
    "maxTemp",
    "minTemp",
    "meanTemp",
    "maxHumidity",
    "minHumidity",
    "meanHumidity",
    "maxCO2",
    "minCO2",
    "meanCO2",
    "maxLight",
    "minLight",
    "meanLight",
    "maxNoise",
    "minNoise",
    "meanNoise",
]


def _load_training_data(dataset_file: Path = DATASET_FILE) -> tuple[pd.DataFrame, pd.Series]:
    if not dataset_file.exists():
        raise FileNotFoundError(
            f"Training dataset not found at {dataset_file}. "
            "Run mockdata.py and transform_mockdata.py first."
        )

    dataset = pd.read_csv(dataset_file)
    missing_columns = [column for column in [*FEATURE_COLUMNS, "rating"] if column not in dataset.columns]
    if missing_columns:
        raise ValueError(f"Training dataset is missing columns: {', '.join(missing_columns)}")

    return dataset[FEATURE_COLUMNS], dataset["rating"]


def train_focus_model(dataset_file: Path = DATASET_FILE) -> tuple[RandomForestClassifier, dict[str, float]]:
    x, y = _load_training_data(dataset_file)
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(x_train, y_train)

    predictions = model.predict(x_test)
    metrics = {"accuracy": round(accuracy_score(y_test, predictions), 4)}
    return model, metrics


@lru_cache(maxsize=1)
def get_focus_model() -> RandomForestClassifier:
    model, _ = train_focus_model()
    return model


def build_feature_row(
    temperature: float,
    humidity: float,
    co2_level: float,
    light_level: float,
    noise_level: float,
) -> pd.DataFrame:
    values = {
        "currentTemperature": temperature,
        "currentHumidity": humidity,
        "currentCO2": co2_level,
        "currentLight": light_level,
        "currentNoise": noise_level,
        "maxTemp": temperature,
        "minTemp": temperature,
        "meanTemp": temperature,
        "maxHumidity": humidity,
        "minHumidity": humidity,
        "meanHumidity": humidity,
        "maxCO2": co2_level,
        "minCO2": co2_level,
        "meanCO2": co2_level,
        "maxLight": light_level,
        "minLight": light_level,
        "meanLight": light_level,
        "maxNoise": noise_level,
        "minNoise": noise_level,
        "meanNoise": noise_level,
    }
    return pd.DataFrame([values], columns=FEATURE_COLUMNS)


def predict_focus_level(
    temperature: float,
    humidity: float,
    co2_level: float,
    light_level: float,
    noise_level: float,
) -> int:
    feature_row = build_feature_row(temperature, humidity, co2_level, light_level, noise_level)
    prediction = get_focus_model().predict(feature_row)[0]
    return int(prediction)


def suggestion_for_focus_level(focus_level: int) -> str:
    if focus_level >= 4:
        return "Study conditions look suitable."
    if focus_level == 3:
        return "Study conditions are acceptable, but check noise, CO2, light, and temperature."
    return "Study conditions may reduce focus. Improve ventilation, noise, lighting, or temperature."


if __name__ == "__main__":
    _, training_metrics = train_focus_model()
    print(f"Trained RandomForest focus model with test accuracy: {training_metrics['accuracy']:.4f}")