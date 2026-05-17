# MAL

Machine Learning and API service for the project.

## Folder layout

- `backend/app/` contains the FastAPI backend only.
- `ml_pipeline/` contains reusable model, training, and transformation code.
- `scripts/` contains runnable entry points for local or Docker workflows.
- `data/raw/` is for imported source datasets and database exports.
- `data/interim/` is for temporary merge/cleaning outputs.
- `data/processed/` is for model-ready datasets.
- `data/mock/legacy/` contains the old synthetic data and generators. Keep it out of normal training once real datasets arrive.
- `models/` contains trained model artifacts such as `rf_model.pkl`.
- `notebooks/` contains exploratory notebooks.
- `tests/` contains automated and HTTP request tests.

## Common commands

Run from `MAL/`:

```bash
python scripts/train_model.py
uvicorn backend.app.main:app --reload
pytest
```

