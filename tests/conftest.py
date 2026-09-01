"""Shared pytest fixtures for Airflow DAG tests."""

from pathlib import Path

import pytest
from airflow.models.dagbag import DagBag


DAGS_FOLDER = Path("/opt/airflow/dags")


@pytest.fixture(scope="session")
def dag_bag() -> DagBag:
    """Load all project DAGs once for the complete test session."""
    return DagBag(dag_folder=str(DAGS_FOLDER))