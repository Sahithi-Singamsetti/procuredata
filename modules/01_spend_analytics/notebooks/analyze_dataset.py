from pathlib import Path
import pandas as pd

# Locate the project root folder
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Locate the raw dataset
data_folder = PROJECT_ROOT / "data" / "raw" / "spend_analytics"

csv_files = list(data_folder.glob("*.csv"))

if not csv_files:
    print("No CSV file found!")
    raise SystemExit

file_path = csv_files[0]

print("Dataset found:", file_path.name)

selected_columns = [
    "contract_transaction_unique_key",
    "award_id_piid",
    "action_date",
    "federal_action_obligation",
    "recipient_name",
    "recipient_uei",
    "product_or_service_code",
    "product_or_service_code_description",
    "naics_code",
    "naics_description"
]

# Load only the selected columns
df = pd.read_csv(
    file_path,
    usecols=selected_columns,
    low_memory=False
)

print("\nDataset loaded successfully!")
print("Number of rows:", len(df))
print("Number of columns:", len(df.columns))

print("\n--- DATA TYPES ---")
print(df.dtypes)

print("\n--- MISSING VALUES ---")
print(df.isnull().sum())

print("\n--- DUPLICATE TRANSACTION IDs ---")
print(df["contract_transaction_unique_key"].duplicated().sum())

print("\n--- DATE RANGE ---")
dates = pd.to_datetime(df["action_date"], errors="coerce")
print("Earliest date:", dates.min())
print("Latest date:", dates.max())

print("\n--- OBLIGATION ANALYSIS ---")
amounts = pd.to_numeric(
    df["federal_action_obligation"],
    errors="coerce"
)

print("Missing amounts:", amounts.isna().sum())
print("Negative amounts:", (amounts < 0).sum())
print("Zero amounts:", (amounts == 0).sum())

print("\n--- FINANCIAL ANALYSIS ---")

print("Total net obligations:", amounts.sum())

print("Total positive obligations:",
      amounts[amounts > 0].sum())

print("Total negative obligations:",
      amounts[amounts < 0].sum())

print("Total zero obligations:",
      amounts[amounts == 0].sum())

print("\n--- SAMPLE NEGATIVE TRANSACTIONS ---")

print(
    df.loc[
        amounts < 0,
        ["award_id_piid", "recipient_name",
         "federal_action_obligation", "action_date"]
    ].head(5)
)

print("\n--- SAMPLE ZERO TRANSACTIONS ---")

print(
    df.loc[
        amounts == 0,
        ["award_id_piid", "recipient_name",
         "federal_action_obligation", "action_date"]
    ].head(5)
)

# Convert action_date into a proper date format
df["action_date"] = pd.to_datetime(
    df["action_date"],
    errors="coerce"
)

# Number of unique suppliers
supplier_count = df["recipient_uei"].nunique()

# Number of unique awards
award_count = df["award_id_piid"].nunique()

print("\n--- BUSINESS OVERVIEW ---")
print("Unique suppliers:", supplier_count)
print("Unique awards:", award_count)

# Monthly obligations
df["month"] = df["action_date"].dt.to_period("M")

monthly_spend = (
    df.groupby("month")["federal_action_obligation"]
    .sum()
    .sort_values(ascending=False)
)

print("\n--- MONTHLY NET OBLIGATIONS ---")
print(monthly_spend)

# Top 10 suppliers
supplier_spend = (
    df.groupby("recipient_name")["federal_action_obligation"]
    .sum()
    .sort_values(ascending=False)
)

print("\n--- TOP 10 SUPPLIERS ---")
print(supplier_spend.head(10))
