# Data

- `raw/`: imported datasets exactly as received, plus database exports such as `environment_history_realdata.csv`.
- `interim/`: temporary cleaned or merged datasets that are not ready for training.
- `processed/`: model-ready datasets. The current training entry point reads `processed/focus_dataset.csv`.
- `mock/legacy/`: old synthetic data retained for reference only.

