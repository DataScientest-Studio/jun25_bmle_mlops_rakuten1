FROM python:3.11-slim

LABEL maintainer="MLOps Rakuten Team"
LABEL description="MLflow Tracking Server"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copier et installer uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copier pyproject.toml et installer les dépendances
COPY pyproject.toml README.md ./

# Installation avec les extras corrects (RÉPÉTER --extra)
RUN uv pip install --system --no-cache .[mlflow,database]

# Créer un utilisateur non-root
RUN useradd -m -u 1000 mlflow && \
    mkdir -p /app/mlruns && \
    chown -R mlflow:mlflow /app
USER mlflow

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

EXPOSE 5000

# Script d'entrée pour attendre la base de données
COPY docker/mlflow/entrypoint.sh /entrypoint.sh
USER root
RUN chmod +x /entrypoint.sh
USER mlflow

ENTRYPOINT ["/entrypoint.sh"]
CMD ["mlflow", "server", \
     "--host", "0.0.0.0", \
     "--port", "5000", \
     "--backend-store-uri", "${MLFLOW_BACKEND_STORE_URI}", \
     "--default-artifact-root", "${MLFLOW_ARTIFACT_ROOT}"]
