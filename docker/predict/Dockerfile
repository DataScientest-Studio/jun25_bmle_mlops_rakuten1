FROM python:3.11-slim

LABEL maintainer="MLOps Rakuten Team"
LABEL description="ML Worker for Training and Preprocessing"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TORCH_HOME=/app/.cache/torch \
    HF_HOME=/app/.cache/huggingface

WORKDIR /app

# Installation des dépendances système pour PyTorch et traitement d'images
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Copier et installer uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copier pyproject.toml et installer les dépendances
COPY pyproject.toml ./

# Copier le code source
COPY src/ /app/src/

# Installation avec les extras corrects (RÉPÉTER --extra)
RUN uv pip install --system --no-cache -e .[etl,datascience,database,mlflow,api]

# Créer les répertoires pour les données et modèles
RUN mkdir -p /app/data/raw /app/data/preprocessed /app/data/processed /app/models /app/notebooks

# Point d'entrée par défaut
ENV PYTHONPATH=/app/src
CMD ["uvicorn", "api.predict_api:prediction", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
