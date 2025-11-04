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
COPY pyproject.toml README.md ./

# Installation avec les extras corrects (RÉPÉTER --extra)
RUN uv pip install --system --no-cache  .[datascience,database,mlflow-client]

# Créer les répertoires pour les données et modèles
RUN mkdir -p /app/data/raw /app/data/preprocessed /app/data/processed /app/models /app/notebooks

# Copier le code source
COPY ./src ./src

# Créer un utilisateur non-root
RUN useradd -m -u 1000 mluser && \
    chown -R mluser:mluser /app
USER mluser

# Point d'entrée par défaut
CMD ["python", "-m", "src.ml.train"]
