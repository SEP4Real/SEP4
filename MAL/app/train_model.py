from .model import (
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

    validation_model = build_model()
    validation_model.fit(x_train, y_train)
    validation_metrics = evaluate_model(validation_model, x_validation, y_validation)
    test_metrics = evaluate_model(validation_model, x_test, y_test)

    print(
        "RandomForest validation metrics: "
        f"accuracy={validation_metrics['accuracy']:.3f}, macro_f1={validation_metrics['macro_f1']:.3f}"
    )
    print(
        "RandomForest test metrics: "
        f"accuracy={test_metrics['accuracy']:.3f}, macro_f1={test_metrics['macro_f1']:.3f}"
    )

    model = train_model(df)
    model_path = save_model(model)
    x, _ = split_features_target(df)
    print(f"Saved RandomForest model to {model_path}")
    print(f"Trained final model on {len(x)} rows")


if __name__ == "__main__":
    main()
