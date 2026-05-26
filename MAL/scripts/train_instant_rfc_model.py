import sys
from pathlib import Path

MAL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(MAL_DIR))

from ml_pipeline.instant_model import (
    INSTANT_FEATURE_COLUMNS,
    load_instant_dataset,
    save_instant_model,
    save_instant_scaler,
    train_instant_model_artifacts,
)


def main() -> None:
    df = load_instant_dataset()
    model, scaler = train_instant_model_artifacts(df)
    model_path = save_instant_model(model)
    scaler_path = save_instant_scaler(scaler)

    print(f"Saved Instant RFC model to {model_path}")
    print(f"Saved instant scaler to {scaler_path}")
    print(f"Trained on {len(df):,} rows with features {INSTANT_FEATURE_COLUMNS}")


if __name__ == "__main__":
    main()
