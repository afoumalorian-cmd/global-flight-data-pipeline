"""Unit tests for Airflow monitoring callbacks."""

import logging
from types import SimpleNamespace

from src.monitoring.airflow_callbacks import log_task_failure, log_task_retry


def test_failure_callback_logs_execution_context(caplog) -> None:
    """The failure callback must log useful task and error information."""
    task_instance = SimpleNamespace(
        dag_id="raw_ingestion",
        task_id="ingest_ourairports_raw",
        try_number=2,
    )

    with caplog.at_level(logging.ERROR):
        log_task_failure(
            {
                "task_instance": task_instance,
                "run_id": "manual__test-run",
                "exception": RuntimeError("Database unavailable"),
            }
        )

    assert "Airflow task failed" in caplog.text
    assert "raw_ingestion" in caplog.text
    assert "ingest_ourairports_raw" in caplog.text
    assert "manual__test-run" in caplog.text
    assert "Database unavailable" in caplog.text


def test_retry_callback_supports_ti_context_key(caplog) -> None:
    """The retry callback must support Airflow's short ti context key."""
    task_instance = SimpleNamespace(
        dag_id="core_transformation",
        task_id="transform_staging_to_core",
        try_number=1,
    )

    with caplog.at_level(logging.WARNING):
        log_task_retry(
            {
                "ti": task_instance,
                "run_id": "scheduled__test-run",
            }
        )

    assert "Airflow task retry scheduled" in caplog.text
    assert "core_transformation" in caplog.text
    assert "transform_staging_to_core" in caplog.text
    assert "scheduled__test-run" in caplog.text