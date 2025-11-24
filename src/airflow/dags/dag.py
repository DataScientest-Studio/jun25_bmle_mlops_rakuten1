"""
DAG Airflow : Entraînement quotidien du modèle Rakuten
Ce DAG appelle l'API FastAPI du service "trainer" afin
de lancer l'entraînement du modèle tous les jours à 7h.
Le DAG utilise un token JWT stocké dans les Variables Airflow :
Menu Airflow -> Admin -> Variables -> clé : TRAIN_JWT
Le service "trainer" doit être joignable via http://trainer:8000/train
(nom du service Docker, pas localhost)
"""

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.models import Variable
from datetime import datetime, timedelta

"""
Arguments par défaut des tâches
"""
default_args = {
    "owner": "rakuten",  # Nom du propriétaire du DAG
    "retries": 1,  # Nombre de réessais en cas d'échec
    "retry_delay": timedelta(minutes=5),  # Délai entre 2 tentatives
}

"""
Définition du DAG
"""
with DAG(
    dag_id="rakuten_daily_training",  # Nom unique du DAG
    default_args=default_args,
    start_date=datetime(2025, 1, 1),  # Date de début (doit être passée)
    schedule_interval="0 7 * * *",  # Tous les jours à 7h
    catchup=False,  # Ne pas exécuter les runs du passé
) as dag:
    """
    Récupération du token JWT depuis les Variables Airflow
    (UI -> Admin -> Variables -> TRAIN_JWT)
    """
    token = Variable.get("TRAIN_JWT")

    #
    # Tâche : appel HTTP au service trainer via curl
    # Lance l'entraînement du modèle via l'endpoint /train
    #
    train_model = BashOperator(
        task_id="trigger_training",  # Nom interne de la tâche
        bash_command=(f"curl -X POST http://trainer:8000/train -H 'Authorization: Bearer {token}'"),
    )

    # On ne définit pas d'autres tâches : execution = train_model
    train_model
