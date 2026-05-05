FROM python:3.12-slim

WORKDIR /mal

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY data ./data
COPY ml_pipeline ./ml_pipeline
COPY scripts ./scripts
RUN python scripts/train_model.py

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
