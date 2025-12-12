FROM python:3.11-slim

LABEL maintainer="MLOps Rakuten Team"
LABEL description="Test Container (System Install)"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # Ajout explicite du dossier courant au PYTHONPATH pour trouver vos modules
    PYTHONPATH=/app

WORKDIR /app

# Installation système minimale
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copie de uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 1. Copie des fichiers de définition
COPY pyproject.toml uv.lock ./

# 2. Installation SYSTEM-WIDE (Sans venv)
# On exporte le lockfile en format requirements et on l'installe directement
# --extra api,database,etl : pour inclure vos groupes optionnels
# --system : installe dans le python global du conteneur
RUN uv pip install --system --no-cache \
    -r pyproject.toml \
    --extra api \
    --extra database \
    --extra etl \
    --extra mlflow \
    --extra dev

# 3. Copie du code source
COPY src/ /app/src/
COPY tests/api/fixtures/X_test_sample.csv /app/data/raw/X_test_update.csv
COPY tests/api/fixtures/image_482661_product_929337.jpg /app/data/raw/images/images/image_test/image_482661_product_929337.jpg

# Création utilisateur non-root (Sécurité)
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

EXPOSE 8000

# Lancement direct (uvicorn est maintenant dans le PATH global par défaut)
CMD ["uvicorn", "src.api.predict_api:prediction", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]
