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
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta
import logging
import requests


def log_hello():
    logging.getLogger("airflow.task").info("DAG bien lancé ✅")


"""
Arguments par défaut des tâches
"""
default_args = {
    "owner": "rakuten",  # Nom du propriétaire du DAG
    "retries": 2,  # Nombre de réessais en cas d'échec
    "retry_delay": timedelta(minutes=1),  # Délai entre 2 tentatives
}


def get_token():
    url_token = "http://trainer:8000/login"
    response = requests.post(url_token, headers={"Authorization": "Bearer user:rakuten_project"})
    response.raise_for_status()
    token = response.json().get("token")
    return token


def call_api(ti):
    token = ti.xcom_pull(task_ids="get_token_task")
    url_api = "http://trainer:8000/train"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(url_api, headers=headers)
    response.raise_for_status()
    print(response.json())


"""
Définition du DAG
"""
with DAG(
    dag_id="rakuten_daily_training",  # Nom unique du DAG
    default_args=default_args,
    start_date=datetime(2025, 1, 1),  # Date de début (doit être passée)
    schedule_interval="0 10 * * *",  # Tous les jours à 7h
    catchup=False,  # Ne pas exécuter les runs du passé
) as dag:
    """
    Récupération du token JWT depuis les Variables Airflow
    (UI -> Admin -> Variables -> TRAIN_JWT)
    """
    #    token = Variable.get("TRAIN_JWT")

    #
    # Tâche : appel HTTP au service trainer via curl
    # Lance l'entraînement du modèle via l'endpoint /train
    #
    #    train_model = BashOperator(
    #        task_id="trigger_training",  # Nom interne de la tâche
    #        bash_command=(f"curl -X POST http://trainer:8000/train -H 'Authorization: Bearer {token}'"),
    #    )

    # On ne définit pas d'autres tâches : execution = train_model
    #    train_model
    # print("toto")
    # toto = PythonOperator(
    #    task_id="hello_task",
    #    python_callable=log_hello,
    # )

    get_token_task = PythonOperator(task_id="get_token_task", python_callable=get_token)

    call_api_task = PythonOperator(task_id="call_api_task", python_callable=call_api)

    get_token_task >> call_api_task
