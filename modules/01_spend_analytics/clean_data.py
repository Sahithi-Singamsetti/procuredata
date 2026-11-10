import sys
from pathlib import Path

import pandas as pd

# Make the src folder accessible
MODULE_SRC = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(MODULE_SRC))

from cleaning import (
    standardise_text_columns,
    calculate_obligation_summary,
    validate_transaction_ids
)

# STEP 1: Locate the selected dataset

input_file = Path(
    "data/interim/spend_analytics/spend_selected.csv"
)

if not input_file.exists():
    raise FileNotFoundError(
        "Selected dataset not found. "
        "prepare_data.py first."
    )

# STEP 2: Load the dataset

df = pd.read_csv(input_file)

print("Dataset loaded successfully!")

print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\nInitial data types:")
print(df.dtypes)

# STEP 3: Convert action_date into datetime

df["action_date"] = pd.to_datetime(
    df["action_date"],
    errors="coerce"
)

print("\n--- DATE CLEANING ---")

print("New data type:", df["action_date"].dtype)

print("Missing dates after conversion:",
      df["action_date"].isna().sum())

print("Earliest date:", df["action_date"].min())

print("Latest date:", df["action_date"].max())

# STEP 4: Validate obligation amounts

import numpy as np

df["federal_action_obligation"] = pd.to_numeric(
    df["federal_action_obligation"],
    errors="coerce"
)

print("\n--- OBLIGATION VALIDATION ---")

print(
    "Data type:",
    df["federal_action_obligation"].dtype
)

print(
    "Missing amounts:",
    df["federal_action_obligation"].isna().sum()
)

print(
    "Infinite values:",
    np.isinf(df["federal_action_obligation"]).sum()
)

print(
    "Negative amounts:",
    (df["federal_action_obligation"] < 0).sum()
)

print(
    "Zero amounts:",
    (df["federal_action_obligation"] == 0).sum()
)

print(
    "Total net obligations:",
    df["federal_action_obligation"].sum()
)

# STEP 5: Inspect supplier names

print("\n--- SUPPLIER NAME INSPECTION ---")

leading_spaces = (
    df["recipient_name"]
    .str.match(r"^\s", na=False)
    .sum()
)

trailing_spaces = (
    df["recipient_name"]
    .str.match(r".*\s$", na=False)
    .sum()
)

print("Names with leading spaces:", leading_spaces)
print("Names with trailing spaces:", trailing_spaces)

print("\nSample supplier names:")
print(df["recipient_name"].head(10).tolist())

# STEP 6: Check supplier name and UEI consistency

print("\n--- SUPPLIER AND UEI CONSISTENCY ---")

# Check how many different names each UEI has
names_per_uei = (
    df.groupby("recipient_uei")["recipient_name"]
    .nunique()
)

# UEIs associated with multiple supplier names
multiple_names = names_per_uei[names_per_uei > 1]

print(
    "UEIs associated with multiple names:",
    len(multiple_names)
)

# Check how many different UEIs each supplier name has
ueis_per_name = (
    df.groupby("recipient_name")["recipient_uei"]
    .nunique()
)

# Names associated with multiple UEIs
multiple_ueis = ueis_per_name[ueis_per_name > 1]

print(
    "Supplier names associated with multiple UEIs:",
    len(multiple_ueis)
)

# Display examples
print("\nExamples of UEIs with multiple supplier names:")

if len(multiple_names) > 0:
    print(
        df[
            df["recipient_uei"].isin(multiple_names.index)
        ][["recipient_uei", "recipient_name"]]
        .drop_duplicates()
        .head(15)
    )
else:
    print("None found.")

print("\nExamples of supplier names with multiple UEIs:")

if len(multiple_ueis) > 0:
    print(
        df[
            df["recipient_name"].isin(multiple_ueis.index)
        ][["recipient_name", "recipient_uei"]]
        .drop_duplicates()
        .head(15)
    )
else:
    print("None found.")

# STEP 7: Inspect NAICS classification data

print("\n--- NAICS DATA INSPECTION ---")

# Count missing NAICS codes and descriptions
print(
    "Missing NAICS codes:",
    df["naics_code"].isna().sum()
)

print(
    "Missing NAICS descriptions:",
    df["naics_description"].isna().sum()
)

# Display rows with missing NAICS information
missing_naics = df[
    df["naics_code"].isna()
    | df["naics_description"].isna()
]

print("\nRows with missing NAICS information:")

print(
    missing_naics[
        [
            "recipient_name",
            "naics_code",
            "naics_description"
        ]
    ]
)

# Count unique NAICS codes
print(
    "\nUnique NAICS codes:",
    df["naics_code"].nunique()
)

# Display the most common NAICS descriptions
print("\nTop 10 NAICS descriptions:")

print(
    df["naics_description"]
    .value_counts()
    .head(10)
)

# STEP 8: Clean NAICS data types

print("\n--- NAICS DATA TYPE CLEANING ---")

# Convert NAICS codes into text
df["naics_code"] = df["naics_code"].astype("Int64").astype("string")

# Convert NAICS descriptions into text
df["naics_description"] = df["naics_description"].astype("string")

print("NAICS code data type:", df["naics_code"].dtype)
print("NAICS description data type:", df["naics_description"].dtype)

print("\nSample NAICS codes:")
print(df["naics_code"].dropna().head(10).tolist())

print("\nMissing NAICS codes after conversion:")
print(df["naics_code"].isna().sum())

# STEP 9: Standardise text columns

print("\n--- TEXT STANDARDISATION ---")

text_columns = [
    "contract_transaction_unique_key",
    "award_id_piid",
    "recipient_uei",
    "recipient_name",
    "product_or_service_code",
    "product_or_service_code_description",
    "naics_description"
]

# Apply the reusable text-standardisation function
df = standardise_text_columns(df, text_columns)

# Check missing values after standardisation
print("\nMissing values in text columns:")
print(df[text_columns].isna().sum())

# Check supplier name examples
print("\nSample supplier names after cleaning:")
print(df["recipient_name"].head(10).tolist())

# STEP 10: Validate transaction IDs

print("\n--- TRANSACTION ID VALIDATION ---")

# Run the reusable transaction ID validation function
transaction_summary = validate_transaction_ids(df)

# Extract validation results
missing_ids = transaction_summary["missing_ids"]
empty_ids = transaction_summary["empty_ids"]
duplicate_ids = transaction_summary["duplicate_ids"]
unique_ids = transaction_summary["unique_ids"]

# Display validation results
print("Missing transaction IDs:", missing_ids)
print("Empty transaction IDs:", empty_ids)
print("Duplicate transaction IDs:", duplicate_ids)
print("Unique transaction IDs:", unique_ids)

print("\nTotal dataset rows:", transaction_summary["total_rows"])

# STEP 11: Final financial validation

print("\n--- FINAL FINANCIAL VALIDATION ---")

obligation_summary = calculate_obligation_summary(df)

net_obligations = obligation_summary["net_obligations"]
positive_obligations = obligation_summary["positive_obligations"]
negative_obligations = obligation_summary["negative_obligations"]
zero_obligations = obligation_summary["zero_obligations"]

print("Net obligations:", net_obligations)
print("Positive obligations:", positive_obligations)
print("Negative obligations:", negative_obligations)
print("Zero-obligation transactions:", zero_obligations)


# Compare with original exploration results

expected_net = 15704952068.38
expected_positive = 16253906572.42
expected_negative = -548954504.04

print("\n--- BASELINE COMPARISON ---")

print(
    "Net obligations match:",
    net_obligations == expected_net
)

print(
    "Positive obligations match:",
    positive_obligations == expected_positive
)

print(
    "Negative obligations match:",
    negative_obligations == expected_negative
)

# STEP 12: Save the cleaned dataset

print("\n--- SAVING CLEANED DATASET ---")

# Create the output directory if it doesn't exist
output_folder = Path(
    "data/processed/spend_analytics"
)

output_folder.mkdir(
    parents=True,
    exist_ok=True
)

# Define the output file
output_file = output_folder / "spend_cleaned.csv"

# Save the cleaned dataset
df.to_csv(
    output_file,
    index=False
)

print("Cleaned dataset saved successfully!")
print("File location:", output_file)
print("Rows saved:", len(df))
print("Columns saved:", len(df.columns))
print("File exists:", output_file.exists())

# STEP 13: Verify the saved dataset

print("\n--- SAVED DATASET VERIFICATION ---")

# Load the saved CSV again
verified_df = pd.read_csv(output_file)

print("Dataset reloaded successfully!")
print("Rows:", len(verified_df))
print("Columns:", len(verified_df.columns))

# Verify row count
print(
    "Row count matches:",
    len(verified_df) == len(df)
)

# Verify column names
print(
    "Columns match:",
    verified_df.columns.tolist() == df.columns.tolist()
)

# Verify financial total
reloaded_total = verified_df[
    "federal_action_obligation"
].sum()

print("Reloaded net obligations:", round(reloaded_total, 2))

print(
    "Financial total matches:",
    round(reloaded_total, 2) == round(net_obligations, 2)
)

# Verify transaction IDs
print(
    "Transaction IDs remain unique:",
    verified_df["contract_transaction_unique_key"].is_unique
)