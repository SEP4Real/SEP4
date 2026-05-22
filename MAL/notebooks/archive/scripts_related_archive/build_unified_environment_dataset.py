from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import pandas as pd


MAL_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = MAL_DIR / "data"

DEFAULT_OUTPUT_PATH = DATA_DIR / "processed" / "unified_environment_focus_dataset.csv"
DEFAULT_REPORT_PATH = DATA_DIR / "processed" / "unified_environment_focus_dataset_report.csv"

SESSION_GAP = pd.Timedelta(hours=2)


@dataclass(frozen=True)
class SourceSpec:
    name: str
    path: Path


DEFAULT_SOURCES: tuple[SourceSpec, ...] = (
    SourceSpec("keti_1min_resampled", DATA_DIR / "interim" / "keti_1min_resampled.csv"),
    SourceSpec("room_conditions", DATA_DIR / "raw" / "DATA_1" / "room_conditions.csv"),
    SourceSpec(
        "room_measurements",
        DATA_DIR
        / "raw"
        / "DATA_8"
        / "smart-campus-comfort-data"
        / "1_room_measurements.csv",
    ),
    SourceSpec("homecoach_5min_2023", DATA_DIR / "raw" / "DATA_7" / "HomeCoach_5min_2023.csv"),
    SourceSpec("homecoach_5min_2024", DATA_DIR / "raw" / "DATA_7" / "HomeCoach_5min_2024.csv"),
    SourceSpec("homecoach_5min_2025", DATA_DIR / "raw" / "DATA_7" / "HomeCoach_5min_2025.csv"),
    SourceSpec("homecoach_5min_2026", DATA_DIR / "raw" / "DATA_7" / "HomeCoach_5min_2026.csv"),
)

OUTPUT_COLUMNS = [
    "timestamp",
    "session_id",
    "location_id",
    "record_id",
    "source",
    "humidity",
    "light",
    "temperature",
    "noise",
    "co2",
    "focus_score",
]
INFORMATION_COLUMNS = ["humidity", "light", "temperature", "noise", "co2", "focus_score"]

TIMESTAMP_CANDIDATES = ["timestamp", "date", "datetime", "time", "sent_at"]
HUMIDITY_CANDIDATES = ["humidity", "relative_humidity", "humidity_percent"]
LIGHT_CANDIDATES = ["light", "light_level", "illumination", "illuminance", "lux"]
TEMPERATURE_CANDIDATES = ["temperature", "temp", "current_temperature", "currentTemperature"]
NOISE_CANDIDATES = ["noise", "noice", "sound", "sound_level", "noise_level", "sound_db"]
CO2_CANDIDATES = ["co2", "co2_level", "carbon_dioxide", "carbonDioxide"]
FOCUS_SCORE_CANDIDATES = [
    "focus_score",
    "focus score",
    "focus",
    "rating",
    "comfort",
    "comfort_score",
    "comfort score",
    "comfortLevel",
    "comfort_level",
]

LOCATION_CANDIDATES = [
    "location_id",
    "location",
    "zone_id",
    "zone",
    "room_id",
    "room",
    "classroom",
    "space_id",
    "space",
]
SUBJECT_CANDIDATES = ["student_id", "student", "user_id", "participant_id", "person_id"]
DEVICE_CANDIDATES = ["device_id", "device", "sensor_id", "sensorId", "sensor"]
SESSION_CANDIDATES = ["session_id", "sessionId", "session"]
RECORD_ID_CANDIDATES = ["record_id", "measurement_id", "id"]


def normalise_column_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(name).strip().lower())


def slugify(value: object) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", str(value).strip().lower()).strip("_")
    return slug or "unknown"


def matching_columns(df: pd.DataFrame, candidates: Iterable[str]) -> list[str]:
    normalised_to_original: dict[str, list[str]] = {}
    for column in df.columns:
        normalised_to_original.setdefault(normalise_column_name(column), []).append(column)

    matches: list[str] = []
    for candidate in candidates:
        matches.extend(normalised_to_original.get(normalise_column_name(candidate), []))

    return list(dict.fromkeys(matches))


def coalesce_columns(df: pd.DataFrame, candidates: Iterable[str]) -> pd.Series:
    matches = matching_columns(df, candidates)
    if not matches:
        return pd.Series(pd.NA, index=df.index, dtype="object")

    result = df[matches[0]]
    for column in matches[1:]:
        result = result.combine_first(df[column])
    return result


def clean_identifier(series: pd.Series) -> pd.Series:
    text = series.astype("string").str.strip()
    missing_tokens = text.str.lower().isin(["", "nan", "none", "null", "<na>"])
    return text.mask(text.isna() | missing_tokens, pd.NA)


def to_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def parse_timestamps(series: pd.Series) -> pd.Series:
    try:
        parsed = pd.to_datetime(series, errors="coerce", utc=True, format="mixed")
    except (TypeError, ValueError):
        parsed = pd.to_datetime(series, errors="coerce", utc=True)
    return pd.Series(parsed, index=series.index)


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(MAL_DIR))
    except ValueError:
        return str(path)


def make_record_ids(source_slug: str, raw_df: pd.DataFrame) -> pd.Series:
    source_record_id = clean_identifier(coalesce_columns(raw_df, RECORD_ID_CANDIDATES))
    fallback_ids = pd.Series(
        (f"row_{position + 1:08d}" for position in range(len(raw_df))),
        index=raw_df.index,
        dtype="string",
    )
    source_record_id = source_record_id.combine_first(fallback_ids)
    return source_record_id.map(lambda value: f"{source_slug}:{value}")


def make_location_ids(source_slug: str, raw_df: pd.DataFrame) -> pd.Series:
    location = clean_identifier(coalesce_columns(raw_df, LOCATION_CANDIDATES))

    # Some public datasets do not contain a room/location column. In those cases
    # a student or device identifier is the next best grouping key.
    subject = clean_identifier(coalesce_columns(raw_df, SUBJECT_CANDIDATES))
    device = clean_identifier(coalesce_columns(raw_df, DEVICE_CANDIDATES))
    location = location.combine_first(subject).combine_first(device)

    fallback_location = pd.Series(
        f"{source_slug}_unknown_location",
        index=raw_df.index,
        dtype="string",
    )
    return location.combine_first(fallback_location).map(slugify)


def make_session_ids(
    source_slug: str,
    raw_df: pd.DataFrame,
    location_ids: pd.Series,
    timestamps: pd.Series,
) -> pd.Series:
    explicit_session = clean_identifier(coalesce_columns(raw_df, SESSION_CANDIDATES))
    session_ids = pd.Series(pd.NA, index=raw_df.index, dtype="object")

    explicit_mask = explicit_session.notna()
    session_ids.loc[explicit_mask] = explicit_session.loc[explicit_mask].map(
        lambda value: f"{source_slug}__{slugify(value)}"
    )

    missing_mask = session_ids.isna()
    if not missing_mask.any():
        return session_ids

    working = pd.DataFrame(
        {
            "location_id": location_ids.loc[missing_mask],
            "timestamp": timestamps.loc[missing_mask],
        },
        index=raw_df.index[missing_mask],
    )

    for location_id, location_df in working.groupby("location_id", dropna=False, sort=True):
        location_slug = slugify(location_id)
        known_time = location_df[location_df["timestamp"].notna()].sort_values(
            "timestamp",
            kind="mergesort",
        )
        unknown_time = location_df[location_df["timestamp"].isna()]

        if not unknown_time.empty:
            session_ids.loc[unknown_time.index] = (
                f"{source_slug}__{location_slug}__unknown_time"
            )

        if known_time.empty:
            continue

        gaps = known_time["timestamp"].diff()
        # Keep a session open across midnight when the actual time gap is small.
        starts_new_session = gaps.isna() | gaps.gt(SESSION_GAP)
        session_numbers = starts_new_session.cumsum()

        for row_index, session_number in session_numbers.items():
            session_ids.loc[row_index] = (
                f"{source_slug}__{location_slug}__s{int(session_number):05d}"
            )

    return session_ids


def standardise_source(spec: SourceSpec) -> tuple[pd.DataFrame, dict[str, object]]:
    raw_df = pd.read_csv(spec.path, low_memory=False)
    raw_row_count = len(raw_df)
    source_slug = slugify(spec.name)

    timestamps = parse_timestamps(coalesce_columns(raw_df, TIMESTAMP_CANDIDATES))
    timestamp_strings = timestamps.dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    timestamp_strings = timestamp_strings.mask(timestamps.isna(), pd.NA)

    focus_score = to_numeric(coalesce_columns(raw_df, FOCUS_SCORE_CANDIDATES))
    focus_score = focus_score.where(focus_score.between(1, 5))
    if focus_score.dropna().mod(1).eq(0).all():
        focus_score = focus_score.astype("Int64")

    location_ids = make_location_ids(source_slug, raw_df)
    record_ids = make_record_ids(source_slug, raw_df)
    humidity = to_numeric(coalesce_columns(raw_df, HUMIDITY_CANDIDATES))
    light = to_numeric(coalesce_columns(raw_df, LIGHT_CANDIDATES))
    temperature = to_numeric(coalesce_columns(raw_df, TEMPERATURE_CANDIDATES))
    noise = to_numeric(coalesce_columns(raw_df, NOISE_CANDIDATES))
    co2 = to_numeric(coalesce_columns(raw_df, CO2_CANDIDATES))

    information = pd.DataFrame(
        {
            "humidity": humidity,
            "light": light,
            "temperature": temperature,
            "noise": noise,
            "co2": co2,
            "focus_score": focus_score,
        },
        index=raw_df.index,
    )
    empty_rows = information[INFORMATION_COLUMNS].isna().all(axis=1)
    dropped_empty_rows = int(empty_rows.sum())

    raw_df = raw_df.loc[~empty_rows].copy()
    timestamps = timestamps.loc[raw_df.index]
    timestamp_strings = timestamp_strings.loc[raw_df.index]
    location_ids = location_ids.loc[raw_df.index]
    record_ids = record_ids.loc[raw_df.index]
    humidity = humidity.loc[raw_df.index]
    light = light.loc[raw_df.index]
    temperature = temperature.loc[raw_df.index]
    noise = noise.loc[raw_df.index]
    co2 = co2.loc[raw_df.index]
    focus_score = focus_score.loc[raw_df.index]

    standardised = pd.DataFrame(
        {
            "timestamp": timestamp_strings,
            "session_id": make_session_ids(source_slug, raw_df, location_ids, timestamps),
            "location_id": location_ids,
            "record_id": record_ids,
            "source": source_slug,
            "humidity": humidity,
            "light": light,
            "temperature": temperature,
            "noise": noise,
            "co2": co2,
            "focus_score": focus_score,
            "_parsed_timestamp": timestamps,
        }
    )

    output_timestamps = standardised["_parsed_timestamp"]

    report = {
        "source": source_slug,
        "input_path": display_path(spec.path),
        "raw_rows": raw_row_count,
        "output_rows": len(standardised),
        "dropped_empty_rows": dropped_empty_rows,
        "first_timestamp": output_timestamps.min(),
        "last_timestamp": output_timestamps.max(),
        "unique_locations": int(standardised["location_id"].nunique(dropna=True)),
        "unique_sessions": int(standardised["session_id"].nunique(dropna=True)),
        "labeled_rows": int(standardised["focus_score"].notna().sum()),
        "temperature_nonnull": int(standardised["temperature"].notna().sum()),
        "humidity_nonnull": int(standardised["humidity"].notna().sum()),
        "light_nonnull": int(standardised["light"].notna().sum()),
        "noise_nonnull": int(standardised["noise"].notna().sum()),
        "co2_nonnull": int(standardised["co2"].notna().sum()),
    }

    return standardised, report


def build_unified_dataset(
    sources: Sequence[SourceSpec] = DEFAULT_SOURCES,
    output_path: Path = DEFAULT_OUTPUT_PATH,
    report_path: Path = DEFAULT_REPORT_PATH,
    allow_missing: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    frames: list[pd.DataFrame] = []
    reports: list[dict[str, object]] = []

    for spec in sources:
        if not spec.path.exists():
            if allow_missing:
                reports.append(
                    {
                        "source": slugify(spec.name),
                        "input_path": display_path(spec.path),
                        "raw_rows": 0,
                        "output_rows": 0,
                        "status": "missing",
                    }
                )
                continue
            raise FileNotFoundError(f"Missing input dataset: {spec.path}")

        frame, report = standardise_source(spec)
        report["status"] = "ok"
        frames.append(frame)
        reports.append(report)

    if not frames:
        raise RuntimeError("No input datasets were loaded.")

    unified = pd.concat(frames, ignore_index=True)
    unified = unified.sort_values(
        ["_parsed_timestamp", "source", "location_id", "record_id"],
        kind="mergesort",
        na_position="last",
    ).reset_index(drop=True)
    unified = unified[OUTPUT_COLUMNS]

    report_df = pd.DataFrame(reports)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    unified.to_csv(output_path, index=False)
    report_df.to_csv(report_path, index=False)

    return unified, report_df


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Combine the available environmental datasets into one ML-friendly CSV."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help=f"Final CSV path. Defaults to {DEFAULT_OUTPUT_PATH}",
    )
    parser.add_argument(
        "--report-output",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help=f"Source coverage report path. Defaults to {DEFAULT_REPORT_PATH}",
    )
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="Skip missing source files instead of failing fast.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    unified, report = build_unified_dataset(
        output_path=args.output,
        report_path=args.report_output,
        allow_missing=args.allow_missing,
    )

    print(f"Saved unified dataset to: {args.output}")
    print(f"Saved source report to: {args.report_output}")
    print(f"Rows: {len(unified):,}")
    print(f"Rows with focus_score labels: {unified['focus_score'].notna().sum():,}")
    print(f"Sources combined: {report.loc[report['status'].eq('ok'), 'source'].nunique()}")


if __name__ == "__main__":
    main()
