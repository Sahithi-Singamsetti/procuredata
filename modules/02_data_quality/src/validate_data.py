
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pandas as pd


# Project paths
MODULE_DIR = Path(__file__).resolve().parents[1]
INPUT_DIR = MODULE_DIR / "data" / "input"
CLEAN_FILE = MODULE_DIR / "data" / "generated" / "purchases_clean.csv"

# Expected dataset structure
EXPECTED_COLUMNS = [
    "date",
    "supplier",
    "item",
    "quantity",
    "unit_price",
    "total",
]


def load_purchase_file(file_path):
    """Load purchase data while preserving original values."""
    data = pd.read_csv(
        file_path,
        dtype=str,
        keep_default_na=False,
    )

    if list(data.columns) != EXPECTED_COLUMNS:
        raise ValueError(
            f"Unexpected dataset columns. Expected: {EXPECTED_COLUMNS}"
        )

    return data


def check_blank_values(data, file_name):
    """Find blank values in purchase records."""
    issues = []

    for index, row in data.iterrows():
        for column in data.columns:
            if not row[column].strip():
                issues.append({
                    "file_name": file_name,
                    "row_number": index + 2,
                    "column": column,
                    "issue_type": "blank_value",
                    "actual_value": row[column],
                })

    return issues


def check_invalid_prices(data, file_name):
    """Find zero or negative unit prices."""
    issues = []

    for index, row in data.iterrows():
        value = row["unit_price"].strip()

        if not value:
            continue

        try:
            price = Decimal(value)

            if price.is_finite() and price <= 0:
                issues.append({
                    "file_name": file_name,
                    "row_number": index + 2,
                    "column": "unit_price",
                    "issue_type": "invalid_price",
                    "actual_value": value,
                })

        except InvalidOperation:
            # Non-numeric values are handled separately.
            continue

    return issues


def check_non_numeric_values(data, file_name):
    """Find text values in numeric columns."""
    issues = []

    numeric_columns = ["quantity", "unit_price", "total"]

    for index, row in data.iterrows():
        for column in numeric_columns:
            value = row[column].strip()

            if not value:
                continue

            try:
                number = Decimal(value)

                if not number.is_finite():
                    raise InvalidOperation

            except InvalidOperation:
                issues.append({
                    "file_name": file_name,
                    "row_number": index + 2,
                    "column": column,
                    "issue_type": "non_numeric_value",
                    "actual_value": value,
                })

    return issues


def check_incorrect_totals(data, file_name):
    """Check whether quantity multiplied by unit price matches total."""
    issues = []

    for index, row in data.iterrows():
        try:
            quantity = Decimal(row["quantity"])
            unit_price = Decimal(row["unit_price"])
            actual_total = Decimal(row["total"])

            # Skip incomplete or non-finite numeric values.
            if not all(
                value.is_finite()
                for value in (quantity, unit_price, actual_total)
            ):
                continue

            # Invalid prices are handled by the price checker.
            if unit_price <= 0:
                continue

            expected_total = quantity * unit_price
            difference = abs(expected_total - actual_total)

            if difference > Decimal("0.01"):
                issues.append({
                    "file_name": file_name,
                    "row_number": index + 2,
                    "column": "total",
                    "issue_type": "incorrect_total",
                    "actual_value": row["total"],
                })

        except InvalidOperation:
            # Invalid numeric values are handled separately.
            continue

    return issues


def check_duplicate_rows(data, file_name):
    """Find complete rows that appear more than once."""
    issues = []

    duplicate_mask = data.duplicated(keep="first")

    for index in data.index[duplicate_mask]:
        issues.append({
            "file_name": file_name,
            "row_number": index + 2,
            "column": "all columns",
            "issue_type": "duplicate_row",
            "actual_value": "Duplicate row",
        })

    return issues


def check_invalid_dates(data, file_name):
    """Find badly formatted or future purchase dates."""
    issues = []

    for index, row in data.iterrows():
        date_value = row["date"].strip()

        # Blank dates are handled by the blank-value checker.
        if not date_value:
            continue

        try:
            parsed_date = datetime.strptime(
                date_value, "%Y-%m-%d"
            ).date()

            if parsed_date.isoformat() != date_value:
                raise ValueError

            if parsed_date > date.today():
                issues.append({
                    "file_name": file_name,
                    "row_number": index + 2,
                    "column": "date",
                    "issue_type": "future_date",
                    "actual_value": date_value,
                })

        except ValueError:
            issues.append({
                "file_name": file_name,
                "row_number": index + 2,
                "column": "date",
                "issue_type": "invalid_date",
                "actual_value": date_value,
            })

    return issues


def validate_purchase_file(file_path):
    """Run all data-quality checks on one purchase file."""
    file_name = file_path.name
    data = load_purchase_file(file_path)

    issues = []

    issues.extend(check_blank_values(data, file_name))
    issues.extend(check_invalid_prices(data, file_name))
    issues.extend(check_non_numeric_values(data, file_name))
    issues.extend(check_incorrect_totals(data, file_name))
    issues.extend(check_duplicate_rows(data, file_name))
    issues.extend(check_invalid_dates(data, file_name))

    return issues


def calculate_quality_score(total_records, issue_count):
    """Calculate a data quality score between 0 and 100."""
    if total_records == 0:
        return 0.0

    score = 100 - (issue_count / total_records * 100)

    return round(max(0, score), 2)
