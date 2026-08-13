import csv
import logging
from pathlib import Path

from psycopg2 import sql


logger = logging.getLogger(__name__)


def validate_csv_file(
    csv_path: Path,
    expected_columns: list[str],
) -> None:
    """Validate that a CSV exists and has the expected column structure."""
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with csv_path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as csv_file:
        reader = csv.reader(csv_file)
        header = next(reader, None)

    if header != expected_columns:
        raise ValueError(
            f"Unexpected CSV structure for {csv_path.name}.\n"
            f"Expected: {expected_columns}\n"
            f"Received: {header}"
        )


def load_csv_snapshot(
    connection,
    table_name: str,
    csv_path: Path,
    columns: list[str],
) -> int:
    """Load a CSV snapshot into a table in the raw schema."""
    validate_csv_file(csv_path, columns)

    logger.info("CSV validation successful: %s", csv_path.name)

    with connection:
        with connection.cursor() as cursor:
            table_identifier = sql.Identifier(table_name)

            truncate_query = sql.SQL(
                "TRUNCATE TABLE raw.{};"
            ).format(table_identifier)

            logger.info("Truncating raw.%s", table_name)
            cursor.execute(truncate_query)

            column_identifiers = sql.SQL(", ").join(
                sql.Identifier(column)
                for column in columns
            )

            copy_query = sql.SQL(
                """
                COPY raw.{} ({})
                FROM STDIN
                WITH (
                    FORMAT CSV,
                    HEADER TRUE,
                    ENCODING 'UTF8'
                );
                """
            ).format(
                table_identifier,
                column_identifiers,
            )

            logger.info(
                "Loading %s into raw.%s",
                csv_path.name,
                table_name,
            )

            with csv_path.open(
                "r",
                encoding="utf-8",
                newline="",
            ) as csv_file:
                cursor.copy_expert(
                    copy_query.as_string(connection),
                    csv_file,
                )

            update_query = sql.SQL(
                """
                UPDATE raw.{}
                SET source_file = %s;
                """
            ).format(table_identifier)

            cursor.execute(
                update_query,
                (csv_path.name,),
            )

            count_query = sql.SQL(
                "SELECT COUNT(*) FROM raw.{};"
            ).format(table_identifier)

            cursor.execute(count_query)

            row_count = cursor.fetchone()[0]

    return row_count