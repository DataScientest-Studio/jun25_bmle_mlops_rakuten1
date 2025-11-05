FROM mongo:7.0

LABEL maintainer="MLOps Rakuten Team"
LABEL description="MongoDB NoSQL Database pour MLOps Rakuten"

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
