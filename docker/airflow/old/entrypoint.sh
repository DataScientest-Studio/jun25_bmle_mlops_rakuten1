#!/bin/bash
set -e

# Attendre PostgreSQL
echo "Waiting for PostgreSQL..."
until pg_isready -h airflow-postgres -p 5432 -U airflow; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "PostgreSQL is up"

# Initialiser la base de données Airflow (une seule fois)
if [ "$1" = "webserver" ]; then
    airflow db init
    airflow users create \
        --username admin \
        --firstname Admin \
        --lastname User \
        --role Admin \
        --email admin@example.com \
        --password admin || true
fi

# Exécuter la commande Airflow
exec airflow "$@"
