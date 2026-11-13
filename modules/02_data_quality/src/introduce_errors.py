
import csv
from decimal import Decimal
from pathlib import Path


# --------------------------------------------------
# 1. Define project paths and dataset columns
# --------------------------------------------------

MODULE_DIR = Path(__file__).resolve().parents[1]

CLEAN_FILE = MODULE_DIR / "data" / "generated" / "purchases_clean.csv"
INPUT_DIR = MODULE_DIR / "data" / "input"
ANSWER_KEY_FILE = MODULE_DIR / "data" / "answer_key.csv"

COLUMNS = [
    "date",
    "supplier",
    "item",
    "quantity",
    "unit_price",
    "total",
]

ANSWER_KEY_COLUMNS = [
    "file_name",
    "row_number",
    "column",
    "issue_type",
    "expected_condition",
    "actual_value",
    "reference_row",
]

# --------------------------------------------------
# 2. Read and write CSV files
# --------------------------------------------------

def read_purchases(file_path):
    """Read purchase records without changing their raw values."""
    with file_path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames != COLUMNS:
            raise ValueError(
                f"Unexpected dataset columns. Expected: {COLUMNS}"
            )

        return list(reader)

def write_csv(file_path, records, columns):
    """Write records to a CSV file."""
    with file_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(records)


# --------------------------------------------------
# 3. Record each deliberately planted mistake
# --------------------------------------------------

def plant_issue(
    records,
    answer_key,
    file_name,
    data_index,
    column,
    new_value,
    issue_type,
    expected_condition,
):
    """Change one cell and document the planted issue."""

    records[data_index][column] = new_value

    answer_key.append({
        "file_name": file_name,
        "row_number": data_index + 2,
        "column": column,
        "issue_type": issue_type,
        "expected_condition": expected_condition,
        "actual_value": new_value,
        "reference_row": "",
    })


# --------------------------------------------------
# 4. Create the five corrupted purchase files
# --------------------------------------------------

def main():
    if not CLEAN_FILE.exists():
        raise FileNotFoundError(
            f"Clean dataset not found: {CLEAN_FILE}"
        )

    INPUT_DIR.mkdir(parents=True, exist_ok=True)

    clean_records = read_purchases(CLEAN_FILE)

    if len(clean_records) != 1000:
        raise ValueError(
            "Expected exactly 1,000 clean purchase records."
        )

    answer_key = []

    # File 1: Blank values
    file_name = "purchases_01.csv"
    records = [row.copy() for row in clean_records]

    plant_issue(
        records, answer_key, file_name,
        0, "supplier", "",
        "blank_value", "Supplier must not be blank"
    )

    plant_issue(
        records, answer_key, file_name,
        1, "item", "",
        "blank_value", "Item must not be blank"
    )

    plant_issue(
        records, answer_key, file_name,
        2, "date", "",
        "blank_value", "Date must not be blank"
    )

    write_csv(INPUT_DIR / file_name, records, COLUMNS)

    # File 2: Invalid prices and text in numeric columns
    file_name = "purchases_02.csv"
    records = [row.copy() for row in clean_records]

    plant_issue(
        records, answer_key, file_name,
        0, "unit_price", "0.00",
        "invalid_price", "Unit price must be greater than zero"
    )

    plant_issue(
        records, answer_key, file_name,
        1, "unit_price", "-25.50",
        "invalid_price", "Unit price must be greater than zero"
    )

    plant_issue(
        records, answer_key, file_name,
        2, "quantity", "many",
        "non_numeric_value", "Quantity must be numeric"
    )

    plant_issue(
        records, answer_key, file_name,
        3, "unit_price", "unknown",
        "non_numeric_value", "Unit price must be numeric"
    )

    plant_issue(
        records, answer_key, file_name,
        4, "total", "pending",
        "non_numeric_value", "Total must be numeric"
    )

    write_csv(INPUT_DIR / file_name, records, COLUMNS)

    # File 3: Incorrect totals and duplicate rows
    file_name = "purchases_03.csv"
    records = [row.copy() for row in clean_records]

    original_total = Decimal(records[0]["total"])
    records[0]["total"] = f"{original_total + Decimal('1.00'):.2f}"

    answer_key.append({
        "file_name": file_name,
        "row_number": 2,
        "column": "total",
        "issue_type": "incorrect_total",
        "expected_condition": "Total must equal quantity multiplied by unit price, within 0.01",
        "actual_value": records[0]["total"],
        "reference_row": "",
    })

    original_total = Decimal(records[1]["total"])
    records[1]["total"] = f"{original_total + Decimal('0.50'):.2f}"

    answer_key.append({
        "file_name": file_name,
        "row_number": 3,
        "column": "total",
        "issue_type": "incorrect_total",
        "expected_condition": "Total must equal quantity multiplied by unit price, within 0.01",
        "actual_value": records[1]["total"],
        "reference_row": "",
    })

    # Copy data record 50 into data record 51.
    records[50] = records[49].copy()

    answer_key.append({
        "file_name": file_name,
        "row_number": 52,
        "column": "all columns",
        "issue_type": "duplicate_row",
        "expected_condition": "Each complete purchase row must be unique",
        "actual_value": "Duplicate of CSV row 51",
        "reference_row": 51,
    })

    write_csv(INPUT_DIR / file_name, records, COLUMNS)

    # File 4: Invalid and future dates
    file_name = "purchases_04.csv"
    records = [row.copy() for row in clean_records]

    plant_issue(
        records, answer_key, file_name,
        0, "date", "2099-01-01",
        "future_date", "Purchase date must not be in the future"
    )

    plant_issue(
        records, answer_key, file_name,
        1, "date", "31/12/2025",
        "invalid_date", "Date must use YYYY-MM-DD format"
    )

    write_csv(INPUT_DIR / file_name, records, COLUMNS)

    # File 5: Combination of different error types
    file_name = "purchases_05.csv"
    records = [row.copy() for row in clean_records]

    plant_issue(
        records, answer_key, file_name,
        0, "supplier", "",
        "blank_value", "Supplier must not be blank"
    )

    plant_issue(
        records, answer_key, file_name,
        1, "unit_price", "-10.00",
        "invalid_price", "Unit price must be greater than zero"
    )

    plant_issue(
        records, answer_key, file_name,
        2, "quantity", "several",
        "non_numeric_value", "Quantity must be numeric"
    )

    plant_issue(
        records, answer_key, file_name,
        3, "date", "2099-06-15",
        "future_date", "Purchase date must not be in the future"
    )

    original_total = Decimal(records[4]["total"])
    records[4]["total"] = f"{original_total + Decimal('2.00'):.2f}"

    answer_key.append({
        "file_name": file_name,
        "row_number": 6,
        "column": "total",
        "issue_type": "incorrect_total",
        "expected_condition": "Total must equal quantity multiplied by unit price, within 0.01",
        "actual_value": records[4]["total"],
        "reference_row": "",
    })

    records[6] = records[5].copy()

    answer_key.append({
        "file_name": file_name,
        "row_number": 8,
        "column": "all columns",
        "issue_type": "duplicate_row",
        "expected_condition": "Each complete purchase row must be unique",
        "actual_value": "Duplicate of CSV row 7",
        "reference_row": 7,
    })

    write_csv(INPUT_DIR / file_name, records, COLUMNS)

    # --------------------------------------------------
    # 5. Save the independent answer key
    # --------------------------------------------------

    write_csv(
        ANSWER_KEY_FILE,
        answer_key,
        ANSWER_KEY_COLUMNS,
    )

    print("Corrupted datasets generated successfully!")
    print("Number of purchase files: 5")
    print("Records per file: 1,000")
    print("Planted issues:", len(answer_key))
    print("Input directory:", INPUT_DIR)
    print("Answer key:", ANSWER_KEY_FILE)


if __name__ == "__main__":
    main()
