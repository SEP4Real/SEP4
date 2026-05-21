from __future__ import annotations

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.ensemble import ExtraTreesRegressor

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

try:
    from MAL.notebooks.archive.scripts_related_archive.build_unified_environment_dataset import (
        DEFAULT_OUTPUT_PATH as DEFAULT_UNIFIED_DATASET_PATH,
        DEFAULT_REPORT_PATH as DEFAULT_UNIFIED_REPORT_PATH,
        build_unified_dataset,
    )
except ImportError:
    from MAL.notebooks.archive.scripts_related_archive.build_unified_environment_dataset import (
        DEFAULT_OUTPUT_PATH as DEFAULT_UNIFIED_DATASET_PATH,
        DEFAULT_REPORT_PATH as DEFAULT_UNIFIED_REPORT_PATH,
        build_unified_dataset,
    )


MAL_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = MAL_DIR / "data"

DEFAULT_OUTPUT_PATH = DATA_DIR / "processed" / "unified_environment_focus_dataset_filled.csv"
DEFAULT_STUDENT_TARGET_OUTPUT_PATH = (
    DATA_DIR / "processed" / "unified_environment_student_target_filled.csv"
)
DEFAULT_RESPONDENT_TARGET_OUTPUT_PATH = (
    DATA_DIR / "processed" / "unified_environment_respondent_focus_score_filled.csv"
)
DEFAULT_STUDENT_TRAINING_PATH = DATA_DIR / "raw" / "DATA_2" / "agile_teaching_dataset.csv"
DEFAULT_ROOM_MEASUREMENTS_PATH = DATA_DIR / "raw" / "DATA_8" / "smart-campus-comfort-data" / "1_room_measurements.csv"
DEFAULT_COMFORT_PERCEPTION_PATH = DATA_DIR / "raw" / "DATA_8" / "smart-campus-comfort-data" / "4_comfort_perception.csv"
DEFAULT_RESPONDENT_TRAINING_OUTPUT_PATH = (
    DATA_DIR / "processed" / "respondent_comfort_training_dataset.csv"
)
DEFAULT_FEATURE_COLUMNS = ["humidity", "light", "temperature", "noise", "co2"]
DEFAULT_STUDENT_FEATURE_COLUMNS = ["humidity", "light", "temperature", "noise"]
DEFAULT_RESPONDENT_FEATURE_COLUMNS = ["humidity", "temperature", "noise", "co2"]
DEFAULT_TARGET_COLUMN = "focus_score"
DEFAULT_STUDENT_TARGET_COLUMN = "target"
DEFAULT_RESPONDENT_TARGET_COLUMN = "focus_score"
DEFAULT_STUDENT_GROUP_COLUMN = "student_id"
DEFAULT_RESPONDENT_GROUP_COLUMN = "respondent_id"
GROUP_COLUMN_CANDIDATES = ["student_id", "location_id", "id"]
RANDOM_STATE = 42

STUDENT_TRAINING_COLUMN_RENAMES = {
    "ambient_light": "light",
    "ambient_noise": "noise",
}

RESPONDENT_TRAINING_COLUMN_RENAMES = {
    "respondentId": "respondent_id",
    "comfortValue": "focus_score",
    "CO2": "co2",
}


@dataclass(frozen=True)
class StudentModel:
    student_id: str
    model: Pipeline
    rows: int
    classes: tuple[int, ...]


def build_classifier(random_state: int) -> Pipeline:
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median", keep_empty_features=True)),
            (
                "model",
                RandomForestClassifier(
                    n_estimators=200,
                    min_samples_leaf=2,
                    class_weight="balanced",
                    random_state=random_state,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def choose_group_column(df: pd.DataFrame, requested_column: str | None) -> str:
    if requested_column:
        if requested_column not in df.columns:
            raise ValueError(f"Group column '{requested_column}' does not exist in the dataset.")
        return requested_column

    for column in GROUP_COLUMN_CANDIDATES:
        if column in df.columns:
            return column

    raise ValueError(
        "Could not find a student/group column. Expected one of: "
        + ", ".join(GROUP_COLUMN_CANDIDATES)
    )


def validate_columns(df: pd.DataFrame, feature_columns: list[str], target_column: str) -> None:
    missing = [column for column in [*feature_columns, target_column] if column not in df.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {', '.join(missing)}")


def normalise_target(values: pd.Series) -> pd.Series:
    target = pd.to_numeric(values, errors="coerce")
    target = target.where(target.between(1, 5))
    return target.round().astype("Int64")


def normalise_class_target(values: pd.Series, allowed_classes: set[int] | None = None) -> pd.Series:
    target = pd.to_numeric(values, errors="coerce").round().astype("Int64")
    if allowed_classes is not None:
        target = target.where(target.isin(allowed_classes))
    return target

# # New 
# class SmartForest(ExtraTreesRegressor):
#     def predict(self, X, return_std=False):
#         if not return_std:
#             return super().predict(X)

#         all_preds = np.stack([tree.predict(X) for tree in self.estimators_])
#         return np.mean(all_preds, axis=0), np.std(all_preds, axis=0)

# # Helper classes to fill in the missing noise and light
# def fill_missing_light_and_noise(df: pd.DataFrame) -> pd.DataFrame:
#     filled_df = df.copy()

#     # Same as in the notebook: these are used as clustering anchors,
#     # so rows missing one of them are removed first.
#     filled_df = filled_df.dropna(subset=["co2", "temperature", "humidity"]).copy()

#     anchors = ["temperature", "humidity", "co2"]
#     scaled_data = StandardScaler().fit_transform(filled_df[anchors])

#     model_kmeans = KMeans(n_clusters=4, random_state=42)
#     filled_df["room_type"] = model_kmeans.fit_predict(scaled_data)

#     impute_cols = ["co2", "noise", "temperature", "light", "humidity"]
#     imputed_chunks = []

#     for room_id in sorted(filled_df["room_type"].unique()):
#         chunk = filled_df[filled_df["room_type"] == room_id].copy()
#         original_backup = chunk.copy()

#         mice = IterativeImputer(
#             estimator=SmartForest(
#                 n_estimators=20,
#                 max_depth=15,
#                 min_samples_leaf=5,
#                 random_state=42,
#             ),
#             sample_posterior=True,
#             n_nearest_features=5,
#             random_state=42,
#         )

#         active_cols = [col for col in impute_cols if chunk[col].notna().any()]

#         imputed_values = mice.fit_transform(chunk[active_cols])
#         temp_df = pd.DataFrame(imputed_values, columns=active_cols, index=chunk.index)

#         if "light" in temp_df.columns:
#             temp_df["light"] = temp_df["light"].clip(lower=0)

#         if "noise" in temp_df.columns:
#             temp_df["noise"] = temp_df["noise"].clip(lower=0)

#         # Keep the original real values for the anchor columns.
#         for col in ["temperature", "humidity", "co2"]:
#             if col in temp_df.columns:
#                 temp_df[col] = original_backup[col].values

#         # Put back all non-imputed columns.
#         for col in chunk.columns:
#             if col not in temp_df.columns:
#                 temp_df[col] = original_backup[col].values

#         imputed_chunks.append(temp_df)

#     result_df = pd.concat(imputed_chunks).sort_index()

#     # Same fallback as the notebook for clusters where a sensor was 100% missing.
#     result_df["light"] = result_df["light"].fillna(filled_df["light"].median())
#     result_df["noise"] = result_df["noise"].fillna(filled_df["noise"].median())

#     result_df = result_df.drop(columns="room_type")
#     return result_df[df.columns]

def train_student_models(
    labeled_df: pd.DataFrame,
    feature_columns: list[str],
    target_column: str,
    group_column: str,
    random_state: int,
) -> list[StudentModel]:
    models: list[StudentModel] = []

    for index, (student_id, student_df) in enumerate(labeled_df.groupby(group_column, dropna=False)):
        y = normalise_target(student_df[target_column]).dropna()
        if y.empty:
            continue

        x = student_df.loc[y.index, feature_columns]
        model = build_classifier(random_state + index)
        model.fit(x, y.astype(int))
        models.append(
            StudentModel(
                student_id=str(student_id),
                model=model,
                rows=len(x),
                classes=tuple(int(value) for value in sorted(y.unique())),
            )
        )

    if not models:
        raise RuntimeError("No per-student models could be trained from the labeled rows.")

    return models


def train_class_models_by_student(
    training_df: pd.DataFrame,
    feature_columns: list[str],
    target_column: str,
    group_column: str,
    random_state: int,
    allowed_classes: set[int] | None = None,
) -> list[StudentModel]:
    validate_columns(training_df, feature_columns, target_column)
    if group_column not in training_df.columns:
        raise ValueError(f"Student/group column '{group_column}' does not exist in training data.")

    models: list[StudentModel] = []
    for index, (student_id, student_df) in enumerate(training_df.groupby(group_column, dropna=False)):
        y = normalise_class_target(student_df[target_column], allowed_classes=allowed_classes).dropna()
        if y.empty:
            continue

        x = student_df.loc[y.index, feature_columns]
        model = build_classifier(random_state + index)
        model.fit(x, y.astype(int))
        models.append(
            StudentModel(
                student_id=str(student_id),
                model=model,
                rows=len(x),
                classes=tuple(int(value) for value in sorted(y.unique())),
            )
        )

    if not models:
        raise RuntimeError("No per-student models could be trained from the training rows.")

    return models


def fill_missing_targets(
    df: pd.DataFrame,
    feature_columns: list[str] | None = None,
    target_column: str = DEFAULT_TARGET_COLUMN,
    group_column: str | None = None,
    random_state: int = RANDOM_STATE,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    feature_columns = feature_columns or DEFAULT_FEATURE_COLUMNS
    validate_columns(df, feature_columns, target_column)
    group_column = choose_group_column(df, group_column)

    filled_df = df.copy()
    filled_df[target_column] = normalise_target(filled_df[target_column])

    labeled_mask = filled_df[target_column].notna()
    missing_mask = filled_df[target_column].isna()
    if not labeled_mask.any():
        raise RuntimeError(f"No labeled rows found in '{target_column}'.")

    student_models = train_student_models(
        filled_df.loc[labeled_mask],
        feature_columns,
        target_column,
        group_column,
        random_state,
    )

    model_summary = pd.DataFrame(
        {
            "student_id": model.student_id,
            "training_rows": model.rows,
            "classes": ",".join(map(str, model.classes)),
        }
        for model in student_models
    )

    if missing_mask.any():
        rng = np.random.default_rng(random_state)
        missing_indexes = filled_df.index[missing_mask].to_numpy()
        chosen_model_indexes = rng.integers(0, len(student_models), size=len(missing_indexes))

        for model_index in np.unique(chosen_model_indexes):
            row_indexes = missing_indexes[chosen_model_indexes == model_index]
            model = student_models[int(model_index)].model
            predictions = model.predict(filled_df.loc[row_indexes, feature_columns])
            filled_df.loc[row_indexes, target_column] = predictions.astype(int)

    filled_df[target_column] = filled_df[target_column].astype(int)
    return filled_df, model_summary


def standardise_student_training_data(training_df: pd.DataFrame) -> pd.DataFrame:
    return training_df.rename(columns=STUDENT_TRAINING_COLUMN_RENAMES).copy()


def model_summary_frame(student_models: list[StudentModel]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "student_id": model.student_id,
            "training_rows": model.rows,
            "classes": ",".join(map(str, model.classes)),
        }
        for model in student_models
    )


def fill_targets_from_student_preferences(
    conditions_df: pd.DataFrame,
    student_training_df: pd.DataFrame,
    feature_columns: list[str] | None = None,
    target_column: str = DEFAULT_STUDENT_TARGET_COLUMN,
    group_column: str = DEFAULT_STUDENT_GROUP_COLUMN,
    random_state: int = RANDOM_STATE,
    allowed_classes: set[int] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    feature_columns = feature_columns or DEFAULT_STUDENT_FEATURE_COLUMNS
    missing_condition_features = [
        column for column in feature_columns if column not in conditions_df.columns
    ]
    if missing_condition_features:
        raise ValueError(
            "Conditions dataset is missing required feature columns: "
            + ", ".join(missing_condition_features)
        )

    training_df = standardise_student_training_data(student_training_df)
    student_models = train_class_models_by_student(
        training_df,
        feature_columns=feature_columns,
        target_column=target_column,
        group_column=group_column,
        random_state=random_state,
        allowed_classes=allowed_classes,
    )

    filled_df = conditions_df.copy()
    if target_column not in filled_df.columns:
        filled_df[target_column] = pd.NA
    else:
        filled_df[target_column] = normalise_class_target(
            filled_df[target_column],
            allowed_classes=allowed_classes,
        )

    missing_mask = filled_df[target_column].isna()
    if missing_mask.any():
        rng = np.random.default_rng(random_state)
        missing_indexes = filled_df.index[missing_mask].to_numpy()
        chosen_model_indexes = rng.integers(0, len(student_models), size=len(missing_indexes))

        for model_index in np.unique(chosen_model_indexes):
            row_indexes = missing_indexes[chosen_model_indexes == model_index]
            model = student_models[int(model_index)].model
            predictions = model.predict(filled_df.loc[row_indexes, feature_columns])
            filled_df.loc[row_indexes, target_column] = predictions.astype(int)

    filled_df[target_column] = filled_df[target_column].astype(int)
    return filled_df, model_summary_frame(student_models)


def build_respondent_comfort_training_data(
    measurements_df: pd.DataFrame,
    comfort_df: pd.DataFrame,
    match_tolerance: pd.Timedelta = pd.Timedelta("5min"),
) -> pd.DataFrame:
    measurements = measurements_df.copy()
    comfort = comfort_df.copy()

    measurements["timestamp"] = pd.to_datetime(measurements["timestamp"], utc=True)
    comfort["timestamp"] = pd.to_datetime(comfort["timestamp"], utc=True)
    comfort = comfort.rename(columns=RESPONDENT_TRAINING_COLUMN_RENAMES)
    measurements = measurements.rename(columns=RESPONDENT_TRAINING_COLUMN_RENAMES)

    merged_parts: list[pd.DataFrame] = []
    for room_name, comfort_room_df in comfort.groupby("room", sort=True):
        measurement_room_df = measurements[measurements["room"] == room_name].sort_values(
            "timestamp"
        )
        if measurement_room_df.empty:
            continue

        merged_room_df = pd.merge_asof(
            comfort_room_df.sort_values("timestamp"),
            measurement_room_df,
            on="timestamp",
            by="room",
            direction="nearest",
            tolerance=match_tolerance,
        )
        merged_parts.append(merged_room_df)

    if not merged_parts:
        raise RuntimeError("No respondent comfort rows could be matched to room measurements.")

    training_df = pd.concat(merged_parts, ignore_index=True)
    training_df = training_df.rename(columns=RESPONDENT_TRAINING_COLUMN_RENAMES)
    training_df = training_df[
        [
            "timestamp",
            "respondent_id",
            "room",
            "temperature",
            "humidity",
            "noise",
            "co2",
            "focus_score",
        ]
    ]
    return training_df.dropna(
        subset=["respondent_id", "temperature", "humidity", "noise", "co2", "focus_score"]
    ).reset_index(drop=True)


def fill_focus_scores_from_respondent_preferences(
    conditions_df: pd.DataFrame,
    respondent_training_df: pd.DataFrame,
    feature_columns: list[str] | None = None,
    random_state: int = RANDOM_STATE,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    training_df = respondent_training_df.rename(columns=RESPONDENT_TRAINING_COLUMN_RENAMES)
    return fill_targets_from_student_preferences(
        conditions_df,
        training_df,
        feature_columns=feature_columns or DEFAULT_RESPONDENT_FEATURE_COLUMNS,
        target_column=DEFAULT_RESPONDENT_TARGET_COLUMN,
        group_column=DEFAULT_RESPONDENT_GROUP_COLUMN,
        random_state=random_state,
        allowed_classes={1, 2, 3, 4, 5},
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Fill missing target labels by training one model per student/location on labeled rows "
            "and randomly selecting among those models for unlabeled rows."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_UNIFIED_DATASET_PATH,
        help=f"Input CSV. Defaults to {DEFAULT_UNIFIED_DATASET_PATH}",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help=f"Filled CSV path. Defaults to {DEFAULT_OUTPUT_PATH}",
    )
    parser.add_argument(
        "--target-column",
        default=DEFAULT_TARGET_COLUMN,
        help=f"Target column to fill. Defaults to {DEFAULT_TARGET_COLUMN}",
    )
    parser.add_argument(
        "--group-column",
        default=None,
        help="Student/group column. Defaults to student_id, then location_id, then id.",
    )
    parser.add_argument(
        "--feature-columns",
        nargs="+",
        default=DEFAULT_FEATURE_COLUMNS,
        help="Numeric feature columns used by each per-student model.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=RANDOM_STATE,
        help=f"Random seed for model selection. Defaults to {RANDOM_STATE}",
    )
    parser.add_argument(
        "--build-input",
        action="store_true",
        help="Build the unified dataset first using scripts/build_unified_environment_dataset.py.",
    )
    parser.add_argument(
        "--student-training-input",
        type=Path,
        default=None,
        help=(
            "Optional student preference training CSV. When set, train one model per student "
            "from this file and fill the input dataset's target column from those models."
        ),
    )
    parser.add_argument(
        "--student-mode",
        action="store_true",
        help=(
            "Use data/raw/agile_teaching_dataset.csv to train per-student target models and "
            "write target predictions to the unified environmental dataset."
        ),
    )
    parser.add_argument(
        "--respondent-comfort-mode",
        action="store_true",
        help=(
            "Use respondentId + comfortValue from data/raw/4_comfort_perception.csv joined "
            "to room measurements to train per-respondent 1-5 focus_score models."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.build_input or not args.input.exists():
        build_unified_dataset(
            output_path=args.input,
            report_path=DEFAULT_UNIFIED_REPORT_PATH,
            allow_missing=False,
        )

    df = pd.read_csv(args.input, low_memory=False)
    # df = fill_missing_light_and_noise(df) new

    if args.respondent_comfort_mode:
        measurements_df = pd.read_csv(DEFAULT_ROOM_MEASUREMENTS_PATH, low_memory=False)
        comfort_df = pd.read_csv(DEFAULT_COMFORT_PERCEPTION_PATH, low_memory=False)
        respondent_training_df = build_respondent_comfort_training_data(
            measurements_df,
            comfort_df,
        )
        DEFAULT_RESPONDENT_TRAINING_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        respondent_training_df.to_csv(DEFAULT_RESPONDENT_TRAINING_OUTPUT_PATH, index=False)
        if args.output == DEFAULT_OUTPUT_PATH:
            args.output = DEFAULT_RESPONDENT_TARGET_OUTPUT_PATH
        if args.target_column == DEFAULT_TARGET_COLUMN:
            args.target_column = DEFAULT_RESPONDENT_TARGET_COLUMN
        if args.feature_columns == DEFAULT_FEATURE_COLUMNS:
            args.feature_columns = DEFAULT_RESPONDENT_FEATURE_COLUMNS
        filled_df, model_summary = fill_focus_scores_from_respondent_preferences(
            df,
            respondent_training_df,
            feature_columns=args.feature_columns,
            random_state=args.seed,
        )
    elif args.student_mode or args.student_training_input:
        training_path = args.student_training_input or DEFAULT_STUDENT_TRAINING_PATH
        training_df = pd.read_csv(training_path, low_memory=False)
        if args.output == DEFAULT_OUTPUT_PATH:
            args.output = DEFAULT_STUDENT_TARGET_OUTPUT_PATH
        if args.target_column == DEFAULT_TARGET_COLUMN:
            args.target_column = DEFAULT_STUDENT_TARGET_COLUMN
        if args.feature_columns == DEFAULT_FEATURE_COLUMNS:
            args.feature_columns = DEFAULT_STUDENT_FEATURE_COLUMNS
        filled_df, model_summary = fill_targets_from_student_preferences(
            df,
            training_df,
            feature_columns=args.feature_columns,
            target_column=args.target_column,
            group_column=args.group_column or DEFAULT_STUDENT_GROUP_COLUMN,
            random_state=args.seed,
            allowed_classes={0, 1},
        )
    else:
        filled_df, model_summary = fill_missing_targets(
            df,
            feature_columns=args.feature_columns,
            target_column=args.target_column,
            group_column=args.group_column,
            random_state=args.seed,
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    filled_df.to_csv(args.output, index=False)

    missing_after = int(filled_df[args.target_column].isna().sum())
    print(f"Saved filled dataset to: {args.output}")
    print(f"Rows: {len(filled_df):,}")
    print(f"Rows with missing {args.target_column}: {missing_after:,}")
    print(f"Per-student models trained: {len(model_summary):,}")
    print(model_summary.to_string(index=False))


if __name__ == "__main__":
    main()
