FROM python:3.11-slim

LABEL maintainer="MLOps Rakuten Team"
LABEL description="Data Preprocessing Worker"

WORKDIR /app

# Copier et installer uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copier la configuration et le code source
COPY pyproject.toml ./
COPY src/ /app/src/

# Installation en mode éditable avec l'extra etl
RUN uv pip install --system --no-cache -e .[etl]

# Créer un utilisateur non-root
RUN useradd -m -u 1000 mluser && \
    chown -R mluser:mluser /app
USER mluser

# Lancer le script de nettoyage
CMD ["python", "src/data/preprocess_data.py"]
