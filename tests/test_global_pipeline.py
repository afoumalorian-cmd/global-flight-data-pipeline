"""Tests for the global Airflow pipeline orchestration."""

import pytest
from airflow.providers.standard.operators.trigger_dagrun import (
    TriggerDagRunOperator,
)


TRIGGERED_DAGS = (
    ("trigger_raw_ingestion", "raw_ingestion"),
    ("trigger_staging_transformation", "staging_transformation"),
    ("trigger_core_transformation", "core_transformation"),
    ("trigger_analytics_transformation", "analytics_transformation"),
)


@pytest.mark.parametrize(("task_id", "trigger_dag_id"), TRIGGERED_DAGS)
def test_global_pipeline_triggers_expected_dag(
    dag_bag,
    task_id: str,
    trigger_dag_id: str,
) -> None:
    """Each orchestration task must trigger and wait for its target DAG."""
    dag = dag_bag.get_dag("global_pipeline")
    task = dag.get_task(task_id)

    assert isinstance(task, TriggerDagRunOperator)
    assert task.trigger_dag_id == trigger_dag_id
    assert task.wait_for_completion is True
    assert task.allowed_states == ["success"]
    assert task.failed_states == ["failed"]
    assert task.poke_interval == 10


def test_global_pipeline_runs_all_layers_in_sequence(dag_bag) -> None:
    """The global pipeline must run RAW, STAGING, CORE, then ANALYTICS."""
    dag = dag_bag.get_dag("global_pipeline")

    ordered_task_ids = [
        "trigger_raw_ingestion",
        "trigger_staging_transformation",
        "trigger_core_transformation",
        "trigger_analytics_transformation",
    ]

    for upstream_task_id, downstream_task_id in zip(
        ordered_task_ids,
        ordered_task_ids[1:],
    ):
        upstream_task = dag.get_task(upstream_task_id)

        assert downstream_task_id in upstream_task.downstream_task_ids