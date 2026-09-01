"""Tests for DAG scheduling and concurrency configuration."""

import pytest


MANUALLY_TRIGGERED_DAG_IDS = (
    "raw_ingestion",
    "staging_transformation",
    "core_transformation",
    "analytics_transformation",
)


@pytest.mark.parametrize("dag_id", MANUALLY_TRIGGERED_DAG_IDS)
def test_layer_dags_have_no_direct_schedule(dag_bag, dag_id: str) -> None:
    """Layer DAGs must run only when triggered by the global pipeline."""
    dag = dag_bag.get_dag(dag_id)

    assert dag is not None
    assert dag.schedule is None
    assert type(dag.timetable).__name__ == "NullTimetable"


def test_global_pipeline_has_daily_schedule(dag_bag) -> None:
    """The global pipeline must run daily at 02:00."""
    dag = dag_bag.get_dag("global_pipeline")

    assert dag is not None
    assert dag.schedule == "0 2 * * *"
    assert type(dag.timetable).__name__ == "CronTriggerTimetable"


def test_global_pipeline_allows_only_one_active_run(dag_bag) -> None:
    """The global pipeline must prevent overlapping executions."""
    dag = dag_bag.get_dag("global_pipeline")

    assert dag is not None
    assert dag.max_active_runs == 1