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
from scripts.linearize_session_windows import build_linearized_sessions


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

    assert len(unified) == 3
    assert unified["session_id"].nunique() == 2


def test_linearized_windows_split_sessions_by_configurable_gap():
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

    linearized, session_report = build_linearized_sessions(
        df,
        feature_columns=["temperature", "humidity"],
        max_segment_minutes=30,
        session_gap_minutes=30,
    )

    assert session_report["n_readings"].tolist() == [3, 1]
    assert len(linearized) == 2

    first_window = linearized.iloc[0]
    assert first_window["temperature_latest"] == 24.0
    assert first_window["temperature_mean"] == 22.0
    assert first_window["temperature_min"] == 20.0
    assert first_window["temperature_max"] == 24.0
    assert first_window["temperature_count"] == 3
    assert first_window["focus_score"] == 4


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

    linearized, _ = build_linearized_sessions(
        df,
        feature_columns=["temperature"],
        max_segment_minutes=15,
        session_gap_minutes=30,
    )

    assert len(linearized) == 2
    assert linearized.iloc[0]["temperature_mean"] == 21.0
    assert linearized.iloc[0]["temperature_count"] == 2
    assert linearized.iloc[1]["temperature_mean"] == 24.0
    assert linearized.iloc[1]["temperature_count"] == 1

