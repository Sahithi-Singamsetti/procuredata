
from datetime import date
from pathlib import Path
import random
import pandas as pd
from faker import Faker

# Reproducible synthetic data
fake = Faker("en_US")
fake.seed_instance(42)
random.seed(42)

# Module directory and output location
MODULE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = MODULE_DIR / "data" / "generated"
OUTPUT_FILE = OUTPUT_DIR / "purchases_clean.csv"

# Sample purchase items
ITEMS = [
    "Laptop",
    "Desktop Computer",
    "Monitor",
    "Keyboard",
    "Mouse",
    "Printer",
    "Office Chair",
    "Desk",
    "Network Switch",
    "External Hard Drive",
    "USB Cable",
    "Headphones",
    "Webcam",
    "Router",
    "Power Supply",
]

def cents_to_amount(cents):
    """Convert an integer number of cents into a two-decimal amount."""
    return f"{cents // 100}.{cents % 100:02d}"


def generate_purchase_records(number_of_records=1000):
    """Generate synthetic purchase records."""

    if not isinstance(number_of_records, int) or isinstance(number_of_records, bool):
        raise TypeError("Number of records must be an integer.")

    if number_of_records < 0:
        raise ValueError("Number of records cannot be negative.")

    records = []

    for _ in range(number_of_records):
        purchase_date = fake.date_between(
            start_date=date(2025, 1, 1),
            end_date=date(2026, 10, 31),
        )

        supplier = fake.company()
        item = random.choice(ITEMS)
        quantity = random.randint(1, 100)

        unit_price_cents = random.randint(100, 50000)
        total_cents = quantity * unit_price_cents

        records.append({
            "date": purchase_date.isoformat(),
            "supplier": supplier,
            "item": item,
            "quantity": quantity,
            "unit_price": cents_to_amount(unit_price_cents),
            "total": cents_to_amount(total_cents),
        })

    return pd.DataFrame(
    records,
    columns=["date", "supplier", "item", "quantity", "unit_price", "total"],
)

def main():
    """Generate and save the clean purchase dataset."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    purchases = generate_purchase_records()

    purchases.to_csv(OUTPUT_FILE, index=False)

    print(f"Dataset generated successfully: {OUTPUT_FILE}")
    print(f"Number of records: {len(purchases)}")
    print("\nDataset preview:")
    print(purchases.head())
    print("\nDataset shape:", purchases.shape)

if __name__ == "__main__":
    main()
