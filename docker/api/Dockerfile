FROM python:3.11-slim

LABEL maintainer="MLOps Rakuten Team"
LABEL description="FastAPI Application with OAuth2 Authentication"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier et installer uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copier pyproject.toml et installer les dépendances
COPY pyproject.toml README.md ./

# Installation avec les extras corrects (RÉPÉTER --extra)
RUN uv pip install --system --no-cache \
    --extra api \
    --extra database \
    --extra monitoring \
    --extra mlflow-client \
    .

# Copier le code source
COPY ./src ./src

# Créer un utilisateur non-root
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "src.master:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
