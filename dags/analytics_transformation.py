import pendulum

from airflow.sdk import DAG, task

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

    run_analytics_transformation()