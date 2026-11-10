
from pathlib import Path
import pandas as pd

# Locate the project root folder

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# STEP 1: Locate the original dataset

raw_folder = PROJECT_ROOT / "data" / "raw" / "spend_analytics"
csv_files = list(raw_folder.glob("*.csv"))

if not csv_files:
    raise FileNotFoundError("No CSV file found in the raw data folder.")

if len(csv_files) > 1:
    raise RuntimeError("Multiple CSV files found. Please select the correct file.")

input_file = csv_files[0]

print("Original dataset:", input_file.name)

# STEP 2: Define the columns we need

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

# STEP 3: Load only the selected columns

df = pd.read_csv(
    input_file,
    usecols=selected_columns,
    low_memory=False
)

print("\nSelected data loaded successfully!")

# STEP 4: Create the output folder

output_folder = PROJECT_ROOT / "data" / "interim" / "spend_analytics"

output_folder.mkdir(parents=True, exist_ok=True)

# STEP 5: Save the smaller dataset

output_file = output_folder / "spend_selected.csv"

df.to_csv(output_file, index=False)

# STEP 6: Verify the output

print("\n--- DATASET VERIFICATION ---")

print("Number of rows:", len(df))
print("Number of columns:", len(df.columns))
print("Saved file:", output_file)
print("File exists:", output_file.exists())

print("\nSelected columns:")
print(df.columns.tolist())

print("\nSmall dataset created successfully!")
