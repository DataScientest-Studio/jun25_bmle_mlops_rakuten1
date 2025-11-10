FROM python:3.11-slim

LABEL maintainer="Rakuten MLOps Team"
LABEL description="Container pour l'entraînement du modèle XGBoost multimodal"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    libgl1 \
    libsm6 \
    libxext6 \
    libxrender-dev \
 && rm -rf /var/lib/apt/lists/*

COPY requirements-train.txt .
RUN pip install --no-cache-dir -r requirements-train.txt

COPY src ./src

RUN mkdir -p /app/data/models /app/mlruns

ENV PYTHONPATH=/app/src
ENV MLFLOW_TRACKING_URI=file:/app/mlruns

CMD ["python", "-m", "train.train"]
