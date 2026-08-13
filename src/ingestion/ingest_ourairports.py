import argparse
import logging

from src.ingestion.csv_loader import load_csv_snapshot
from src.ingestion.database import get_database_connection
from src.ingestion.datasets import DATASETS


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


def ingest_dataset(dataset_name: str) -> None:
    """Ingest one configured OurAirports dataset."""
    dataset = DATASETS[dataset_name]

    table_name = dataset["table"]
    csv_path = dataset["file_path"]
    columns = dataset["columns"]

    logger.info(
        "Starting ingestion for dataset: %s",
        dataset_name,
    )
    logger.info("Source file: %s", csv_path)

    connection = get_database_connection()

    try:
        row_count = load_csv_snapshot(
            connection=connection,
            table_name=table_name,
            csv_path=csv_path,
            columns=columns,
        )

        logger.info(
            "Dataset %s ingested successfully: %s rows loaded",
            dataset_name,
            row_count,
        )

    finally:
        connection.close()
        logger.info("Database connection closed")


def main() -> None:
    """Parse CLI arguments and run the requested ingestion."""
    parser = argparse.ArgumentParser(
        description="Ingest OurAirports datasets into PostgreSQL."
    )

    parser.add_argument(
        "dataset",
        choices=[*DATASETS.keys(), "all"],
        help="Dataset to ingest.",
    )

    args = parser.parse_args()

    if args.dataset == "all":
        for dataset_name in DATASETS:
            ingest_dataset(dataset_name)
    else:
        ingest_dataset(args.dataset)


if __name__ == "__main__":
    main()