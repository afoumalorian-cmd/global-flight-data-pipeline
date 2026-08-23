from datetime import datetime
from zoneinfo import ZoneInfo

from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator

from src.ingestion.ingest_ourairports import DATASETS, ingest_dataset


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
    tags=["global-flight-data", "raw", "ingestion"],
) as dag:

    ingest_raw = PythonOperator(
        task_id="ingest_ourairports_raw",
        python_callable=ingest_all_ourairports_datasets,
    )