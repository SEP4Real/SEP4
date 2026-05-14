from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

import pandas as pd


MAL_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = MAL_DIR / "data"

DEFAULT_INPUT_PATH = DATA_DIR / "processed" / "unified_environment_respondent_focus_score_filled.csv"
DEFAULT_OUTPUT_PATH = DATA_DIR / "processed" / "linearized_session_windows_30min.csv"
DEFAULT_REPORT_PATH = DATA_DIR / "processed" / "linearized_session_windows_30min_report.csv"

DEFAULT_GROUP_COLUMNS = ["source", "location_id"]
DEFAULT_FEATURE_COLUMNS = ["temperature", "humidity", "light", "noise", "co2"]
DEFAULT_TARGET_COLUMN = "focus_score"
DEFAULT_TIMESTAMP_COLUMN = "timestamp"
DEFAULT_WINDOW_MINUTES = 30
DEFAULT_SESSION_GAP_MINUTES = 30

ROLLING_STATS = ["mean", "min", "max", "std", "count"]
METADATA_COLUMNS = [
    "linear_session_id",
    "source",
    "location_id",
    "window_end",
    "source_session_id",
    "source_record_id",
    "window_start",
    "session_elapsed_minutes",
]


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
    output_column: str = "linear_session_id",
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
        + "__gap"
        + str(session_gap_minutes)
        + "min__s"
        + session_number.astype(int).astype(str).str.zfill(5)
    )

    return working


def build_linearized_windows(
    df: pd.DataFrame,
    feature_columns: Sequence[str] = DEFAULT_FEATURE_COLUMNS,
    target_column: str = DEFAULT_TARGET_COLUMN,
    timestamp_column: str = DEFAULT_TIMESTAMP_COLUMN,
    group_columns: Sequence[str] = DEFAULT_GROUP_COLUMNS,
    window_minutes: int = DEFAULT_WINDOW_MINUTES,
    session_gap_minutes: int = DEFAULT_SESSION_GAP_MINUTES,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    validate_columns(df, [*group_columns, *feature_columns, target_column, timestamp_column])

    sessionized = add_gap_based_session_ids(
        df,
        group_columns=group_columns,
        timestamp_column=timestamp_column,
        session_gap_minutes=session_gap_minutes,
    )
    window = f"{window_minutes}min"
    output_parts: list[pd.DataFrame] = []

    for session_id, session_df in sessionized.groupby("linear_session_id", sort=False):
        session_df = session_df.sort_values("_parsed_timestamp", kind="mergesort").copy()
        session_indexed = session_df.set_index("_parsed_timestamp", drop=False)

        output = pd.DataFrame(
            {
                "linear_session_id": session_id,
                "source": session_df["source"].to_numpy() if "source" in session_df else pd.NA,
                "location_id": session_df["location_id"].to_numpy()
                if "location_id" in session_df
                else pd.NA,
                "window_end": session_df["_parsed_timestamp"].dt.strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                ).to_numpy(),
                "target_latest": pd.to_numeric(session_df[target_column], errors="coerce").to_numpy(),
            },
            index=session_df.index,
        )

        if "session_id" in session_df.columns:
            output["source_session_id"] = session_df["session_id"].to_numpy()
        if "record_id" in session_df.columns:
            output["source_record_id"] = session_df["record_id"].to_numpy()

        first_timestamp = session_df["_parsed_timestamp"].iloc[0]
        window_start = session_df["_parsed_timestamp"] - pd.Timedelta(minutes=window_minutes)
        output["window_start"] = window_start.clip(lower=first_timestamp).dt.strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        output["session_elapsed_minutes"] = (
            (session_df["_parsed_timestamp"] - first_timestamp).dt.total_seconds() / 60
        ).to_numpy()

        for feature in feature_columns:
            numeric = pd.to_numeric(session_indexed[feature], errors="coerce")
            rolling = numeric.rolling(window=window, min_periods=1).agg(ROLLING_STATS)
            rolling = rolling.reset_index(drop=True)

            output[f"{feature}_latest"] = numeric.reset_index(drop=True).to_numpy()
            output[f"{feature}_mean"] = rolling["mean"].to_numpy()
            output[f"{feature}_min"] = rolling["min"].to_numpy()
            output[f"{feature}_max"] = rolling["max"].to_numpy()
            output[f"{feature}_std"] = rolling["std"].fillna(0).to_numpy()
            output[f"{feature}_count"] = rolling["count"].astype("Int64").to_numpy()
            output[f"{feature}_range"] = (rolling["max"] - rolling["min"]).to_numpy()

        output_parts.append(output.reset_index(drop=True))

    if not output_parts:
        raise RuntimeError("No timestamped rows were available for linearization.")

    linearized_with_metadata = pd.concat(output_parts, ignore_index=True)
    linearized_with_metadata["focus_score"] = (
        linearized_with_metadata["target_latest"].round().astype("Int64")
    )
    linearized = linearized_with_metadata.drop(
        columns=[*METADATA_COLUMNS, "target_latest"],
        errors="ignore",
    )
    linearized = linearized[["focus_score", *[column for column in linearized.columns if column != "focus_score"]]]

    session_report = (
        sessionized.groupby("linear_session_id", dropna=False)
        .agg(
            source=("source", "first") if "source" in sessionized else ("linear_session_id", "size"),
            location_id=("location_id", "first")
            if "location_id" in sessionized
            else ("linear_session_id", "size"),
            rows=("linear_session_id", "size"),
            first_timestamp=("_parsed_timestamp", "min"),
            last_timestamp=("_parsed_timestamp", "max"),
        )
        .reset_index()
    )
    session_report["duration_minutes"] = (
        (session_report["last_timestamp"] - session_report["first_timestamp"]).dt.total_seconds()
        / 60
    )
    session_report["first_timestamp"] = session_report["first_timestamp"].dt.strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    session_report["last_timestamp"] = session_report["last_timestamp"].dt.strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    return linearized, session_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Split environmental rows into gap-based sessions and compress overlapping "
            "time windows into one ML-ready row per window end."
        )
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--report-output", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--window-minutes", type=int, default=DEFAULT_WINDOW_MINUTES)
    parser.add_argument("--session-gap-minutes", type=int, default=DEFAULT_SESSION_GAP_MINUTES)
    parser.add_argument("--features", nargs="+", default=DEFAULT_FEATURE_COLUMNS)
    parser.add_argument("--target-column", default=DEFAULT_TARGET_COLUMN)
    parser.add_argument("--timestamp-column", default=DEFAULT_TIMESTAMP_COLUMN)
    parser.add_argument("--group-columns", nargs="+", default=DEFAULT_GROUP_COLUMNS)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    df = pd.read_csv(args.input, low_memory=False)
    linearized, session_report = build_linearized_windows(
        df,
        feature_columns=args.features,
        target_column=args.target_column,
        timestamp_column=args.timestamp_column,
        group_columns=args.group_columns,
        window_minutes=args.window_minutes,
        session_gap_minutes=args.session_gap_minutes,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.report_output.parent.mkdir(parents=True, exist_ok=True)
    linearized.to_csv(args.output, index=False)
    session_report.to_csv(args.report_output, index=False)

    print(f"Saved linearized dataset to: {args.output}")
    print(f"Saved session report to: {args.report_output}")
    print(f"Rows: {len(linearized):,}")
    print(f"Sessions: {len(session_report):,}")
    print(f"Window minutes: {args.window_minutes}")
    print(f"Session gap minutes: {args.session_gap_minutes}")
    print(f"Missing targets: {linearized['focus_score'].isna().sum():,}")


if __name__ == "__main__":
    main()
