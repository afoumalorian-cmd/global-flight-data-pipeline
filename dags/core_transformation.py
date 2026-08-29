from datetime import timedelta

import pendulum

from airflow.sdk import DAG, task

from src.quality.quality_runner import run_core_quality_checks
from src.transform.transform_core import transform_core
from src.monitoring.airflow_callbacks import (
    log_task_failure,
    log_task_retry,
)


DEFAULT_ARGS = {
    "on_failure_callback": log_task_failure,
    "on_retry_callback": log_task_retry,
}

with DAG(
    dag_id="core_transformation",
    description="Transform STAGING data into the trusted CORE layer",
    start_date=pendulum.datetime(
        2026,
        1,
        1,
        tz="Europe/Paris",
    ),
    schedule=None,
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=[
        "global-flight-data",
        "core",
        "transformation",
    ],
) as dag:

    @task(
        task_id="transform_staging_to_core",
        retries=2,
        retry_delay=timedelta(minutes=5),
        execution_timeout=timedelta(minutes=20),
    )
    def run_core_transformation() -> None:
        """Execute the STAGING to CORE transformation."""
        transform_core()

    @task(
        task_id="validate_core_quality",
        execution_timeout=timedelta(minutes=10),
    )
    def run_core_quality_validation() -> None:
        """Execute standalone CORE Data Quality checks."""
        run_core_quality_checks()

    transform_task = run_core_transformation()
    quality_task = run_core_quality_validation()

    transform_task >> quality_task
