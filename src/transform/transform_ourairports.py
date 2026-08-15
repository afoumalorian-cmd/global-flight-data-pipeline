import logging
from pathlib import Path

from psycopg2 import sql

from src.ingestion.database import get_database_connection
from src.ingestion.datasets import DATASETS

from src.quality.staging_quality import validate_staging_quality


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TRANSFORMATION_SQL_PATH = (
    PROJECT_ROOT / "sql" / "006_transform_raw_to_staging.sql"
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


def validate_staging_row_counts(connection) -> None:
    """Validate that RAW and STAGING contain the same number of rows."""
    with connection.cursor() as cursor:
        for dataset_name, dataset in DATASETS.items():
            raw_table = f"raw.{dataset['table']}"
            staging_table = f"staging.{dataset['table']}"

            raw_count = get_table_row_count(
                cursor,
                raw_table,
            )

            staging_count = get_table_row_count(
                cursor,
                staging_table,
            )

            logger.info(
                "%s row count: raw=%s staging=%s",
                dataset_name,
                raw_count,
                staging_count,
            )

            if raw_count != staging_count:
                raise RuntimeError(
                    f"Row count mismatch for {dataset_name}: "
                    f"raw={raw_count}, staging={staging_count}"
                )


def transform_ourairports() -> None:
    """Transform OurAirports datasets from RAW into STAGING."""
    logger.info(
        "Starting OurAirports RAW -> STAGING transformation"
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
            logger.info("Executing staging transformation")
            cursor.execute(transformation_sql)

        logger.info(
            "Staging transformation executed successfully"
        )

        validate_staging_row_counts(connection)

        logger.info("Running staging Data Quality checks")

        validate_staging_quality(connection)

        logger.info(
            "Staging Data Quality checks completed"
        )

        connection.commit()

        logger.info(
            "OurAirports RAW -> STAGING transformation "
            "completed successfully"
        )

    except Exception:
        connection.rollback()

        logger.exception(
            "OurAirports staging transformation failed"
        )

        raise

    finally:
        connection.close()
        logger.info("Database connection closed")


def main() -> None:
    """Run the OurAirports staging transformation."""
    transform_ourairports()


if __name__ == "__main__":
    main()