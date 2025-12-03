from airflow import DAG
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.models import DagRun
from airflow.utils.state import State
from airflow.utils.session import provide_session
from datetime import datetime, timedelta
import logging
import os
import pandas as pd
import sys
import json

sys.path.append("/app")
from evidently import ColumnMapping
from evidently.metrics import (
    ColumnDriftMetric,
    DatasetDriftMetric,
    TextDescriptorsDriftMetric,
)
from evidently.report import Report

from src.data.clean_data import calcul_lignes_a_lire, clean_text


default_args = {
    "owner": "rakuten",
    "retries": 2,
    "retry_delay": timedelta(minutes=1),
}


@provide_session
def get_last_successful_training_date(dag_id="rakuten_weekly_training", session=None):
    last_run = (
        session.query(DagRun)
        .filter(
            DagRun.dag_id == dag_id,
            DagRun.state == State.SUCCESS,
        )
        .order_by(DagRun.start_date.desc())
        .first()
    )
    if last_run:
        return last_run.start_date.strftime("%Y-%m-%d")
    else:
        return None


def load_data_partial(input_path, n_lignes):
    df = pd.read_csv(input_path, nrows=n_lignes)
    return df


def cleaning_texts_only(df):
    df["title_clean"] = df["designation"].apply(clean_text).replace("", " ")
    df["description_clean"] = df["description"].apply(clean_text).replace("", " ")
    return df[["title_clean", "description_clean"]]


def generate_datasets(date_ref, date_curr, input_path):
    n_ref = calcul_lignes_a_lire(date_ref)
    n_curr = calcul_lignes_a_lire(date_curr)
    df_ref_raw = load_data_partial(input_path, n_ref)
    reference_df = cleaning_texts_only(df_ref_raw)

    df_curr_raw = load_data_partial(input_path, n_curr)
    current_df = cleaning_texts_only(df_curr_raw)

    return reference_df, current_df


def run_drift_monitoring(**context):
    input_dir = "/app/data/raw"
    input_path = os.path.join(input_dir, "X_train_update.csv")
    date_run = context["ds"]

    date_reference = get_last_successful_training_date()

    if date_reference is None:
        date_reference = "2025-01-01"
        logging.warning("Aucune date d'entraînement trouvée, fallback sur 2025-01-01")

    logging.info(f"🚀 Drift monitoring : référence = {date_reference}, courant = {date_run}")

    reference_data, current_data = generate_datasets(date_reference, date_run, input_path)

    column_mapping = ColumnMapping()
    column_mapping.numerical_columns = []
    column_mapping.categorical_columns = []
    column_mapping.text_features = ["title_clean", "description_clean"]

    report = Report(
        metrics=[
            DatasetDriftMetric(),
            ColumnDriftMetric(column_name="title_clean", stattest_threshold=0.45),
            ColumnDriftMetric(column_name="description_clean", stattest_threshold=0.45),
            TextDescriptorsDriftMetric(column_name="title_clean"),
            TextDescriptorsDriftMetric(column_name="description_clean"),
        ]
    )

    report.run(
        reference_data=reference_data, current_data=current_data, column_mapping=column_mapping
    )

    # Récupérer les résultats des métriques
    results = report.as_dict()

    metrics_results = results.get("metrics", [])

    def safe_get_drift(index):
        try:
            metric_result = metrics_results[index]["result"]
            return metric_result.get("drift_detected", False)
        except (IndexError, KeyError, TypeError):
            logging.warning(f"Impossible de lire drift_detected à l'index {index}")
            return False

    dataset_drift = safe_get_drift(0)  # DatasetDriftMetric
    title_drift = safe_get_drift(1)  # ColumnDriftMetric title_clean
    desc_drift = safe_get_drift(2)  # ColumnDriftMetric description_clean
    title_desc_drift = safe_get_drift(3)  # TextDescriptorsDriftMetric title_clean
    desc_desc_drift = safe_get_drift(4)  # TextDescriptorsDriftMetric description_clean

    logging.info(f"📊 Dataset drift: {dataset_drift}")
    logging.info(f"📊 Title drift: {title_drift}")
    logging.info(f"📊 Description drift: {desc_drift}")
    logging.info(f"📊 Title descriptors drift: {title_desc_drift}")
    logging.info(f"📊 Description descriptors drift: {desc_desc_drift}")

    drift_detected = any(
        [dataset_drift, title_drift, desc_drift, title_desc_drift, desc_desc_drift]
    )

    logging.info(f"🚨 Drift global détecté: {drift_detected}")

    # Sauvegarde HTML
    output_dir = "/app/reports/evidently_reports"
    os.makedirs(output_dir, exist_ok=True)
    html_path = f"{output_dir}/drift_report_{date_run}.html"
    report.save_html(html_path)
    logging.info(f"✅ Rapport HTML sauvegardé : {html_path}")

    return drift_detected


def decide_trigger(**context):
    drift = context["ti"].xcom_pull(task_ids="data_drift_monitoring")
    if drift:
        return "trigger_rakuten_weekly_training"
    else:
        return "no_trigger"


with DAG(
    dag_id="rakuten_data_drift_monitoring",
    default_args=default_args,
    description="Monitoring drift avec vocab titres et descriptions",
    start_date=datetime(2025, 1, 1),
    schedule_interval="0 8 * * *",
    catchup=False,
    tags=["mlops", "drift"],
) as dag:
    drift_task = PythonOperator(
        task_id="data_drift_monitoring",
        python_callable=run_drift_monitoring,
        provide_context=True,
    )

    trigger_retrain = TriggerDagRunOperator(
        task_id="trigger_rakuten_weekly_training",
        trigger_dag_id="rakuten_weekly_training",
        wait_for_completion=False,
        reset_dag_run=True,
        execution_date="{{ ds }}",
    )

    dummy_no_trigger = DummyOperator(task_id="no_trigger")

    decide_task = BranchPythonOperator(
        task_id="branch_decision",
        python_callable=decide_trigger,
    )

    drift_task >> decide_task
    decide_task >> [trigger_retrain, dummy_no_trigger]
