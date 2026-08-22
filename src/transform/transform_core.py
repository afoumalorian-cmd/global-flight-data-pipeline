"""Transform STAGING data into the CORE layer."""

import logging
from pathlib import Path

from psycopg2 import sql

from src.ingestion.database import get_database_connection
from src.quality.core_quality import validate_core_quality


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TRANSFORMATION_SQL_PATH = (
    PROJECT_ROOT / "sql" / "008_transform_staging_to_core.sql"
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


def get_table_row_count(cursor, table_name: str) -> int:
    """Return the number of rows in a qualified PostgreSQL table."""
    schema_name, relation_name = table_name.split(".", maxsplit=1)

    query = sql.SQL("SELECT COUNT(*) FROM {}.{}").format(
        sql.Identifier(schema_name),
        sql.Identifier(relation_name),
    )

    cursor.execute(query)

    return cursor.fetchone()[0]


def get_eligible_runway_count(cursor) -> int:
    """Return the number of STAGING runways eligible for CORE."""
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM staging.runways r
        JOIN staging.airports a
            ON a.id = r.airport_ref
        """
    )

    return cursor.fetchone()[0]


def validate_core_row_counts(connection) -> None:
    """Validate row counts between STAGING and CORE tables."""
    validations = (
        (
            "countries",
            "staging.countries",
            "core.countries",
        ),
        (
            "regions",
            "staging.regions",
            "core.regions",
        ),
        (
            "airports",
            "staging.airports",
            "core.airports",
        ),
    )

    with connection.cursor() as cursor:
        for dataset_name, staging_table, core_table in validations:
            staging_count = get_table_row_count(
                cursor,
                staging_table,
            )

            core_count = get_table_row_count(
                cursor,
                core_table,
            )

            logger.info(
                "%s row count: staging=%s core=%s",
                dataset_name,
                staging_count,
                core_count,
            )

            if staging_count != core_count:
                raise RuntimeError(
                    f"Row count mismatch for {dataset_name}: "
                    f"staging={staging_count}, core={core_count}"
                )

        eligible_runway_count = get_eligible_runway_count(
            cursor
        )

        core_runway_count = get_table_row_count(
            cursor,
            "core.runways",
        )

        logger.info(
            "runways row count: eligible_staging=%s core=%s",
            eligible_runway_count,
            core_runway_count,
        )

        if eligible_runway_count != core_runway_count:
            raise RuntimeError(
                "Row count mismatch for runways: "
                f"eligible_staging={eligible_runway_count}, "
                f"core={core_runway_count}"
            )


def transform_core() -> None:
    """Transform OurAirports datasets from STAGING into CORE."""
    logger.info(
        "Starting OurAirports STAGING -> CORE transformation"
    )
    logger.info(
        "Transformation SQL: %s",
        TRANSFORMATION_SQL_PATH,
    )

    if not TRANSFORMATION_SQL_PATH.is_file():
        raise FileNotFoundError(
            f"Transformation SQL file not found: "
            f"{TRANSFORMATION_SQL_PATH}"
        )

    transformation_sql = TRANSFORMATION_SQL_PATH.read_text(
        encoding="utf-8"
    )

    connection = get_database_connection()

    try:
        with connection.cursor() as cursor:
            logger.info("Executing CORE transformation")
            cursor.execute(transformation_sql)

        logger.info(
            "CORE transformation executed successfully"
        )

        logger.info(
            "Validating CORE row counts"
        )

        validate_core_row_counts(connection)

        logger.info(
            "Running CORE Data Quality checks"
        )

        validate_core_quality(connection)

        logger.info(
            "CORE Data Quality checks completed"
        )

        connection.commit()

        logger.info(
            "OurAirports STAGING -> CORE transformation "
            "completed successfully"
        )

    except Exception:
        connection.rollback()

        logger.exception(
            "OurAirports CORE transformation failed"
        )

        raise

    finally:
        connection.close()
        logger.info("Database connection closed")


def main() -> None:
    """Run the OurAirports CORE transformation."""
    transform_core()


if __name__ == "__main__":
    main()