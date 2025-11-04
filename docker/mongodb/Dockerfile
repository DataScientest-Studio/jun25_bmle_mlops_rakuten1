FROM mongo:7.0

LABEL maintainer="MLOps Rakuten Team"
LABEL description="MongoDB NoSQL Database pour MLOps Rakuten"

# Installer Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier et installer uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copier pyproject.toml pour installer les dépendances database
COPY pyproject.toml README.md ./

# Installer uniquement les dépendances database (pymongo, motor, beanie)
RUN uv pip install --system --no-cache \
    --extra database \
    .

# Copier les scripts d'initialisation
COPY docker/mongodb/init-mongodb.sh /docker-entrypoint-initdb.d/01-init.sh
COPY docker/mongodb/setup-database.py /docker-entrypoint-initdb.d/02-setup.py
COPY docker/mongodb/indexes.json /docker-entrypoint-initdb.d/indexes.json

# Copier la configuration MongoDB
COPY docker/mongodb/mongodb.yaml /etc/mongod.conf

# Rendre les scripts exécutables
RUN chmod +x /docker-entrypoint-initdb.d/01-init.sh
RUN chmod +x /docker-entrypoint-initdb.d/02-setup.py

# Créer le répertoire pour les logs MongoDB
RUN mkdir -p /var/log/mongodb && \
    chown -R mongodb:mongodb /var/log/mongodb

EXPOSE 27017
