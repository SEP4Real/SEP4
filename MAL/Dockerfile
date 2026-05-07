FROM python:3.12-slim

WORKDIR /mal

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY ml_pipeline ./ml_pipeline
COPY models ./models

# rf_model.pkl is committed to the repo and copied in above. Retraining at
# build time is expensive and unnecessary — train locally with
# `python scripts/train_model.py` from MAL/ and commit the new artifact.

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
