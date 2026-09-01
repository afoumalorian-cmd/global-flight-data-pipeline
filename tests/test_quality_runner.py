"""Unit tests for standalone data quality gate execution."""

from unittest.mock import MagicMock

import pytest

from src.quality import quality_runner


QUALITY_WORKFLOWS = (
    (
        "run_staging_quality_checks",
        (
            "validate_staging_row_counts",
            "validate_staging_quality",
        ),
    ),
    (
        "run_core_quality_checks",
        (
            "validate_core_row_counts",
            "validate_core_quality",
        ),
    ),
    (
        "run_analytics_quality_checks",
        (
            "validate_analytics_row_counts",
            "validate_runway_counts",
            "validate_analytics_quality",
        ),
    ),
)


@pytest.mark.parametrize(
    ("runner_function_name", "validator_names"),
    QUALITY_WORKFLOWS,
)
def test_quality_gates_run_all_validations_and_close_connection(
    monkeypatch,
    runner_function_name: str,
    validator_names: tuple[str, ...],
) -> None:
    """A quality gate must run each validation and close its connection."""
    connection = MagicMock()
    validators = {
        validator_name: MagicMock()
        for validator_name in validator_names
    }

    monkeypatch.setattr(
        quality_runner,
        "get_database_connection",
        lambda: connection,
    )

    for validator_name, validator in validators.items():
        monkeypatch.setattr(
            quality_runner,
            validator_name,
            validator,
        )

    getattr(quality_runner, runner_function_name)()

    for validator in validators.values():
        validator.assert_called_once_with(connection)

    connection.close.assert_called_once()


@pytest.mark.parametrize(
    ("runner_function_name", "validator_names"),
    QUALITY_WORKFLOWS,
)
def test_quality_gates_close_connection_when_validation_fails(
    monkeypatch,
    runner_function_name: str,
    validator_names: tuple[str, ...],
) -> None:
    """A failing quality validation must still close its database connection."""
    connection = MagicMock()
    validation_error = RuntimeError("Quality check failed")

    first_validator_name, *remaining_validator_names = validator_names
    first_validator = MagicMock(side_effect=validation_error)

    monkeypatch.setattr(
        quality_runner,
        "get_database_connection",
        lambda: connection,
    )
    monkeypatch.setattr(
        quality_runner,
        first_validator_name,
        first_validator,
    )

    remaining_validators = {}

    for validator_name in remaining_validator_names:
        validator = MagicMock()
        remaining_validators[validator_name] = validator
        monkeypatch.setattr(
            quality_runner,
            validator_name,
            validator,
        )

    with pytest.raises(RuntimeError, match="Quality check failed"):
        getattr(quality_runner, runner_function_name)()

    first_validator.assert_called_once_with(connection)

    for validator in remaining_validators.values():
        validator.assert_not_called()

    connection.close.assert_called_once()