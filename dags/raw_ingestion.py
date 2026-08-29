from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator

from src.ingestion.ingest_ourairports import DATASETS, ingest_dataset
from src.monitoring.airflow_callbacks import (
    log_task_failure,
    log_task_retry,
)


DEFAULT_ARGS = {
    "on_failure_callback": log_task_failure,
    "on_retry_callback": log_task_retry,
}


def ingest_all_ourairports_datasets() -> None:
    """Ingest all OurAirports datasets into the RAW layer."""
    for dataset_name in DATASETS:
        ingest_dataset(dataset_name)


with DAG(
    dag_id="raw_ingestion",
    description="Ingest OurAirports datasets into the RAW layer",
    schedule=None,
    start_date=datetime(
        2026,
        1,
        1,
        tzinfo=ZoneInfo("Europe/Paris"),
    ),
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["global-flight-data", "raw", "ingestion"],
) as dag:

    ingest_raw = PythonOperator(
        task_id="ingest_ourairports_raw",
        python_callable=ingest_all_ourairports_datasets,
        retries=2,
        retry_delay=timedelta(minutes=5),
        execution_timeout=timedelta(minutes=30),
    )
