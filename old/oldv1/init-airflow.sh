#!/bin/bash
set -e

echo "=========================================="
echo "Airflow Initialization - MLOps Rakuten"
echo "=========================================="

# Attendre que PostgreSQL soit prêt
echo "Waiting for PostgreSQL..."
until pg_isready -h airflow-postgres -p 5432 -U airflow; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "PostgreSQL is up - initializing Airflow"

# Initialiser la base de données Airflow
airflow db upgrade

# Créer l'utilisateur admin si nécessaire
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@mlops-rakuten.com \
    --password admin 2>/dev/null || echo "Admin user already exists"

echo "Airflow initialization completed!"
echo "=========================================="
