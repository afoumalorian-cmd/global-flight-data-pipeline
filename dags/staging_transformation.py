from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator

from src.quality.quality_runner import run_staging_quality_checks
from src.transform.transform_ourairports import transform_ourairports
from src.monitoring.airflow_callbacks import (
    log_task_failure,
    log_task_retry,
)


DEFAULT_ARGS = {
    "on_failure_callback": log_task_failure,
    "on_retry_callback": log_task_retry,
}


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
    default_args=DEFAULT_ARGS,
    tags=["global-flight-data", "staging", "transformation"],
) as dag:

    transform_staging = PythonOperator(
        task_id="transform_raw_to_staging",
        python_callable=transform_ourairports,
        retries=2,
        retry_delay=timedelta(minutes=5),
        execution_timeout=timedelta(minutes=20),
    )

    validate_staging_quality = PythonOperator(
        task_id="validate_staging_quality",
        python_callable=run_staging_quality_checks,
        execution_timeout=timedelta(minutes=10),
    )

    transform_staging >> validate_staging_quality
