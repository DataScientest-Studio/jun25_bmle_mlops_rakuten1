FROM python:3.11-slim

LABEL maintainer="MLOps Rakuten Team"
LABEL description="FastAPI Application with OAuth2 Authentication"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # Configure uv pour utiliser le système directement ou un chemin fixe
    UV_SYSTEM_PYTHON=1

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier et installer uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 1. Copier les fichiers de définition de projet
COPY pyproject.toml uv.lock ./

# 2. Copier le code source (nécessaire pour installer le projet lui-même)
COPY src/ /app/src/

# 3. Installation avec uv sync
# --frozen : s'assure qu'on utilise exactement les versions du uv.lock
# --no-install-project : si vous vouliez installer juste les deps (mais ici on veut tout)
# --extra : pour activer vos groupes optionnels
RUN uv sync --frozen --no-cache \
    --extra api \
    --extra database \
    --extra etl

# Note : uv sync installe par défaut dans .venv
# Il faut donc s'assurer que le PATH est à jour pour la suite
ENV PATH="/app/.venv/bin:$PATH"

# Créer un utilisateur non-root
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Plus besoin de 'uv run', car on a mis le venv dans le PATH
CMD ["uvicorn", "src.api.api:api", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
