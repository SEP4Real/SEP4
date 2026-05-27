"""
session_linearize_and_score.py
================================
Two-stage pipeline that produces a compact, fully-labelled ML dataset
directly from raw sensor rows, without any intermediate per-row fill step.

Stage 1 — Linearize
    Group rows by room (source + location_id), sort by timestamp, split into
    sessions whenever the gap between consecutive readings exceeds
    ``session_gap_minutes`` (default 30 min).  Every session is compressed
    into *one row* containing seven aggregates per sensor feature:
        mean, min, max, std, latest (last reading), count, range (max - min)
    plus session-level metadata: start/end timestamps, duration, n_readings.

    Input:  ~947k raw rows  →  Output: ~tens-of-thousands of session rows.

Stage 2 — Score
    Assign a focus_score (1–5) to every session row using eight hand-crafted
    *session-aware* personas.  Unlike the per-reading profiles in
    fill_missing_targets_profiles.py, these personas evaluate the *full
    shape* of a session: not just the average condition but also the
    worst-case reading and how variable conditions were throughout.

    The comfort formula for each sensor is:
        base_weight  × gaussian(mean,    ideal, tolerance)
      + worst_weight × gaussian(max,     ideal, tolerance)   # noise / CO2
      + stab_weight  × exp(-std / tolerance)                  # low variability
    where base_weight = 1 - worst_weight - stab_weight.

CLI usage
---------
    python scripts/session_linearize_and_score.py
    python scripts/session_linearize_and_score.py \\
        --input data/processed/final_mock_dataset.csv \\
        --output data/processed/sessions_scored.csv
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
MAL_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = MAL_DIR / "data"

DEFAULT_INPUT_PATH    = DATA_DIR / "processed" / "final_mock_dataset.csv"
DEFAULT_SESSIONS_PATH = DATA_DIR / "processed" / "sessions_linearized_30min.csv"
DEFAULT_OUTPUT_PATH   = DATA_DIR / "processed" / "sessions_scored_30min.csv"

RANDOM_STATE         = 42
SESSION_GAP_MINUTES  = 30
FEATURE_COLUMNS      = ["temperature", "humidity", "noise", "co2", "light"]
GROUP_COLUMNS        = ["source", "location_id"]


# ---------------------------------------------------------------------------
# Stage 1 — Linearise sessions
# ---------------------------------------------------------------------------

def _parse_timestamps(series: pd.Series) -> pd.Series:
    try:
        return pd.to_datetime(series, errors="coerce", utc=True, format="mixed")
    except (TypeError, ValueError):
        return pd.to_datetime(series, errors="coerce", utc=True)


def linearize_sessions(
    df: pd.DataFrame,
    group_columns: list[str] | None = None,
    feature_columns: list[str] | None = None,
    session_gap_minutes: int = SESSION_GAP_MINUTES,
) -> pd.DataFrame:
    """
    Collapse raw sensor rows into one row per 30-minute session.

    Each output row contains:
      - Metadata: source, location_id, session_id, session_start, session_end,
                  session_duration_minutes, n_readings
      - For every feature: {feat}_mean, {feat}_min, {feat}_max, {feat}_std,
                           {feat}_latest, {feat}_count, {feat}_range

    Parameters
    ----------
    df:
        Raw sensor DataFrame with at least 'timestamp' and the group columns.
    group_columns:
        Columns that identify a unique "room". Defaults to ['source', 'location_id'].
    feature_columns:
        Sensor feature columns to aggregate. Defaults to FEATURE_COLUMNS.
    session_gap_minutes:
        Duration of each fixed time window in minutes (default 30).
        Every timestamp is floored to the nearest ``session_gap_minutes``
        boundary so each room produces exactly one session row per window,
        regardless of how long the data stream runs.

    Returns
    -------
    sessions_df: DataFrame with one row per session, fully aggregated.
    """
    group_columns   = group_columns   or GROUP_COLUMNS
    feature_columns = feature_columns or FEATURE_COLUMNS

    df = df.copy()
    df["_ts"] = _parse_timestamps(df["timestamp"])
    df = df[df["_ts"].notna()].copy()
    df = df.sort_values([*group_columns, "_ts"]).reset_index(drop=True)

    # ── Assign session IDs (vectorised) ─────────────────────────────────
    # Group number (integer label per unique combination of group columns)
    df["_grp"] = df.groupby(group_columns, sort=False, observed=True).ngroup()

    # Floor every timestamp to the start of its 30-min bucket.
    # This is the key fix: using dt.floor() instead of gap detection ensures
    # that each room produces one row per 30-min window across its full stream.
    # Gap detection only produces ~1 session per room for nearly-continuous data.
    df["_window"] = df["_ts"].dt.floor(f"{session_gap_minutes}min")

    # Composite session key = room identity + window start timestamp
    df["_sess_key"] = df["_grp"].astype(str) + "__" + df["_window"].astype(str)

    # ── Build named-aggregation dict ─────────────────────────────────────
    # Each entry maps output_column_name → (source_column, aggregation_func)
    existing_features = [f for f in feature_columns if f in df.columns]
    for feat in existing_features:
        df[feat] = pd.to_numeric(df[feat], errors="coerce")

    named_agg: dict[str, tuple] = {}
    for col in group_columns:
        named_agg[col] = (col, "first")
    named_agg["session_start"] = ("_ts", "min")
    named_agg["session_end"]   = ("_ts", "max")
    named_agg["n_readings"]    = ("_ts", "count")

    for feat in existing_features:
        named_agg[f"{feat}_mean"]   = (feat, "mean")
        named_agg[f"{feat}_min"]    = (feat, "min")
        named_agg[f"{feat}_max"]    = (feat, "max")
        named_agg[f"{feat}_std"]    = (feat, "std")
        named_agg[f"{feat}_latest"] = (feat, "last")
        named_agg[f"{feat}_count"]  = (feat, "count")

    # ── Aggregate ────────────────────────────────────────────────────────
    sessions = df.groupby("_sess_key", sort=False).agg(**{
        out_col: pd.NamedAgg(column=src_col, aggfunc=func)
        for out_col, (src_col, func) in named_agg.items()
    })
    sessions = sessions.reset_index(drop=True)

    # ── Derived columns ──────────────────────────────────────────────────
    sessions["session_duration_minutes"] = (
        (sessions["session_end"] - sessions["session_start"])
        .dt.total_seconds()
        .div(60)
    )
    sessions["session_start"] = sessions["session_start"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    sessions["session_end"]   = sessions["session_end"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    for feat in existing_features:
        max_col = f"{feat}_max"
        min_col = f"{feat}_min"
        std_col = f"{feat}_std"
        if max_col in sessions.columns and min_col in sessions.columns:
            sessions[f"{feat}_range"] = sessions[max_col] - sessions[min_col]
        if std_col in sessions.columns:
            # std is NaN for single-reading sessions → treat as 0 (no variability)
            sessions[std_col] = sessions[std_col].fillna(0.0)

    # Give missing features NaN columns so downstream code is uniform
    for feat in feature_columns:
        if feat not in existing_features:
            for suffix in ("mean", "min", "max", "std", "latest", "count", "range"):
                sessions[f"{feat}_{suffix}"] = np.nan

    # ── Global session ID ────────────────────────────────────────────────
    sessions.insert(0, "session_id", range(len(sessions)))

    return sessions


# ---------------------------------------------------------------------------
# Stage 2 — Session-aware profiles
# ---------------------------------------------------------------------------

@dataclass
class SessionProfile:
    """
    A persona that scores a *session* (not a single reading).

    Comfort is computed as a weighted blend of:
    - **mean comfort**     — how comfortable were average conditions?
    - **worst-case**       — how bad was the worst reading?
                             (max for noise/CO2; min/max for temp & humidity)
    - **stability**        — was the environment stable throughout the session?
    """
    name: str
    description: str

    # Ideal mean conditions
    ideal_temperature: float     # °C
    ideal_humidity:    float     # %
    ideal_noise:       float     # dB
    ideal_co2:         float     # ppm

    # Gaussian tolerance for mean deviations
    temp_tolerance:     float
    humidity_tolerance: float
    noise_tolerance:    float
    co2_tolerance:      float

    # Score blend weights
    worst_case_weight:  float = 0.30  # weight on worst-case reading
    variability_weight: float = 0.15  # weight on stability (penalises high std)

    # How much overall environment shifts the base distribution
    env_sensitivity:    float = 0.55

    # Prior distribution over scores [1, 2, 3, 4, 5] in comfortable conditions
    base_weights: list[float] = field(
        default_factory=lambda: [0.05, 0.10, 0.30, 0.35, 0.20]
    )


SESSION_PROFILES: list[SessionProfile] = [
    SessionProfile(
        name="thermophile_student",
        description=(
            "Needs warmth to concentrate. Cold spikes and temperature swings "
            "hurt focus. Worst-case cold reading weighs heavily."
        ),
        ideal_temperature=23.0, ideal_humidity=50.0,
        ideal_noise=35.0,       ideal_co2=700.0,
        temp_tolerance=2.5,     humidity_tolerance=15.0,
        noise_tolerance=8.0,    co2_tolerance=300.0,
        worst_case_weight=0.35, variability_weight=0.15,
        env_sensitivity=0.65,
        base_weights=[0.03, 0.07, 0.20, 0.40, 0.30],
    ),
    SessionProfile(
        name="cool_air_engineer",
        description=(
            "Prefers cool, fresh sessions. Notices when CO2 climbs over the "
            "session. Comfortable with moderate sustained noise."
        ),
        ideal_temperature=19.5, ideal_humidity=45.0,
        ideal_noise=45.0,       ideal_co2=500.0,
        temp_tolerance=3.0,     humidity_tolerance=20.0,
        noise_tolerance=15.0,   co2_tolerance=200.0,
        worst_case_weight=0.30, variability_weight=0.10,
        env_sensitivity=0.55,
        base_weights=[0.04, 0.10, 0.25, 0.38, 0.23],
    ),
    SessionProfile(
        name="noise_sensitive_introvert",
        description=(
            "Loses focus the moment noise peaks. Worst-case noise max dominates "
            "the comfort score — even one loud event ruins the session."
        ),
        ideal_temperature=21.0, ideal_humidity=50.0,
        ideal_noise=28.0,       ideal_co2=650.0,
        temp_tolerance=5.0,     humidity_tolerance=20.0,
        noise_tolerance=5.0,    co2_tolerance=350.0,
        worst_case_weight=0.45, variability_weight=0.20,
        env_sensitivity=0.70,
        base_weights=[0.02, 0.08, 0.20, 0.40, 0.30],
    ),
    SessionProfile(
        name="balanced_professional",
        description=(
            "Evaluates sessions holistically. Neither mean nor extreme dominates. "
            "Variability matters a little. Resilient to minor deviations."
        ),
        ideal_temperature=21.5, ideal_humidity=50.0,
        ideal_noise=40.0,       ideal_co2=650.0,
        temp_tolerance=4.0,     humidity_tolerance=20.0,
        noise_tolerance=12.0,   co2_tolerance=300.0,
        worst_case_weight=0.25, variability_weight=0.15,
        env_sensitivity=0.45,
        base_weights=[0.05, 0.10, 0.30, 0.35, 0.20],
    ),
    SessionProfile(
        name="humidity_sensitive_artist",
        description=(
            "Highly sensitive to humidity swings within a session. A wide "
            "humidity range is very distracting even if the mean is fine."
        ),
        ideal_temperature=22.0, ideal_humidity=55.0,
        ideal_noise=42.0,       ideal_co2=700.0,
        temp_tolerance=3.5,     humidity_tolerance=8.0,
        noise_tolerance=14.0,   co2_tolerance=350.0,
        worst_case_weight=0.20, variability_weight=0.30,
        env_sensitivity=0.60,
        base_weights=[0.04, 0.10, 0.25, 0.38, 0.23],
    ),
    SessionProfile(
        name="co2_sleepy_type",
        description=(
            "CO2 accumulation over a session is the primary concern. "
            "Both mean and max CO2 are heavily penalised. Loses focus in stuffy sessions."
        ),
        ideal_temperature=21.0, ideal_humidity=48.0,
        ideal_noise=38.0,       ideal_co2=450.0,
        temp_tolerance=4.5,     humidity_tolerance=18.0,
        noise_tolerance=12.0,   co2_tolerance=150.0,
        worst_case_weight=0.40, variability_weight=0.10,
        env_sensitivity=0.65,
        base_weights=[0.05, 0.12, 0.28, 0.35, 0.20],
    ),
    SessionProfile(
        name="outdoor_craver",
        description=(
            "Strongly dislikes warm, stuffy sessions. Worst-case temperature "
            "and CO2 peaks both matter. Long warm sessions feel exhausting."
        ),
        ideal_temperature=18.0, ideal_humidity=55.0,
        ideal_noise=35.0,       ideal_co2=450.0,
        temp_tolerance=2.0,     humidity_tolerance=15.0,
        noise_tolerance=10.0,   co2_tolerance=200.0,
        worst_case_weight=0.35, variability_weight=0.15,
        env_sensitivity=0.70,
        base_weights=[0.05, 0.12, 0.28, 0.35, 0.20],
    ),
    SessionProfile(
        name="robust_multitasker",
        description=(
            "Barely affected by any single dimension. Even large swings and "
            "high worst-case readings barely shift the score. "
            "Slightly biased toward moderate scores."
        ),
        ideal_temperature=21.0, ideal_humidity=50.0,
        ideal_noise=50.0,       ideal_co2=800.0,
        temp_tolerance=7.0,     humidity_tolerance=25.0,
        noise_tolerance=20.0,   co2_tolerance=500.0,
        worst_case_weight=0.15, variability_weight=0.10,
        env_sensitivity=0.30,
        base_weights=[0.08, 0.18, 0.34, 0.28, 0.12],
    ),
]


# ---------------------------------------------------------------------------
# Comfort scoring for sessions
# ---------------------------------------------------------------------------

def _gaussian(value: float, ideal: float, tolerance: float) -> float:
    """Gaussian comfort kernel — returns 1.0 at ideal, decays to 0 at extremes."""
    if np.isnan(value):
        return 0.5  # neutral when sensor data is absent
    return float(np.exp(-0.5 * ((value - ideal) / tolerance) ** 2))


def _sensor_comfort(
    mean_val: float,
    min_val: float,
    max_val: float,
    std_val: float,
    ideal: float,
    tolerance: float,
    high_bad: bool,
    worst_case_weight: float,
    variability_weight: float,
) -> float:
    """
    Composite comfort score [0, 1] for one sensor over an entire session.

    Parameters
    ----------
    high_bad:
        True  → high values are uncomfortable (noise, CO2) → worst = max
        False → both extremes are uncomfortable (temp, humidity) → worst = min(min_comfort, max_comfort)
    """
    mean_score = _gaussian(mean_val, ideal, tolerance)

    if high_bad:
        worst_score = _gaussian(max_val, ideal, tolerance)
    else:
        # Take the worse of the two extremes
        worst_score = min(
            _gaussian(min_val, ideal, tolerance),
            _gaussian(max_val, ideal, tolerance),
        )

    # Stability: low std → stable → comfortable
    # Normalise std by tolerance so the scale is profile-relative
    safe_tol = max(tolerance * 0.5, 1e-6)
    stability_score = float(np.exp(-float(std_val) / safe_tol)) if not np.isnan(std_val) else 0.5

    base_weight = 1.0 - worst_case_weight - variability_weight
    return base_weight * mean_score + worst_case_weight * worst_score + variability_weight * stability_score


def session_comfort_score(
    profile: SessionProfile,
    session_row: pd.Series,
) -> float:
    """
    Compute overall comfort score in [0, 1] for one session under a given profile.
    Averages across all four primary sensors.
    """
    def _g(key: str) -> float:
        val = session_row.get(key, np.nan)
        return float(val) if val is not None and not pd.isna(val) else np.nan

    wc = profile.worst_case_weight
    vw = profile.variability_weight
    sensor_scores = []

    # Temperature: both cold and hot are bad
    sensor_scores.append(_sensor_comfort(
        _g("temperature_mean"), _g("temperature_min"), _g("temperature_max"), _g("temperature_std"),
        profile.ideal_temperature, profile.temp_tolerance,
        high_bad=False, worst_case_weight=wc, variability_weight=vw,
    ))

    # Humidity: both dry and damp are bad
    sensor_scores.append(_sensor_comfort(
        _g("humidity_mean"), _g("humidity_min"), _g("humidity_max"), _g("humidity_std"),
        profile.ideal_humidity, profile.humidity_tolerance,
        high_bad=False, worst_case_weight=wc, variability_weight=vw,
    ))

    # Noise: high is bad
    sensor_scores.append(_sensor_comfort(
        _g("noise_mean"), _g("noise_min"), _g("noise_max"), _g("noise_std"),
        profile.ideal_noise, profile.noise_tolerance,
        high_bad=True, worst_case_weight=wc, variability_weight=vw,
    ))

    # CO2: high is bad
    sensor_scores.append(_sensor_comfort(
        _g("co2_mean"), _g("co2_min"), _g("co2_max"), _g("co2_std"),
        profile.ideal_co2, profile.co2_tolerance,
        high_bad=True, worst_case_weight=wc, variability_weight=vw,
    ))

    return float(np.nanmean(sensor_scores))


def _sample_focus_score(
    profile: SessionProfile,
    comfort: float,
    rng: np.random.Generator,
) -> int:
    """Sample a 1–5 score from the profile's environment-adjusted distribution."""
    base = np.array(profile.base_weights, dtype=float)
    base /= base.sum()

    # Shift distribution based on comfort: comfort=1 → center near 5, comfort=0 → near 1
    scores = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    center = 1.0 + comfort * 4.0
    sigma  = 1.2
    env_weights = np.exp(-0.5 * ((scores - center) / sigma) ** 2)
    env_weights /= env_weights.sum()

    s      = profile.env_sensitivity
    final  = (1 - s) * base + s * env_weights
    final /= final.sum()

    return int(rng.choice([1, 2, 3, 4, 5], p=final))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def score_sessions(
    sessions_df: pd.DataFrame,
    profiles: list[SessionProfile] | None = None,
    target_column: str = "focus_score",
    random_state: int = RANDOM_STATE,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Assign a focus_score (1–5) to every session row.

    Parameters
    ----------
    sessions_df:
        Output of :func:`linearize_sessions` (one row per session).
    profiles:
        List of :class:`SessionProfile` instances. Defaults to SESSION_PROFILES.
    target_column:
        Column name to write the score into.
    random_state:
        RNG seed for reproducibility.

    Returns
    -------
    scored_df:
        Copy of *sessions_df* with *target_column* populated.
    profile_summary:
        DataFrame with one row per profile showing how many sessions it scored.
    """
    profiles = profiles or SESSION_PROFILES
    rng      = np.random.default_rng(random_state)

    scored = sessions_df.copy()
    n      = len(scored)

    # Randomly assign each session to a profile (uniform)
    profile_indexes  = rng.integers(0, len(profiles), size=n)
    fill_counts      = np.zeros(len(profiles), dtype=int)
    scores           = np.empty(n, dtype=int)

    for i, (_, row) in enumerate(scored.iterrows()):
        p           = profiles[int(profile_indexes[i])]
        comfort     = session_comfort_score(p, row)
        scores[i]   = _sample_focus_score(p, comfort, rng)
        fill_counts[int(profile_indexes[i])] += 1

    scored[target_column] = scores

    summary = pd.DataFrame([
        {
            "profile_name":       p.name,
            "description":        p.description,
            "ideal_temperature":  p.ideal_temperature,
            "ideal_humidity":     p.ideal_humidity,
            "ideal_noise":        p.ideal_noise,
            "ideal_co2":          p.ideal_co2,
            "worst_case_weight":  p.worst_case_weight,
            "variability_weight": p.variability_weight,
            "env_sensitivity":    p.env_sensitivity,
            "sessions_scored":    int(fill_counts[i]),
        }
        for i, p in enumerate(profiles)
    ])
    return scored, summary


def run_pipeline(
    input_path: Path = DEFAULT_INPUT_PATH,
    sessions_path: Path = DEFAULT_SESSIONS_PATH,
    output_path: Path = DEFAULT_OUTPUT_PATH,
    session_gap_minutes: int = SESSION_GAP_MINUTES,
    random_state: int = RANDOM_STATE,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Convenience wrapper: read raw CSV → linearize → score → save both CSVs.

    Returns
    -------
    sessions_df, scored_df, profile_summary
    """
    df = pd.read_csv(input_path, low_memory=False)
    sessions_df = linearize_sessions(df, session_gap_minutes=session_gap_minutes)
    _overwrite_csv(sessions_df, sessions_path)

    scored_df, summary = score_sessions(sessions_df, random_state=random_state)

    drop_cols = ["session_id", "source", "location_id", "session_start", "session_end", "n_readings"]
    export_df = scored_df.drop(columns=drop_cols, errors="ignore")
    
    _overwrite_csv(export_df, output_path)

    return sessions_df, scored_df, summary


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------

def _overwrite_csv(df: pd.DataFrame, path: Path) -> None:
    """Always overwrite — explicitly delete any pre-existing file first."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
        print(f"  [overwrite] removed existing: {path.name}")
    df.to_csv(path, index=False, mode="w")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Linearize raw sensor rows into 30-min sessions, then assign "
            "focus_score using session-aware profile-based sampling."
        )
    )
    parser.add_argument(
        "--input", type=Path, default=DEFAULT_INPUT_PATH,
        help=f"Raw input CSV. Defaults to {DEFAULT_INPUT_PATH}",
    )
    parser.add_argument(
        "--sessions-output", type=Path, default=DEFAULT_SESSIONS_PATH,
        help=f"Intermediate sessions CSV (no scores). Defaults to {DEFAULT_SESSIONS_PATH}",
    )
    parser.add_argument(
        "--output", type=Path, default=DEFAULT_OUTPUT_PATH,
        help=f"Final scored sessions CSV. Defaults to {DEFAULT_OUTPUT_PATH}",
    )
    parser.add_argument(
        "--session-gap", type=int, default=SESSION_GAP_MINUTES,
        help=f"Session gap in minutes. Defaults to {SESSION_GAP_MINUTES}.",
    )
    parser.add_argument(
        "--seed", type=int, default=RANDOM_STATE,
        help=f"Random seed. Defaults to {RANDOM_STATE}.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print(f"Reading raw data: {args.input}")
    df = pd.read_csv(args.input, low_memory=False)
    print(f"  Raw rows: {len(df):,}")

    print(f"\nStage 1 — Linearizing sessions (gap = {args.session_gap} min) ...")
    sessions_df = linearize_sessions(df, session_gap_minutes=args.session_gap)
    print(f"  Sessions produced: {len(sessions_df):,}")
    print(f"  Avg readings/session: {sessions_df['n_readings'].mean():.1f}")
    print(f"  Avg duration (min):   {sessions_df['session_duration_minutes'].mean():.1f}")
    _overwrite_csv(sessions_df, args.sessions_output)
    print(f"  Saved sessions → {args.sessions_output}")

    print("\nStage 2 — Scoring sessions with persona profiles ...")
    scored_df, summary = score_sessions(sessions_df, random_state=args.seed)

    drop_cols = ["session_id", "source", "location_id", "session_start", "session_end", "n_readings"]
    export_df = scored_df.drop(columns=drop_cols, errors="ignore")
    
    _overwrite_csv(export_df, args.output)
    print(f"  Saved scored sessions → {args.output}")

    score_dist = scored_df["focus_score"].value_counts().sort_index()
    print(f"\nFocus score distribution:\n{score_dist.to_string()}")
    print(f"\nProfile summary:\n{summary[['profile_name', 'sessions_scored']].to_string(index=False)}")


if __name__ == "__main__":
    main()
