FROM apache/airflow:2.11.0

# Passer en root si tu veux installer des paquets système
# USER root

# Exemple: paquets OS optionnels
# RUN apt-get update && \
#     apt-get install -y --no-install-recommends vim && \
#     apt-get clean && rm -rf /var/lib/apt/lists/*

# Revenir à l’utilisateur airflow (obligatoire pour Airflow)
USER airflow

# Installer des dépendances Python supplémentaires
# (tu peux aussi utiliser requirements.txt si tu préfères)
RUN pip install --no-cache-dir pymongo