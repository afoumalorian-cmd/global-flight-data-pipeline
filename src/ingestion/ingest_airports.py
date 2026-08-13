import csv
import logging
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]    #Finds project root directory
CSV_PATH = PROJECT_ROOT / "data" / "raw" / "ourairports" / "airports.csv" 
ENV_PATH = PROJECT_ROOT / ".env"


# Expected columns from the OurAirports airports dataset
EXPECTED_COLUMNS = [
    "id",
    "ident",
    "type",
    "name",
    "latitude_deg",
    "longitude_deg",
    "elevation_ft",
    "continent",
    "iso_country",
    "iso_region",
    "municipality",
    "scheduled_service",
    "icao_code",
    "iata_code",
    "gps_code",
    "local_code",
    "home_link",
    "wikipedia_link",
    "keywords",
]


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


def validate_csv_file(csv_path: Path) -> None:
    """Validate that the CSV exists and contains the expected columns."""
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with csv_path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.reader(csv_file)
        header = next(reader, None)

    if header != EXPECTED_COLUMNS:
        raise ValueError(
            "Unexpected CSV structure.\n"
            f"Expected: {EXPECTED_COLUMNS}\n"
            f"Received: {header}"
        )


def get_database_connection():
    """Create and return a PostgreSQL connection."""
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5434"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )


def ingest_airports() -> None:
    """Load the OurAirports airports CSV into raw.airports."""
    load_dotenv(ENV_PATH)

    logger.info("Starting airports ingestion")
    logger.info("Source file: %s", CSV_PATH)

    validate_csv_file(CSV_PATH)

    logger.info("CSV validation successful")

    connection = get_database_connection()

    try:
        with connection:
            with connection.cursor() as cursor:
                logger.info("Truncating raw.airports")

                cursor.execute("TRUNCATE TABLE raw.airports;")

                copy_sql = """
                    COPY raw.airports (
                        id,
                        ident,
                        type,
                        name,
                        latitude_deg,
                        longitude_deg,
                        elevation_ft,
                        continent,
                        iso_country,
                        iso_region,
                        municipality,
                        scheduled_service,
                        icao_code,
                        iata_code,
                        "gps_code",
                        local_code,
                        home_link,
                        wikipedia_link,
                        keywords
                    )
                    FROM STDIN
                    WITH (
                        FORMAT CSV,
                        HEADER TRUE,
                        ENCODING 'UTF8'
                    );
                """

                logger.info("Loading airports into PostgreSQL")

                with CSV_PATH.open("r", encoding="utf-8") as csv_file:
                    cursor.copy_expert(copy_sql, csv_file)

                cursor.execute(
                    """
                    UPDATE raw.airports
                    SET source_file = %s;
                    """,
                    (CSV_PATH.name,),
                )

                cursor.execute("SELECT COUNT(*) FROM raw.airports;")
                row_count = cursor.fetchone()[0]

        logger.info(
            "Airports ingestion completed successfully: %s rows loaded",
            row_count,
        )

    finally:
        connection.close()
        logger.info("Database connection closed")


if __name__ == "__main__":
    ingest_airports()