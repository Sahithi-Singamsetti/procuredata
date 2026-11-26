
import random
from pathlib import Path

import pandas as pd
from faker import Faker

from header_aliases import HEADER_ALIASES


# Initialize Faker
fake = Faker()
Faker.seed(42)
random.seed(42)


# Project directories
PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODULE_DIR = PROJECT_ROOT / "modules" / "03_column_mapper"
DATA_DIR = MODULE_DIR / "data" / "generated"


# Dataset configuration
NUM_FILES = 20
RECORDS_PER_FILE = 50


# Additional header variations not included in the alias library
HEADER_VARIATIONS = {
    "description": [
        "Material Details",
        "Item Information",
        "Goods Details",
    ],
    "quantity": [
        "Ordered Units",
        "Purchase Qty",
        "No. of Items",
    ],
    "unit_price": [
        "Price per Item",
        "Individual Cost",
        "Per Unit Rate",
    ],
    "total_spend": [
        "Overall Spend",
        "Final Line Value",
        "Extended Amount",
    ],
    "supplier": [
        "Vendor Organization",
        "Supplying Company",
        "Paying Party",
    ],
    "manufacturer": [
        "Mfr Name",
        "Produced By",
        "Brand Owner",
    ],
    "part_number": [
        "Catalog Number",
        "Item Reference",
        "Mfr Code",
    ],
    "date": [
        "PO Creation Date",
        "Order Timestamp",
        "Purchase Timestamp",
    ],
}


# Generic headers that may require human review
AMBIGUOUS_HEADERS = {
    "description": ["Details"],
    "quantity": ["Count"],
    "unit_price": ["Price"],
    "total_spend": ["Amount"],
    "supplier": ["Name"],
    "manufacturer": ["Company"],
    "part_number": ["Code"],
    "date": ["Date"],
}


def generate_record():
    quantity = random.randint(1, 500)
    unit_price = round(random.uniform(10, 5000), 2)
    total_spend = round(quantity * unit_price, 2)

    return {
        "description": fake.catch_phrase(),
        "quantity": quantity,
        "unit_price": unit_price,
        "total_spend": total_spend,
        "supplier": fake.company(),
        "manufacturer": fake.company(),
        "part_number": fake.bothify(text="??-####-??"),
        "date": fake.date_between(
            start_date="-2y",
            end_date="today"
        ).isoformat(),
    }


def generate_headers(file_number):
    headers = {}

    for field_index, (standard_field, aliases) in enumerate(
        HEADER_ALIASES.items()
    ):
        variations = HEADER_VARIATIONS[standard_field]
        ambiguous = AMBIGUOUS_HEADERS[standard_field]

        category_position = (
            file_number - 1 + field_index * 3
        ) % 10

        if category_position < 6:
            options = aliases

        elif category_position < 9:
            options = variations

        else:
            options = ambiguous

        selected_alias = random.choice(options)

        headers[standard_field] = selected_alias

    return headers


def generate_datasets():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    answer_key = []

    for file_number in range(1, NUM_FILES + 1):
        headers = generate_headers(file_number)

        records = [
            generate_record()
            for _ in range(RECORDS_PER_FILE)
        ]

        df = pd.DataFrame(records)
        df = df.rename(columns=headers)

        file_name = f"file_{file_number:02d}.csv"
        file_path = DATA_DIR / file_name

        df.to_csv(file_path, index=False)

        for standard_field, original_header in headers.items():
            answer_key.append({
                "file_name": file_name,
                "original_header": original_header,
                "standard_field": standard_field,
            })

    answer_key_df = pd.DataFrame(answer_key)

    answer_key_df.to_csv(
        MODULE_DIR / "data" / "answer_key.csv",
        index=False
    )

    print(f"Generated {NUM_FILES} datasets successfully.")
    print(f"Records per dataset: {RECORDS_PER_FILE}")
    print(f"Total records: {NUM_FILES * RECORDS_PER_FILE}")
    print(f"Answer key entries: {len(answer_key)}")


if __name__ == "__main__":
    generate_datasets()
