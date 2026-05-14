from pathlib import Path
import sys

import pandas as pd

MAL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MAL_DIR))

from scripts.build_unified_environment_dataset import (
    SourceSpec,
    build_unified_dataset,
    make_location_ids,
    make_session_ids,
    parse_timestamps,
)
from scripts.fill_missing_targets import (
    build_respondent_comfort_training_data,
    fill_focus_scores_from_respondent_preferences,
    fill_missing_targets,
    fill_targets_from_student_preferences,
)
from scripts.linearize_session_windows import build_linearized_windows


def test_session_ids_do_not_split_on_midnight_when_gap_is_small():
    raw_df = pd.DataFrame(
        {
            "timestamp": [
                "2026-05-14T23:50:00Z",
                "2026-05-15T00:10:00Z",
                "2026-05-15T03:00:00Z",
            ],
            "room": ["Lab 1", "Lab 1", "Lab 1"],
        }
    )
    timestamps = parse_timestamps(raw_df["timestamp"])
    location_ids = make_location_ids("test_source", raw_df)

    session_ids = make_session_ids("test_source", raw_df, location_ids, timestamps)

    assert session_ids.iloc[0] == session_ids.iloc[1]
    assert session_ids.iloc[2] != session_ids.iloc[1]


def test_build_unified_dataset_maps_comfort_level_to_focus_score(tmp_path: Path):
    source_path = tmp_path / "comfort_measurements.csv"
    source_path.write_text(
        "\n".join(
            [
                "timestamp,room,temperature,humidity,noise,CO2,comfortLevel",
                "2026-05-14T10:00:00Z,Lab 1,22.1,45,41,500,4",
                "2026-05-14T10:05:00Z,Lab 1,22.3,46,42,505,5",
            ]
        )
    )

    unified, report = build_unified_dataset(
        sources=(SourceSpec("comfort_measurements", source_path),),
        output_path=tmp_path / "unified.csv",
        report_path=tmp_path / "report.csv",
    )

    assert unified["focus_score"].tolist() == [4, 5]
    assert report.loc[0, "labeled_rows"] == 2


def test_session_ids_are_inferred_after_empty_rows_are_dropped(tmp_path: Path):
    source_path = tmp_path / "measurements_with_empty_gap.csv"
    source_path.write_text(
        "\n".join(
            [
                "timestamp,room,temperature,humidity,CO2",
                "2026-05-14T10:00:00Z,Lab 1,22.1,45,500",
                "2026-05-14T11:00:00Z,Lab 1,,,",
                "2026-05-14T13:30:00Z,Lab 1,22.3,46,505",
            ]
        )
    )

    unified, report = build_unified_dataset(
        sources=(SourceSpec("empty_gap", source_path),),
        output_path=tmp_path / "unified.csv",
        report_path=tmp_path / "report.csv",
    )

    assert len(unified) == 2
    assert unified["session_id"].nunique() == 2
    assert report.loc[0, "dropped_empty_rows"] == 1


def test_fill_missing_targets_trains_student_models_and_fills_missing_values():
    df = pd.DataFrame(
        {
            "student_id": ["s1", "s1", "s2", "s2", "s3", "s4"],
            "humidity": [40, 42, 60, 62, 45, 55],
            "light": [300, 310, 500, 510, 350, 450],
            "temperature": [21, 21.5, 25, 25.5, 22, 24],
            "noise": [40, 41, 65, 66, 45, 55],
            "co2": [500, 510, 900, 920, 550, 750],
            "focus_score": [4, 4, 2, 2, None, None],
        }
    )

    filled, model_summary = fill_missing_targets(df, group_column="student_id", random_state=7)

    assert filled["focus_score"].isna().sum() == 0
    assert filled["focus_score"].between(1, 5).all()
    assert model_summary["student_id"].tolist() == ["s1", "s2"]


def test_fill_targets_from_student_preferences_uses_student_training_dataset():
    conditions = pd.DataFrame(
        {
            "humidity": [40, 60, 50],
            "light": [300, 700, 500],
            "temperature": [21, 28, 24],
            "noise": [35, 70, 50],
        }
    )
    student_training = pd.DataFrame(
        {
            "student_id": [101, 101, 102, 102],
            "humidity": [35, 45, 55, 65],
            "ambient_light": [250, 350, 650, 750],
            "temperature": [20, 22, 27, 29],
            "ambient_noise": [30, 40, 65, 75],
            "target": [0, 0, 1, 1],
        }
    )

    filled, model_summary = fill_targets_from_student_preferences(
        conditions,
        student_training,
        random_state=3,
        allowed_classes={0, 1},
    )

    assert filled["target"].isna().sum() == 0
    assert set(filled["target"].unique()).issubset({0, 1})
    assert model_summary["student_id"].tolist() == ["101", "102"]


def test_respondent_comfort_training_preserves_respondent_ids_and_1_to_5_target():
    measurements = pd.DataFrame(
        {
            "timestamp": ["2026-05-14T10:00:00Z", "2026-05-14T10:05:00Z"],
            "room": ["Lab 1", "Lab 1"],
            "temperature": [22.0, 23.0],
            "humidity": [45.0, 46.0],
            "noise": [40.0, 42.0],
            "CO2": [500.0, 520.0],
        }
    )
    comfort = pd.DataFrame(
        {
            "timestamp": ["2026-05-14T10:01:00Z", "2026-05-14T10:06:00Z"],
            "respondentId": [13, 31],
            "room": ["Lab 1", "Lab 1"],
            "comfortValue": [4, 5],
        }
    )

    training = build_respondent_comfort_training_data(measurements, comfort)

    assert training["respondent_id"].tolist() == [13, 31]
    assert training["focus_score"].tolist() == [4, 5]
    assert "co2" in training.columns


def test_fill_focus_scores_from_respondent_preferences_outputs_1_to_5_scores():
    conditions = pd.DataFrame(
        {
            "humidity": [45.0, 55.0],
            "temperature": [22.0, 26.0],
            "noise": [40.0, 60.0],
            "co2": [500.0, 800.0],
            "focus_score": [None, None],
        }
    )
    respondent_training = pd.DataFrame(
        {
            "respondent_id": [13, 13, 31, 31],
            "humidity": [44.0, 46.0, 54.0, 56.0],
            "temperature": [21.5, 22.5, 25.5, 26.5],
            "noise": [39.0, 41.0, 59.0, 61.0],
            "co2": [490.0, 510.0, 790.0, 810.0],
            "focus_score": [4, 4, 2, 2],
        }
    )

    filled, model_summary = fill_focus_scores_from_respondent_preferences(
        conditions,
        respondent_training,
        random_state=4,
    )

    assert filled["focus_score"].isna().sum() == 0
    assert filled["focus_score"].between(1, 5).all()
    assert model_summary["student_id"].tolist() == ["13", "31"]


def test_linearized_windows_split_sessions_by_configurable_gap_and_overlap():
    df = pd.DataFrame(
        {
            "timestamp": [
                "2026-05-14T10:00:00Z",
                "2026-05-14T10:10:00Z",
                "2026-05-14T10:20:00Z",
                "2026-05-14T11:00:00Z",
            ],
            "source": ["test"] * 4,
            "location_id": ["room_a"] * 4,
            "record_id": ["r1", "r2", "r3", "r4"],
            "session_id": ["old"] * 4,
            "temperature": [20.0, 22.0, 24.0, 30.0],
            "humidity": [40.0, 42.0, 44.0, 50.0],
            "focus_score": [2, 3, 4, 5],
        }
    )

    linearized, session_report = build_linearized_windows(
        df,
        feature_columns=["temperature", "humidity"],
        window_minutes=30,
        session_gap_minutes=30,
    )

    assert "linear_session_id" not in linearized.columns
    assert "source" not in linearized.columns
    assert "window_end" not in linearized.columns
    assert session_report["rows"].tolist() == [3, 1]

    third_window = linearized.iloc[2]
    assert third_window["temperature_latest"] == 24.0
    assert third_window["temperature_mean"] == 22.0
    assert third_window["temperature_min"] == 20.0
    assert third_window["temperature_max"] == 24.0
    assert third_window["focus_score"] == 4


def test_linearized_window_size_is_configurable():
    df = pd.DataFrame(
        {
            "timestamp": [
                "2026-05-14T10:00:00Z",
                "2026-05-14T10:10:00Z",
                "2026-05-14T10:20:00Z",
            ],
            "source": ["test"] * 3,
            "location_id": ["room_a"] * 3,
            "temperature": [20.0, 22.0, 24.0],
            "focus_score": [2, 3, 4],
        }
    )

    linearized, _ = build_linearized_windows(
        df,
        feature_columns=["temperature"],
        window_minutes=15,
        session_gap_minutes=30,
    )

    assert linearized.iloc[2]["temperature_mean"] == 23.0
    assert linearized.iloc[2]["temperature_count"] == 2
    assert list(linearized.columns) == [
        "focus_score",
        "temperature_latest",
        "temperature_mean",
        "temperature_min",
        "temperature_max",
        "temperature_std",
        "temperature_count",
        "temperature_range",
    ]
