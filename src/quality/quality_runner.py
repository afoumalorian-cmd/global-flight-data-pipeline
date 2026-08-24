"""Run Data Quality validations as standalone pipeline tasks."""

import logging

from src.ingestion.database import get_database_connection
from src.quality.staging_quality import validate_staging_quality
from src.transform.transform_ourairports import validate_staging_row_counts
from src.quality.core_quality import validate_core_quality
from src.transform.transform_core import validate_core_row_counts
from src.quality.analytics_quality import validate_analytics_quality
from src.transform.transform_analytics import (
    validate_analytics_row_counts,
    validate_runway_counts,
)


logger = logging.getLogger(__name__)


def run_staging_quality_checks() -> None:
    """Run standalone Data Quality checks for the STAGING layer."""
    logger.info("Starting standalone STAGING Data Quality checks")

    connection = get_database_connection()

    try:
        logger.info("Validating STAGING row counts")
        validate_staging_row_counts(connection)

        logger.info("Running STAGING Data Quality checks")
        validate_staging_quality(connection)

        logger.info(
            "Standalone STAGING Data Quality checks completed successfully"
        )
    finally:
        connection.close()
        logger.info("Database connection closed")

def run_core_quality_checks() -> None:
    """Run standalone Data Quality checks for the CORE layer."""
    logger.info("Starting standalone CORE Data Quality checks")

    connection = get_database_connection()

    try:
        logger.info("Validating CORE row counts")
        validate_core_row_counts(connection)

        logger.info("Running CORE Data Quality checks")
        validate_core_quality(connection)

        logger.info(
            "Standalone CORE Data Quality checks completed successfully"
        )
    finally:
        connection.close()
        logger.info("Database connection closed")

def run_analytics_quality_checks() -> None:
    """Run standalone Data Quality checks for the ANALYTICS layer."""
    logger.info("Starting standalone ANALYTICS Data Quality checks")

    connection = get_database_connection()

    try:
        logger.info("Validating ANALYTICS row counts")
        validate_analytics_row_counts(connection)

        logger.info("Validating ANALYTICS runway counts")
        validate_runway_counts(connection)

        logger.info("Running ANALYTICS Data Quality checks")
        validate_analytics_quality(connection)

        logger.info(
            "Standalone ANALYTICS Data Quality checks completed successfully"
        )
    finally:
        connection.close()
        logger.info("Database connection closed")