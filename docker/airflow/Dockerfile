FROM apache/airflow:2.8.0-python3.11

LABEL maintainer="MLOps Rakuten Team"
LABEL description="Airflow for ML Workflow Orchestration"

USER root

# Installation des dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Copier et installer uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copier pyproject.toml et installer les dépendances
COPY --chown=airflow:root pyproject.toml README.md ./

# Installation avec les extras corrects (RÉPÉTER --extra)
RUN uv pip install --system --no-cache \
    --extra airflow \
    --extra database \
    --extra mlflow-client \
    .

# Copier les DAGs
COPY --chown=airflow:root airflow/dags /opt/airflow/dags

# Copier le script d'initialisation custom
COPY --chown=airflow:root docker/airflow/init-airflow.sh /opt/airflow/init-airflow.sh
RUN chmod +x /opt/airflow/init-airflow.sh

# L'entrypoint de base d'Airflow est conservé
# On utilise init-airflow.sh comme script de pré-démarrage via docker-compose
