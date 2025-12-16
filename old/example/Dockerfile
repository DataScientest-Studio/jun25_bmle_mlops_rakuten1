FROM python:3.11-slim

LABEL maintainer="MLOps Rakuten Team"
LABEL description="Example image"

# Repertoire de base/travail sur le container
WORKDIR /app

# Copier et installer uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copier la configuration pour uv et le code source
COPY pyproject.toml ./
COPY src/ /app/src/

# Installation en mode éditable avec l'extra example
# l'extra doit avoir été defini dans pyproject.toml
RUN uv pip install --system --no-cache -e .[example]

# Créer un utilisateur non-root
RUN useradd -m -u 1000 mluser && \
    chown -R mluser:mluser /app
USER mluser

# Lancer un script un fichier.py
CMD ["python", "src/example/un_fichier.py"]
