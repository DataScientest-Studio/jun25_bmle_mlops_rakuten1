FROM python:3.11-slim

WORKDIR /app

# Copier et installer uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copier pyproject.toml et installer les dépendances
COPY ../../pyproject.toml ./

# Installation avec les extras corrects (RÉPÉTER --extra)
RUN uv pip install --system --no-cache .[etl]

COPY ./src/data/clean_data.py ./src/data/clean_text.py /app/

# Créer un utilisateur non-root
RUN useradd -m -u 1000 mluser && \
    chown -R mluser:mluser /app
USER mluser

# Lancer le script avec imports absolus
CMD ["python", "src/data/clean_data.py"]
