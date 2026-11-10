import csv
import sys
from pathlib import Path
from decimal import Decimal
from datetime import date

# Find the project root folder
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Make the project root accessible to Python
sys.path.insert(0, str(PROJECT_ROOT))

from shared.database.connection import get_connection

# Locate the cleaned dataset
DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "spend_analytics"
    / "spend_cleaned.csv"
)

def load_data():

    print("Starting data loading...")

    # Check that the cleaned dataset exists
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Cleaned dataset not found: {DATA_FILE}"
        )

    with get_connection() as connection:

        with connection.cursor() as cursor:

            # Count existing records
            cursor.execute(
                "SELECT COUNT(*) FROM spend_transactions"
            )
            count_before = cursor.fetchone()[0]

            # SQL statement for inserting records
            insert_query = """
                INSERT INTO spend_transactions (
                    contract_transaction_unique_key,
                    award_id_piid,
                    federal_action_obligation,
                    action_date,
                    recipient_uei,
                    recipient_name,
                    product_or_service_code,
                    product_or_service_code_description,
                    naics_code,
                    naics_description
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (contract_transaction_unique_key)
                DO NOTHING
            """

            batch = []
            batch_size = 1000
            attempted = 0

            # Read the cleaned CSV
            with open(
                DATA_FILE,
                "r",
                encoding="utf-8",
                newline=""
            ) as file:

                reader = csv.DictReader(file)

                # Define the required CSV columns
                required_columns = {
                    "contract_transaction_unique_key",
                    "award_id_piid",
                    "federal_action_obligation",
                    "action_date",
                    "recipient_uei",
                    "recipient_name",
                    "product_or_service_code",
                    "product_or_service_code_description",
                    "naics_code",
                    "naics_description"
                }

                # Check whether all required columns exist
                actual_columns = set(reader.fieldnames or [])

                missing_columns = required_columns - actual_columns

                if missing_columns:
                    raise ValueError(
                        "Required CSV columns are missing: "
                        f"{sorted(missing_columns)}"
                    )

                for row in reader:

                    record = (
                        row["contract_transaction_unique_key"],
                        row["award_id_piid"],
                        Decimal(row["federal_action_obligation"]),
                        date.fromisoformat(row["action_date"]),
                        row["recipient_uei"],
                        row["recipient_name"],
                        row["product_or_service_code"] or None,
                        row["product_or_service_code_description"] or None,
                        row["naics_code"] or None,
                        row["naics_description"] or None,
                    )

                    batch.append(record)
                    attempted += 1

                    # Insert records in batches of 1,000
                    if len(batch) == batch_size:
                        cursor.executemany(insert_query, batch)
                        batch.clear()

                # Insert any remaining records
                if batch:
                    cursor.executemany(insert_query, batch)

            # Count records after loading
            cursor.execute(
                "SELECT COUNT(*) FROM spend_transactions"
            )
            count_after = cursor.fetchone()[0]

    print("\n--- DATABASE LOADING SUMMARY ---")
    print(f"Records processed: {attempted}")
    print(f"Records already in database: {count_before}")
    print(f"Records in database now: {count_after}")
    print(f"New records inserted: {count_after - count_before}")

    print("\nData loading completed successfully!")


if __name__ == "__main__":
    load_data()
