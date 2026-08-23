import pendulum

from airflow.sdk import DAG, task

from src.transform.transform_core import transform_core


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
    tags=[
        "global-flight-data",
        "core",
        "transformation",
    ],
) as dag:

    @task(task_id="transform_staging_to_core")
    def run_core_transformation() -> None:
        """Execute the STAGING to CORE transformation."""
        transform_core()

    run_core_transformation()