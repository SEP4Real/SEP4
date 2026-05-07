FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# rf_model.pkl is committed to the repo and copied in above. Retraining at
# build time is expensive and unnecessary — train locally with
# `python -m app.train_model` from MAL/ and commit the new artifact.

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
