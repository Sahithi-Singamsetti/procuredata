import sys
from pathlib import Path

import pandas as pd
import pytest

# Make the src folder accessible to pytest
sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src")
)

from cleaning import (
    standardise_text_columns,
    calculate_obligation_summary,
    validate_transaction_ids
)

def test_validate_transaction_ids():

    df = pd.DataFrame({
        "contract_transaction_unique_key": [
            "TXN001",
            "TXN002",
            " TXN001",
            None,
            "",
            "   "
        ]
    })

    summary = validate_transaction_ids(df)

    assert summary["total_rows"] == 6
    assert summary["missing_ids"] == 1
    assert summary["empty_ids"] == 2
    assert summary["duplicate_ids"] == 1
    assert summary["unique_ids"] == 2

def test_validate_transaction_ids_with_empty_dataframe():

    df = pd.DataFrame({
        "contract_transaction_unique_key": pd.Series(dtype="string")
    })

    summary = validate_transaction_ids(df)

    assert summary["total_rows"] == 0
    assert summary["missing_ids"] == 0
    assert summary["empty_ids"] == 0
    assert summary["duplicate_ids"] == 0
    assert summary["unique_ids"] == 0

def test_validate_transaction_ids_raises_error_for_missing_column():

    df = pd.DataFrame({
        "recipient_name": ["NASA"]
    })

    with pytest.raises(
        ValueError,
        match="Column 'contract_transaction_unique_key' does not exist"
    ):
        validate_transaction_ids(df)

def test_validate_transaction_ids_raises_error_for_non_text_values():

    df = pd.DataFrame({
        "contract_transaction_unique_key": [123, 456]
    })

    with pytest.raises(
        TypeError,
        match="Transaction IDs must contain text values"
    ):
        validate_transaction_ids(df)


def test_validate_transaction_ids_does_not_modify_original_dataframe():

    df = pd.DataFrame({
        "contract_transaction_unique_key": [
            " TXN001 ",
            "TXN002"
        ]
    })

    original_df = df.copy()

    validate_transaction_ids(df)

    pd.testing.assert_frame_equal(df, original_df)

def test_standardise_text_columns():

    data = {
        "recipient_name": [" NASA ", "LOCKHEED MARTIN ", "  "],
        "naics_description": [" Research ", "Engineering", ""]
    }

    df = pd.DataFrame(data)

    text_columns = [
        "recipient_name",
        "naics_description"
    ]

    cleaned_df = standardise_text_columns(df, text_columns)

    assert cleaned_df["recipient_name"].iloc[0] == "NASA"
    assert cleaned_df["recipient_name"].iloc[1] == "LOCKHEED MARTIN"
    assert pd.isna(cleaned_df["recipient_name"].iloc[2])

    assert cleaned_df["naics_description"].iloc[0] == "Research"
    assert pd.isna(cleaned_df["naics_description"].iloc[2])

def test_standardisation_does_not_modify_original_dataframe():

    data = {
        "recipient_name": [" NASA ", "LOCKHEED MARTIN "]
    }

    df = pd.DataFrame(data)

    original_df = df.copy()

    cleaned_df = standardise_text_columns(
        df,
        ["recipient_name"]
    )

    pd.testing.assert_frame_equal(df, original_df)

    assert cleaned_df["recipient_name"].iloc[0] == "NASA"

def test_standardise_text_columns_raises_error_for_missing_column():

    df = pd.DataFrame({
        "recipient_name": ["NASA"]
    })

    with pytest.raises(
        ValueError,
        match="Column 'naics_description' does not exist"
    ):
        standardise_text_columns(
            df,
            ["naics_description"]
        )

def test_calculate_obligation_summary():

    df = pd.DataFrame({
        "federal_action_obligation": [
            1000.00,
            500.00,
            -200.00,
            -100.00,
            0.00,
            0.00
        ]
    })

    summary = calculate_obligation_summary(df)

    assert summary["net_obligations"] == 1200.00
    assert summary["positive_obligations"] == 1500.00
    assert summary["negative_obligations"] == -300.00
    assert summary["zero_obligations"] == 2

def test_calculate_obligation_summary_raises_error_for_missing_values():

    df = pd.DataFrame({
        "federal_action_obligation": [
            1000.00,
            None,
            -200.00
        ]
    })

    with pytest.raises(
        ValueError,
        match="Missing financial obligation values"
    ):
        calculate_obligation_summary(df)

def test_calculate_obligation_summary_raises_error_for_missing_column():

    df = pd.DataFrame({
        "recipient_name": ["NASA", "LOCKHEED MARTIN"]
    })

    with pytest.raises(
        ValueError,
        match="Column 'federal_action_obligation' does not exist"
    ):
        calculate_obligation_summary(df)

def test_standardise_text_columns_raises_error_for_non_text_column():

    df = pd.DataFrame({
        "recipient_name": [123, 456]
    })

    with pytest.raises(
        TypeError,
        match="must contain text values"
    ):
        standardise_text_columns(
            df,
            ["recipient_name"]
        )

def test_calculate_obligation_summary_raises_error_for_non_numeric_values():

    df = pd.DataFrame({
        "federal_action_obligation": [
            "1000",
            "500",
            "-200"
        ]
    })

    with pytest.raises(
        TypeError,
        match="Financial obligation values must be numeric"
    ):
        calculate_obligation_summary(df)

def test_calculate_obligation_summary_raises_error_for_infinite_values():

    df = pd.DataFrame({
        "federal_action_obligation": [
            1000.00,
            float("inf"),
            -200.00
        ]
    })

    with pytest.raises(
        ValueError,
        match="Infinite financial obligation values"
    ):
        calculate_obligation_summary(df)
