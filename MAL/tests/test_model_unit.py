"""
Unit tests for ml_pipeline/model.py and ml_pipeline/instant_model.py.

Tests follow the AAA pattern:
  Arrange - set up inputs and dependencies
  Act     - call the function under test
  Assert  - verify the result

Naming convention: <what_is_tested>_<scenario>_<expected_outcome>
"""
import pytest
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from ml_pipeline.model import (
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    build_model,
    evaluate_model,
    load_dataset,
    load_model,
    predict,
    save_model,
    split_features_target,
    train_model,
)
from ml_pipeline.instant_model import (
    INSTANT_FEATURE_COLUMNS,
    load_instant_model,
    load_instant_scaler,
    predict_instant,
)

_MOCK_DF = pd.DataFrame(
    {
        "currentTemperature": [20.0, 22.0, 24.0, 26.0, 28.0, 30.0],
        "maxTemp": [25.0, 25.0, 27.0, 29.0, 30.0, 32.0],
        "minTemp": [18.0, 20.0, 22.0, 24.0, 26.0, 28.0],
        "meanTemp": [21.0, 22.5, 24.0, 26.0, 27.5, 29.5],
        "rating": [3, 4, 4, 3, 2, 2],
    }
)


def test_build_model_default_returns_random_forest_classifier():
    # Arrange - nothing required
    # Act
    model = build_model()
    # Assert
    assert isinstance(model, RandomForestClassifier)


def test_build_model_uses_fixed_random_state():
    # Arrange - nothing required
    # Act
    model = build_model()
    # Assert
    assert model.random_state == 42


def test_split_features_target_features_match_configured_columns():
    # Arrange
    df = _MOCK_DF.copy()
    # Act
    x, _ = split_features_target(df)
    # Assert
    assert list(x.columns) == FEATURE_COLUMNS


def test_split_features_target_target_matches_configured_column():
    # Arrange
    df = _MOCK_DF.copy()
    # Act
    _, y = split_features_target(df)
    # Assert
    assert y.name == TARGET_COLUMN


def test_train_model_with_dataframe_returns_fitted_classifier():
    # Arrange
    df = _MOCK_DF.copy()
    # Act
    model = train_model(df=df)
    # Assert
    assert isinstance(model, RandomForestClassifier)
    assert hasattr(model, "estimators_")


def test_evaluate_model_returns_accuracy_and_macro_f1():
    # Arrange
    model = train_model(df=_MOCK_DF)
    x, y = split_features_target(_MOCK_DF)
    # Act
    metrics = evaluate_model(model, x, y)
    # Assert
    assert "accuracy" in metrics
    assert "macro_f1" in metrics
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["macro_f1"] <= 1.0


def test_save_model_creates_file_at_given_path(tmp_path):
    # Arrange
    model = train_model(df=_MOCK_DF)
    output_path = tmp_path / "test_model.pkl"
    # Act
    returned_path = save_model(model, path=output_path)
    # Assert
    assert output_path.exists()
    assert returned_path == output_path


def test_load_model_raises_when_file_is_missing(tmp_path):
    # Arrange - temporarily point MODEL_PATH at a nonexistent file
    import ml_pipeline.model as model_module

    original_path = model_module.MODEL_PATH
    model_module.MODEL_PATH = tmp_path / "nonexistent.pkl"
    model_module.load_model.cache_clear()
    # Act & Assert
    try:
        with pytest.raises(FileNotFoundError):
            model_module.load_model()
    finally:
        model_module.MODEL_PATH = original_path
        model_module.load_model.cache_clear()


def test_load_instant_model_raises_when_file_is_missing(tmp_path):
    import ml_pipeline.instant_model as instant_model_module

    original_path = instant_model_module.INSTANT_MODEL_PATH
    instant_model_module.INSTANT_MODEL_PATH = tmp_path / "nonexistent_instant.pkl"
    instant_model_module.load_instant_model.cache_clear()
    try:
        with pytest.raises(FileNotFoundError):
            instant_model_module.load_instant_model()
    finally:
        instant_model_module.INSTANT_MODEL_PATH = original_path
        instant_model_module.load_instant_model.cache_clear()


def test_load_instant_scaler_raises_when_file_is_missing(tmp_path):
    import ml_pipeline.instant_model as instant_model_module

    original_path = instant_model_module.INSTANT_SCALER_PATH
    instant_model_module.INSTANT_SCALER_PATH = tmp_path / "nonexistent_instant_scaler.pkl"
    instant_model_module.load_instant_scaler.cache_clear()
    try:
        with pytest.raises(FileNotFoundError):
            instant_model_module.load_instant_scaler()
    finally:
        instant_model_module.INSTANT_SCALER_PATH = original_path
        instant_model_module.load_instant_scaler.cache_clear()


def test_predict_with_valid_input_returns_integer_in_rating_range():
    # Arrange - the committed rf_model.pkl is loaded automatically
    load_model.cache_clear()
    # Act
    result = predict(22.0, 25.0, 20.0, 22.5)
    # Assert
    assert isinstance(result, int)
    assert 1 <= result <= 5


def test_predict_instant_returns_integer_in_rating_range():
    load_instant_model.cache_clear()
    load_instant_scaler.cache_clear()

    result = predict_instant(
        humidity=40.0,
        light=300.0,
        temperature=22.0,
        noise=29.0,
        co2=600.0,
    )

    assert isinstance(result, int)
    assert 1 <= result <= 5


def test_predict_instant_applies_scaler_before_model_prediction(monkeypatch):
    import ml_pipeline.instant_model as instant_model_module

    class DummyScaler:
        def __init__(self):
            self.received = None

        def transform(self, input_df):
            self.received = input_df.copy()
            return [[-1.0, -2.0, -3.0, -4.0, -5.0]]

    class DummyModel:
        def __init__(self):
            self.received = None

        def predict(self, scaled_input):
            self.received = scaled_input
            return [4]

    scaler = DummyScaler()
    model = DummyModel()

    monkeypatch.setattr(instant_model_module, "load_instant_scaler", lambda: scaler)
    monkeypatch.setattr(instant_model_module, "load_instant_model", lambda: model)

    result = predict_instant(
        humidity=40.0,
        light=300.0,
        temperature=22.0,
        noise=29.0,
        co2=600.0,
    )

    assert result == 4
    assert list(scaler.received.columns) == INSTANT_FEATURE_COLUMNS
    assert scaler.received.iloc[0].to_dict() == {
        "humidity": 40.0,
        "light": 300.0,
        "temperature": 22.0,
        "noise": 29.0,
        "co2": 600.0,
    }
    assert model.received == [[-1.0, -2.0, -3.0, -4.0, -5.0]]


def test_load_dataset_raises_when_required_columns_are_missing(tmp_path):
    # Arrange
    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text("col1,col2\n1,2\n")
    # Act & Assert
    with pytest.raises(ValueError, match="missing required columns"):
        load_dataset(path=bad_csv)


def test_load_dataset_returns_dataframe_with_all_required_columns(tmp_path):
    # Arrange
    good_csv = tmp_path / "dataset.csv"
    header = ",".join(FEATURE_COLUMNS + [TARGET_COLUMN])
    row = ",".join(["1.0"] * len(FEATURE_COLUMNS) + ["3"])
    good_csv.write_text(f"{header}\n{row}\n")
    # Act
    df = load_dataset(path=good_csv)
    # Assert
    for col in FEATURE_COLUMNS + [TARGET_COLUMN]:
        assert col in df.columns


def test_load_real_sensor_dataset_returns_dataframe_from_csv(tmp_path):
    # Arrange
    from ml_pipeline.model import load_real_sensor_dataset

    csv_path = tmp_path / "sensor_history.csv"
    csv_path.write_text("sent_at,temperature\n2026-01-01,22.0\n2026-01-02,23.5\n")
    # Act
    df = load_real_sensor_dataset(path=csv_path)
    # Assert
    assert isinstance(df, pd.DataFrame)
    assert "temperature" in df.columns
    assert len(df) == 2


def test_train_validation_test_split_produces_three_non_overlapping_sets():
    # Arrange - 15 samples with 3 classes (5 each) so stratification works
    df = pd.DataFrame(
        {
            "currentTemperature": [20.0, 21.0, 22.0, 23.0, 24.0] * 3,
            "maxTemp": [25.0] * 15,
            "minTemp": [18.0] * 15,
            "meanTemp": [21.5] * 15,
            "rating": [2] * 5 + [3] * 5 + [4] * 5,
        }
    )
    from ml_pipeline.model import train_validation_test_split

    # Act
    x_train, x_val, x_test, y_train, y_val, y_test = train_validation_test_split(df)
    # Assert
    total = len(x_train) + len(x_val) + len(x_test)
    assert total == len(df)
    assert len(x_train) > 0
    assert len(x_val) > 0
    assert len(x_test) > 0
