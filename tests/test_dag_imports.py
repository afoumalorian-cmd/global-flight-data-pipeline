"""Tests ensuring every Airflow DAG imports correctly."""

EXPECTED_DAG_IDS = {
    "raw_ingestion",
    "staging_transformation",
    "core_transformation",
    "analytics_transformation",
    "global_pipeline",
}


def test_dags_import_without_errors(dag_bag) -> None:
    """All project DAG files must load without an import error."""
    assert dag_bag.import_errors == {}


def test_expected_dags_are_loaded(dag_bag) -> None:
    """All expected project DAGs must be present in the DagBag."""
    assert EXPECTED_DAG_IDS.issubset(dag_bag.dags)