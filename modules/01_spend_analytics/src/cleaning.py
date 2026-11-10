import numpy as np
import pandas as pd

def standardise_text_columns(df, text_columns):

    df = df.copy()

    for column in text_columns:

        # Check whether the requested column exists
        if column not in df.columns:
            raise ValueError(
                f"Column '{column}' does not exist in the DataFrame."
            )

        # Ensure the column contains text values
        if not (
            pd.api.types.is_string_dtype(df[column].dtype)
            or pd.api.types.is_object_dtype(df[column].dtype)
        ):
            raise TypeError(
                f"Column '{column}' must contain text values."
            )

        # Remove leading and trailing spaces
        df[column] = df[column].str.strip()

        # Replace empty strings with missing values
        df[column] = df[column].replace("", pd.NA)

    return df


def calculate_obligation_summary(df):

    column = "federal_action_obligation"

    # Check whether the required column exists
    if column not in df.columns:
        raise ValueError(
            f"Column '{column}' does not exist in the DataFrame."
        )

    # Ensure the financial column is numeric
    if not pd.api.types.is_numeric_dtype(df[column].dtype):
        raise TypeError(
            "Financial obligation values must be numeric."
        )

    # Check for missing financial values
    if df[column].isna().any():
        raise ValueError(
            "Missing financial obligation values were found."
        )

    # Check for infinite financial values
    if not np.isfinite(df[column]).all():
        raise ValueError(
            "Infinite financial obligation values were found."
        )

    # Calculate net obligations
    net_obligations = df[column].sum()

    # Calculate positive obligations
    positive_obligations = df.loc[
        df[column] > 0,
        column
    ].sum()

    # Calculate negative obligations
    negative_obligations = df.loc[
        df[column] < 0,
        column
    ].sum()

    # Count zero-obligation transactions
    zero_obligations = (
        df[column] == 0
    ).sum()

    return {
        "net_obligations": round(net_obligations, 2),
        "positive_obligations": round(positive_obligations, 2),
        "negative_obligations": round(negative_obligations, 2),
        "zero_obligations": int(zero_obligations)
    }

def validate_transaction_ids(df):

    column = "contract_transaction_unique_key"

    # Check whether the required column exists
    if column not in df.columns:
        raise ValueError(
            f"Column '{column}' does not exist in the DataFrame."
        )

    # Ensure transaction IDs contain text values
    if not (
        pd.api.types.is_string_dtype(df[column].dtype)
        or pd.api.types.is_object_dtype(df[column].dtype)
    ):
        raise TypeError(
            "Transaction IDs must contain text values."
        )

    # Prepare IDs for validation without modifying the original DataFrame
    transaction_ids = (
        df[column]
        .astype("string")
        .str.strip()
    )

    # Count missing and empty transaction IDs
    missing_ids = int(transaction_ids.isna().sum())

    empty_ids = int(
        transaction_ids.eq("").fillna(False).sum()
    )

    # Exclude missing and empty IDs from duplicate checks
    valid_ids = transaction_ids[
        transaction_ids.notna()
        & transaction_ids.ne("")
    ]

    # Count duplicate and unique transaction IDs
    duplicate_ids = int(valid_ids.duplicated().sum())
    unique_ids = int(valid_ids.nunique())

    return {
        "total_rows": len(df),
        "missing_ids": missing_ids,
        "empty_ids": empty_ids,
        "duplicate_ids": duplicate_ids,
        "unique_ids": unique_ids
    }