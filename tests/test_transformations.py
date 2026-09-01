"""Unit tests for transformation success and failure behaviour."""

from unittest.mock import MagicMock

import pytest

from src.transform import transform_analytics
from src.transform import transform_core
from src.transform import transform_ourairports


TRANSFORMATIONS = (
    (
        transform_ourairports,
        "transform_ourairports",
        "validate_staging_row_counts",
        "validate_staging_quality",
    ),
    (
        transform_core,
        "transform_core",
        "validate_core_row_counts",
        "validate_core_quality",
    ),
    (
        transform_analytics,
        "transform_analytics",
        "validate_analytics_row_counts",
        "validate_analytics_quality",
    ),
)


@pytest.mark.parametrize(
    (
        "module",
        "transform_function_name",
        "row_count_validator_name",
        "quality_validator_name",
    ),
    TRANSFORMATIONS,
)
def test_transformations_commit_after_successful_validation(
    monkeypatch,
    module,
    transform_function_name: str,
    row_count_validator_name: str,
    quality_validator_name: str,
) -> None:
    """A transformation must validate data, commit, and close its connection."""
    connection = MagicMock()
    cursor = MagicMock()
    connection.cursor.return_value.__enter__.return_value = cursor

    row_count_validator = MagicMock()
    quality_validator = MagicMock()

    monkeypatch.setattr(
        module,
        "get_database_connection",
        lambda: connection,
    )
    monkeypatch.setattr(
        module,
        row_count_validator_name,
        row_count_validator,
    )
    monkeypatch.setattr(
        module,
        quality_validator_name,
        quality_validator,
    )

    getattr(module, transform_function_name)()

    assert cursor.execute.call_count >= 1
    row_count_validator.assert_called_once_with(connection)
    quality_validator.assert_called_once_with(connection)
    connection.commit.assert_called_once()
    connection.rollback.assert_not_called()
    connection.close.assert_called_once()


@pytest.mark.parametrize(
    (
        "module",
        "transform_function_name",
        "row_count_validator_name",
        "quality_validator_name",
    ),
    TRANSFORMATIONS,
)
def test_transformations_rollback_and_reraise_on_validation_failure(
    monkeypatch,
    module,
    transform_function_name: str,
    row_count_validator_name: str,
    quality_validator_name: str,
) -> None:
    """A failed validation must rollback, close the connection, and raise."""
    connection = MagicMock()
    cursor = MagicMock()
    connection.cursor.return_value.__enter__.return_value = cursor

    validation_error = RuntimeError("Validation failed")
    row_count_validator = MagicMock(side_effect=validation_error)
    quality_validator = MagicMock()

    monkeypatch.setattr(
        module,
        "get_database_connection",
        lambda: connection,
    )
    monkeypatch.setattr(
        module,
        row_count_validator_name,
        row_count_validator,
    )
    monkeypatch.setattr(
        module,
        quality_validator_name,
        quality_validator,
    )

    with pytest.raises(RuntimeError, match="Validation failed"):
        getattr(module, transform_function_name)()

    connection.rollback.assert_called_once()
    connection.commit.assert_not_called()
    quality_validator.assert_not_called()
    connection.close.assert_called_once()