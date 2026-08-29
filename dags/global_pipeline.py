from datetime import datetime
from zoneinfo import ZoneInfo

from airflow.sdk import DAG
from airflow.providers.standard.operators.trigger_dagrun import (
    TriggerDagRunOperator,
)

from src.monitoring.airflow_callbacks import log_task_failure


DEFAULT_ARGS = {
    "on_failure_callback": log_task_failure,
}


with DAG(
    dag_id="global_pipeline",
    description="Orchestrate the complete Global Flight Data Pipeline",
    schedule="0 2 * * *",
    start_date=datetime(
        2026,
        1,
        1,
        tzinfo=ZoneInfo("Europe/Paris"),
    ),
    catchup=False,
    max_active_runs=1,
    default_args=DEFAULT_ARGS,
    tags=["global-flight-data", "pipeline", "orchestration"],
) as dag:

    trigger_raw_ingestion = TriggerDagRunOperator(
        task_id="trigger_raw_ingestion",
        trigger_dag_id="raw_ingestion",
        wait_for_completion=True,
        allowed_states=["success"],
        failed_states=["failed"],
        poke_interval=10,
    )

    trigger_staging_transformation = TriggerDagRunOperator(
        task_id="trigger_staging_transformation",
        trigger_dag_id="staging_transformation",
        wait_for_completion=True,
        allowed_states=["success"],
        failed_states=["failed"],
        poke_interval=10,
    )

    trigger_core_transformation = TriggerDagRunOperator(
        task_id="trigger_core_transformation",
        trigger_dag_id="core_transformation",
        wait_for_completion=True,
        allowed_states=["success"],
        failed_states=["failed"],
        poke_interval=10,
    )

    trigger_analytics_transformation = TriggerDagRunOperator(
        task_id="trigger_analytics_transformation",
        trigger_dag_id="analytics_transformation",
        wait_for_completion=True,
        allowed_states=["success"],
        failed_states=["failed"],
        poke_interval=10,
    )

    (
        trigger_raw_ingestion
        >> trigger_staging_transformation
        >> trigger_core_transformation
        >> trigger_analytics_transformation
    )