"""Airflow callbacks used for pipeline monitoring."""

import logging
from typing import Any


logger = logging.getLogger(__name__)


def log_task_failure(context: dict[str, Any]) -> None:
    """Log useful information when an Airflow task fails."""
    task_instance = context.get("task_instance") or context.get("ti")
    exception = context.get("exception")

    logger.error(
        "Airflow task failed: dag_id=%s task_id=%s run_id=%s "
        "try_number=%s exception=%r",
        getattr(task_instance, "dag_id", "unknown"),
        getattr(task_instance, "task_id", "unknown"),
        context.get("run_id", "unknown"),
        getattr(task_instance, "try_number", "unknown"),
        exception,
    )


def log_task_retry(context: dict[str, Any]) -> None:
    """Log useful information when an Airflow task is scheduled for retry."""
    task_instance = context.get("task_instance") or context.get("ti")

    logger.warning(
        "Airflow task retry scheduled: dag_id=%s task_id=%s "
        "run_id=%s try_number=%s",
        getattr(task_instance, "dag_id", "unknown"),
        getattr(task_instance, "task_id", "unknown"),
        context.get("run_id", "unknown"),
        getattr(task_instance, "try_number", "unknown"),
    )