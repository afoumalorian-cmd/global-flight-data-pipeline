import logging
from pathlib import Path

from psycopg2 import sql

from src.ingestion.database import get_database_connection
from src.quality.analytics_quality import validate_analytics_quality


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TRANSFORMATION_SQL_PATH = (
    PROJECT_ROOT / "sql" / "010_transform_core_to_analytics.sql"
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


def validate_analytics_row_counts(connection) -> None:
    """Validate row counts between CORE and ANALYTICS tables."""
    validations = (
        (
            "countries",
            "core.countries",
            "analytics.country_stats",
        ),
        (
            "regions",
            "core.regions",
            "analytics.region_stats",
        ),
        (
            "airports",
            "core.airports",
            "analytics.airport_stats",
        ),
    )

    with connection.cursor() as cursor:
        for dataset_name, core_table, analytics_table in validations:
            core_count = get_table_row_count(
                cursor,
                core_table,
            )

            analytics_count = get_table_row_count(
                cursor,
                analytics_table,
            )

            logger.info(
                "%s row count: core=%s analytics=%s",
                dataset_name,
                core_count,
                analytics_count,
            )

            if core_count != analytics_count:
                raise RuntimeError(
                    f"Row count mismatch for {dataset_name}: "
                    f"core={core_count}, analytics={analytics_count}"
                )

        global_summary_count = get_table_row_count(
            cursor,
            "analytics.global_summary",
        )

        logger.info(
            "global_summary row count: analytics=%s",
            global_summary_count,
        )

        if global_summary_count != 1:
            raise RuntimeError(
                "analytics.global_summary must contain exactly "
                f"1 row, found {global_summary_count}"
            )


def validate_runway_counts(connection) -> None:
    """Validate runway totals across CORE and ANALYTICS."""
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) FROM core.runways"
        )
        core_runway_count = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT total_runways
            FROM analytics.global_summary
            WHERE summary_id = 1
            """
        )
        global_runway_count = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COALESCE(SUM(runway_count), 0)
            FROM analytics.country_stats
            """
        )
        country_runway_count = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COALESCE(SUM(runway_count), 0)
            FROM analytics.region_stats
            """
        )
        region_runway_count = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COALESCE(SUM(runway_count), 0)
            FROM analytics.airport_stats
            """
        )
        airport_runway_count = cursor.fetchone()[0]

        logger.info(
            "Runway counts: core=%s global=%s country=%s "
            "region=%s airport=%s",
            core_runway_count,
            global_runway_count,
            country_runway_count,
            region_runway_count,
            airport_runway_count,
        )

        runway_counts = {
            core_runway_count,
            global_runway_count,
            country_runway_count,
            region_runway_count,
            airport_runway_count,
        }

        if len(runway_counts) != 1:
            raise RuntimeError(
                "Runway count mismatch across CORE and ANALYTICS: "
                f"core={core_runway_count}, "
                f"global={global_runway_count}, "
                f"country={country_runway_count}, "
                f"region={region_runway_count}, "
                f"airport={airport_runway_count}"
            )


def transform_analytics() -> None:
    """Transform CORE data into ANALYTICS tables."""
    logger.info(
        "Starting CORE -> ANALYTICS transformation"
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
            logger.info(
                "Executing analytics transformation"
            )
            cursor.execute(transformation_sql)

        logger.info(
            "Analytics transformation executed successfully"
        )

        logger.info(
            "Validating ANALYTICS row counts"
        )
        validate_analytics_row_counts(connection)

        logger.info(
            "Validating ANALYTICS runway counts"
        )
        validate_runway_counts(connection)
        
        logger.info(
            "Running ANALYTICS Data Quality checks"
        )

        validate_analytics_quality(connection)

        logger.info(
            "ANALYTICS Data Quality checks completed"
        )

        connection.commit()

        logger.info(
            "CORE -> ANALYTICS transformation "
            "completed successfully"
        )

    except Exception:
        connection.rollback()

        logger.exception(
            "CORE -> ANALYTICS transformation failed"
        )

        raise

    finally:
        connection.close()
        logger.info("Database connection closed")


def main() -> None:
    """Run the CORE to ANALYTICS transformation."""
    transform_analytics()


if __name__ == "__main__":
    main()