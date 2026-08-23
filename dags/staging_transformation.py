from datetime import datetime
from zoneinfo import ZoneInfo

from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator

from src.transform.transform_ourairports import transform_ourairports


with DAG(
    dag_id="staging_transformation",
    description="Transform OurAirports data from RAW to STAGING",
    schedule=None,
    start_date=datetime(
        2026,
        1,
        1,
        tzinfo=ZoneInfo("Europe/Paris"),
    ),
    catchup=False,
    tags=["global-flight-data", "staging", "transformation"],
) as dag:

    transform_staging = PythonOperator(
        task_id="transform_raw_to_staging",
        python_callable=transform_ourairports,
    )