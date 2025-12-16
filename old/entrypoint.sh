#!/bin/bash
set -e

# Attendre que PostgreSQL soit prêt
echo "Waiting for PostgreSQL..."
until pg_isready -h postgres -p 5432 -U mlflow; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "PostgreSQL is up - starting MLflow server"

# Initialiser la base de données MLflow
mlflow db upgrade ${MLFLOW_BACKEND_STORE_URI}

# Exécuter la commande passée en argument
exec "$@"
