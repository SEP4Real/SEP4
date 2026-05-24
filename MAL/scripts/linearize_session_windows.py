from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

import pandas as pd
import numpy as np


MAL_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = MAL_DIR / "data"

DEFAULT_INPUT_PATH = DATA_DIR / "processed" / "unified_environment_focus_dataset.csv"
DEFAULT_OUTPUT_PATH = DATA_DIR / "processed" / "linearized_sessions_with_missing_targets.csv"
DEFAULT_REPORT_PATH = DATA_DIR / "processed" / "linearized_sessions_with_missing_targets_report.csv"

DEFAULT_GROUP_COLUMNS = ["source", "location_id"]
DEFAULT_FEATURE_COLUMNS = ["temperature", "humidity", "light", "noise", "co2"]
DEFAULT_TARGET_COLUMN = "focus_score"
DEFAULT_TIMESTAMP_COLUMN = "timestamp"
DEFAULT_SESSION_GAP_MINUTES = 30
DEFAULT_MAX_SEGMENT_MINUTES = 240


def parse_timestamps(series: pd.Series) -> pd.Series:
    try:
        return pd.to_datetime(series, errors="coerce", utc=True, format="mixed")
    except (TypeError, ValueError):
        return pd.to_datetime(series, errors="coerce", utc=True)


def validate_columns(df: pd.DataFrame, required_columns: Sequence[str]) -> None:
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")


def add_gap_based_session_ids(
    df: pd.DataFrame,
    group_columns: Sequence[str],
    timestamp_column: str,
    session_gap_minutes: int,
    output_column: str = "session_id",
) -> pd.DataFrame:
    validate_columns(df, [*group_columns, timestamp_column])
    session_gap = pd.Timedelta(minutes=session_gap_minutes)

    working = df.copy()
    working["_parsed_timestamp"] = parse_timestamps(working[timestamp_column])
    working = working[working["_parsed_timestamp"].notna()].copy()
    working = working.sort_values(
        [*group_columns, "_parsed_timestamp", "record_id"]
        if "record_id" in working.columns
        else [*group_columns, "_parsed_timestamp"],
        kind="mergesort",
    ).reset_index(drop=True)

    group_key = working.groupby(list(group_columns), dropna=False, sort=False)
    gaps = group_key["_parsed_timestamp"].diff()
    starts_new_session = gaps.isna() | gaps.gt(session_gap)
    session_number = starts_new_session.groupby(
        [working[column] for column in group_columns],
        sort=False,
        dropna=False,
    ).cumsum()

    group_label = working[list(group_columns)].astype("string").agg("__".join, axis=1)
    working[output_column] = (
        group_label
        + "__s"
        + session_number.astype(int).astype(str).str.zfill(5)
    )

    return working


def build_linearized_sessions(
    df: pd.DataFrame,
    feature_columns: Sequence[str] = DEFAULT_FEATURE_COLUMNS,
    target_column: str = DEFAULT_TARGET_COLUMN,
    timestamp_column: str = DEFAULT_TIMESTAMP_COLUMN,
    group_columns: Sequence[str] = DEFAULT_GROUP_COLUMNS,
    session_gap_minutes: int = DEFAULT_SESSION_GAP_MINUTES,
    max_segment_minutes: int = DEFAULT_MAX_SEGMENT_MINUTES,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    validate_columns(df, [*group_columns, *feature_columns, target_column, timestamp_column])

    # 1. Continuous session identification by gap threshold
    sessionized = add_gap_based_session_ids(
        df,
        group_columns=group_columns,
        timestamp_column=timestamp_column,
        session_gap_minutes=session_gap_minutes,
    )
    
    # 2. Segment assignment within each session
    # Vectorized assignment of segment numbers and segment IDs
    session_starts = sessionized.groupby("session_id")["_parsed_timestamp"].transform("min")
    elapsed_minutes = (sessionized["_parsed_timestamp"] - session_starts).dt.total_seconds() / 60.0
    segment_nums = (elapsed_minutes // max_segment_minutes).astype(int)
    sessionized["segment_id"] = sessionized["session_id"] + "__seg" + segment_nums.astype(str).str.zfill(3)

    output_rows: list[dict] = []

    def last_valid(series: pd.Series) -> object:
        valid = series.dropna()
        if valid.empty:
            return pd.NA
        return valid.iloc[-1]

    # 3. Aggregate each segment into one row
    for segment_id, segment_df in sessionized.groupby("segment_id", sort=False):
        segment_df = segment_df.sort_values("_parsed_timestamp", kind="mergesort").copy()
        segment_start = segment_df["_parsed_timestamp"].iloc[0]
        segment_end = segment_df["_parsed_timestamp"].iloc[-1]
        duration_minutes = (segment_end - segment_start).total_seconds() / 60.0

        segment_targets = pd.to_numeric(segment_df[target_column], errors="coerce").dropna()
        if not segment_targets.empty:
            # Latest (last chronological) rating in the segment
            target_val = int(segment_targets.iloc[-1])
        else:
            target_val = pd.NA

        row = {
            "segment_id": segment_id,
            "session_id": segment_df["session_id"].iloc[0],
            "source": last_valid(segment_df["source"]) if "source" in segment_df else pd.NA,
            "location_id": last_valid(segment_df["location_id"]) if "location_id" in segment_df else pd.NA,
            "segment_start": segment_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "segment_end": segment_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "duration_minutes": duration_minutes,
            "n_readings": len(segment_df),
            "focus_score": target_val,
        }

        for feature in feature_columns:
            numeric = pd.to_numeric(segment_df[feature], errors="coerce")
            latest_value = last_valid(numeric)
            mean_value = numeric.mean()
            min_value = numeric.min()
            max_value = numeric.max()
            std_value = numeric.std()
            count_value = int(numeric.count())

            row[f"{feature}_latest"] = latest_value
            row[f"{feature}_mean"] = mean_value
            row[f"{feature}_min"] = min_value
            row[f"{feature}_max"] = max_value
            row[f"{feature}_std"] = 0.0 if pd.isna(std_value) else std_value
            row[f"{feature}_count"] = count_value
            row[f"{feature}_range"] = (
                max_value - min_value if pd.notna(max_value) and pd.notna(min_value) else pd.NA
            )

        output_rows.append(row)

    if not output_rows:
        raise RuntimeError("No timestamped rows were available for linearization.")

    linearized = pd.DataFrame(output_rows)
    
    # Put focus_score as the first column for standard dataset format
    cols = ["focus_score"] + [col for col in linearized.columns if col != "focus_score"]
    linearized = linearized[cols]

    # Generate session/segment report
    segment_report = (
        linearized[[
            "segment_id", "session_id", "source", "location_id", "segment_start", "segment_end", "duration_minutes", "n_readings"
        ]].copy()
    )

    return linearized, segment_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Split environmental rows into gap-based sessions, segment by maximum duration, "
            "and compress each segment into exactly one ML-ready row."
        )
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--report-output", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--session-gap-minutes", type=int, default=DEFAULT_SESSION_GAP_MINUTES)
    parser.add_argument("--max-segment-minutes", type=int, default=DEFAULT_MAX_SEGMENT_MINUTES)
    parser.add_argument("--features", nargs="+", default=DEFAULT_FEATURE_COLUMNS)
    parser.add_argument("--target-column", default=DEFAULT_TARGET_COLUMN)
    parser.add_argument("--timestamp-column", default=DEFAULT_TIMESTAMP_COLUMN)
    parser.add_argument("--group-columns", nargs="+", default=DEFAULT_GROUP_COLUMNS)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(f"Reading unified dataset from: {args.input}")
    df = pd.read_csv(args.input, low_memory=False)
    linearized, segment_report = build_linearized_sessions(
        df,
        feature_columns=args.features,
        target_column=args.target_column,
        timestamp_column=args.timestamp_column,
        group_columns=args.group_columns,
        session_gap_minutes=args.session_gap_minutes,
        max_segment_minutes=args.max_segment_minutes,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.report_output.parent.mkdir(parents=True, exist_ok=True)
    linearized.to_csv(args.output, index=False)
    segment_report.to_csv(args.report_output, index=False)

    print(f"Saved linearized dataset to: {args.output}")
    print(f"Saved segment report to: {args.report_output}")
    print(f"Rows/Segments: {len(linearized):,}")
    print(f"Segment gap limit (min): {args.session_gap_minutes}")
    print(f"Max segment length (min): {args.max_segment_minutes}")
    print(f"Missing targets: {linearized['focus_score'].isna().sum():,}")
    print(f"Labeled targets: {linearized['focus_score'].notna().sum():,}")


if __name__ == "__main__":
    main()
