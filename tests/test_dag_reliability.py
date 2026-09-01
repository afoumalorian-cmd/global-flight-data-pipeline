"""Tests for Airflow task reliability and monitoring configuration."""

from datetime import timedelta

import pytest

from src.monitoring.airflow_callbacks import log_task_failure, log_task_retry


TRANSFORMATION_TASKS = (
    ("raw_ingestion", "ingest_ourairports_raw", timedelta(minutes=30)),
    ("staging_transformation", "transform_raw_to_staging", timedelta(minutes=20)),
    ("core_transformation", "transform_staging_to_core", timedelta(minutes=20)),
    (
        "analytics_transformation",
        "transform_core_to_analytics",
        timedelta(minutes=20),
    ),
)

QUALITY_GATE_TASKS = (
    ("staging_transformation", "validate_staging_quality"),
    ("core_transformation", "validate_core_quality"),
    ("analytics_transformation", "validate_analytics_quality"),
)


@pytest.mark.parametrize(
    ("dag_id", "task_id", "expected_timeout"),
    TRANSFORMATION_TASKS,
)
def test_transformation_tasks_have_retry_policy(
    dag_bag,
    dag_id: str,
    task_id: str,
    expected_timeout: timedelta,
) -> None:
    """Transformation tasks must retry twice with a five-minute delay."""
    task = dag_bag.get_dag(dag_id).get_task(task_id)

    assert task.retries == 2
    assert task.retry_delay == timedelta(minutes=5)
    assert task.execution_timeout == expected_timeout


@pytest.mark.parametrize(("dag_id", "task_id"), QUALITY_GATE_TASKS)
def test_quality_gates_have_no_retries(dag_bag, dag_id: str, task_id: str) -> None:
    """Quality gates must fail immediately and never retry."""
    task = dag_bag.get_dag(dag_id).get_task(task_id)

    assert task.retries == 0
    assert task.execution_timeout == timedelta(minutes=10)


@pytest.mark.parametrize(
    ("dag_id", "task_id"),
    [
        *[(dag_id, task_id) for dag_id, task_id, _ in TRANSFORMATION_TASKS],
        *QUALITY_GATE_TASKS,
    ],
)
def test_layer_tasks_use_monitoring_callbacks(
    dag_bag,
    dag_id: str,
    task_id: str,
) -> None:
    """Layer DAG tasks must expose failure and retry monitoring callbacks."""
    task = dag_bag.get_dag(dag_id).get_task(task_id)

    assert log_task_failure in task.on_failure_callback
    assert log_task_retry in task.on_retry_callback


def test_global_pipeline_has_failure_monitoring_callback(dag_bag) -> None:
    """The orchestrator must report failures through its monitoring callback."""
    dag = dag_bag.get_dag("global_pipeline")

    assert dag.default_args["on_failure_callback"] is log_task_failure