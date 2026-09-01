"""Tests for Airflow DAG task structure and dependencies."""

import pytest


EXPECTED_TASK_IDS = {
    "raw_ingestion": {"ingest_ourairports_raw"},
    "staging_transformation": {
        "transform_raw_to_staging",
        "validate_staging_quality",
    },
    "core_transformation": {
        "transform_staging_to_core",
        "validate_core_quality",
    },
    "analytics_transformation": {
        "transform_core_to_analytics",
        "validate_analytics_quality",
    },
    "global_pipeline": {
        "trigger_raw_ingestion",
        "trigger_staging_transformation",
        "trigger_core_transformation",
        "trigger_analytics_transformation",
    },
}


@pytest.mark.parametrize("dag_id", EXPECTED_TASK_IDS)
def test_dag_contains_expected_tasks(dag_bag, dag_id: str) -> None:
    """Each DAG must expose exactly its expected task IDs."""
    dag = dag_bag.get_dag(dag_id)

    assert dag is not None
    assert set(dag.task_ids) == EXPECTED_TASK_IDS[dag_id]


@pytest.mark.parametrize(
    ("dag_id", "upstream_task_id", "downstream_task_id"),
    [
        (
            "staging_transformation",
            "transform_raw_to_staging",
            "validate_staging_quality",
        ),
        (
            "core_transformation",
            "transform_staging_to_core",
            "validate_core_quality",
        ),
        (
            "analytics_transformation",
            "transform_core_to_analytics",
            "validate_analytics_quality",
        ),
        (
            "global_pipeline",
            "trigger_raw_ingestion",
            "trigger_staging_transformation",
        ),
        (
            "global_pipeline",
            "trigger_staging_transformation",
            "trigger_core_transformation",
        ),
        (
            "global_pipeline",
            "trigger_core_transformation",
            "trigger_analytics_transformation",
        ),
    ],
)
def test_dag_tasks_have_expected_dependencies(
    dag_bag,
    dag_id: str,
    upstream_task_id: str,
    downstream_task_id: str,
) -> None:
    """Pipeline stages and their quality gates must run in order."""
    dag = dag_bag.get_dag(dag_id)

    assert dag is not None
    assert downstream_task_id in dag.get_task(upstream_task_id).downstream_task_ids