import pendulum

from airflow.sdk import DAG, task

from src.quality.quality_runner import run_analytics_quality_checks
from src.transform.transform_analytics import transform_analytics


with DAG(
    dag_id="analytics_transformation",
    description="Transform CORE data into the business-ready ANALYTICS layer",
    start_date=pendulum.datetime(
        2026,
        1,
        1,
        tz="Europe/Paris",
    ),
    schedule=None,
    catchup=False,
    tags=[
        "global-flight-data",
        "analytics",
        "transformation",
    ],
) as dag:

    @task(task_id="transform_core_to_analytics")
    def run_analytics_transformation() -> None:
        """Execute the CORE to ANALYTICS transformation."""
        transform_analytics()

    @task(task_id="validate_analytics_quality")
    def run_analytics_quality_validation() -> None:
        """Execute standalone ANALYTICS Data Quality checks."""
        run_analytics_quality_checks()

    transform_task = run_analytics_transformation()
    quality_task = run_analytics_quality_validation()

    transform_task >> quality_task