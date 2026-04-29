from .model import save_model, train_model


def main() -> None:
    model = train_model()
    model_path = save_model(model)
    print(f"Saved RandomForest model to {model_path}")


if __name__ == "__main__":
    main()
