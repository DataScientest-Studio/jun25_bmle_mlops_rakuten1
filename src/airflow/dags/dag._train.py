"""
DAG Airflow : Entraînement hebdomadaire du modèle Rakuten
Ce DAG appelle l'API FastAPI du service "trainer" afin
de lancer l'entraînement du modèle une fois par semaine, chaque lundi à 4h.
"""

import logging
from datetime import datetime, timedelta

import requests
from airflow.operators.python import PythonOperator

from airflow import DAG


def log_hello():
    logging.getLogger("airflow.task").info("DAG hebdo bien lancé ✅")


default_args = {
    "owner": "rakuten",
    "retries": 2,
    "retry_delay": timedelta(minutes=1),
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


with DAG(
    dag_id="rakuten_weekly_training",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule_interval="0 4 * * 1",  # Tous les lundis à 4h du matin
    catchup=False,
    tags=["rakuten", "training", "weekly"],
) as dag:
    get_token_task = PythonOperator(task_id="get_token_task", python_callable=get_token)
    call_api_task = PythonOperator(task_id="call_api_task", python_callable=call_api)

    get_token_task >> call_api_task
