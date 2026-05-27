import sys
from pathlib import Path

MAL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(MAL_DIR))

from sklearn.preprocessing import StandardScaler
from ml_pipeline.model import (
    build_model,
    evaluate_model,
    load_dataset,
    save_model,
    split_features_target,
    train_model,
    train_validation_test_split,
)


def main() -> None:
    df = load_dataset()
    x_train, x_validation, x_test, y_train, y_validation, y_test = train_validation_test_split(df)

    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(x_train)
    x_validation_scaled = scaler.transform(x_validation)
    x_test_scaled = scaler.transform(x_test)

    validation_model = build_model()
    validation_model.fit(x_train_scaled, y_train)
    validation_metrics = evaluate_model(validation_model, x_validation_scaled, y_validation)
    test_metrics = evaluate_model(validation_model, x_test_scaled, y_test)

    print(
        "MLPClassifier validation metrics: "
        f"accuracy={validation_metrics['accuracy']:.3f}, macro_f1={validation_metrics['macro_f1']:.3f}"
    )
    print(
        "MLPClassifier test metrics: "
        f"accuracy={test_metrics['accuracy']:.3f}, macro_f1={test_metrics['macro_f1']:.3f}"
    )

    model, final_scaler = train_model(df)
    model_path = save_model(model, final_scaler)
    x, _ = split_features_target(df)
    print(f"Saved MLPClassifier model & scaler to {model_path}")
    print(f"Trained final model on {len(x)} rows")


if __name__ == "__main__":
    main()
